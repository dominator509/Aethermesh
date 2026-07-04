"""CLI unit coverage for EP-007 testing hardening."""

from __future__ import annotations

import argparse
import builtins
import importlib
import os
from unittest.mock import mock_open

import pytest

from aethermesh.cli import audit, demo, keyring, node, tools
from aethermesh.cli.common import (
    EXIT_STOP,
    EXIT_SUCCESS,
    EXIT_USAGE,
    EXIT_VALIDATION,
    format_output,
    print_error,
    print_json,
    print_line,
    use_color,
)

cli_main = importlib.import_module("aethermesh.cli.main")


def _ns(**values: object) -> argparse.Namespace:
    return argparse.Namespace(**values)


class TestCommonOutput:
    def test_use_color_honors_no_color(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv("NO_COLOR", raising=False)
        assert use_color() is True

        monkeypatch.setenv("NO_COLOR", "1")
        assert use_color() is False

    def test_print_line_color_and_plain(self, capsys: pytest.CaptureFixture[str]) -> None:
        print_line("ok", color="green")
        print_line("plain")
        out = capsys.readouterr().out
        assert "ok" in out
        assert "plain" in out

    def test_print_error(self, capsys: pytest.CaptureFixture[str]) -> None:
        print_error("bad")
        assert capsys.readouterr().err == "aethermesh: bad\n"

    def test_json_and_text_formatting(self, capsys: pytest.CaptureFixture[str]) -> None:
        print_json({"b": 2, "a": 1})
        format_output([{"x": 1, "y": "z"}], "text")
        format_output([{"x": 2}], "json")
        out = capsys.readouterr().out
        assert '{"a": 1, "b": 2}' in out
        assert "x=1  y=z" in out
        assert '{"x": 2}' in out


class TestMain:
    def test_no_command_returns_usage(self) -> None:
        assert cli_main.main([]) == EXIT_USAGE

    def test_help_returns_success(self) -> None:
        assert cli_main.main(["--help"]) == EXIT_SUCCESS

    def test_no_color_sets_env(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv("NO_COLOR", raising=False)
        assert cli_main.main(["--no-color"]) == EXIT_USAGE
        assert os.environ["NO_COLOR"] == "1"

    def test_dispatch_unknown(self) -> None:
        assert cli_main._dispatch(_ns(command="unknown")) == EXIT_USAGE

    @pytest.mark.parametrize(
        ("exc", "code"),
        [
            (PermissionError("stop"), EXIT_STOP),
            (ValueError("bad"), EXIT_VALIDATION),
            (RuntimeError("boom"), EXIT_VALIDATION),
        ],
    )
    def test_main_translates_dispatch_exceptions(
        self,
        monkeypatch: pytest.MonkeyPatch,
        exc: Exception,
        code: int,
    ) -> None:
        def _raise(_args: argparse.Namespace) -> int:
            raise exc

        monkeypatch.setattr(cli_main, "_dispatch", _raise)
        with pytest.raises(SystemExit) as raised:
            cli_main.main(["demo", "--layer", "1"])
        assert raised.value.code == code

    def test_debug_reraises_unexpected(self, monkeypatch: pytest.MonkeyPatch) -> None:
        def _raise(_args: argparse.Namespace) -> int:
            raise RuntimeError("boom")

        monkeypatch.setattr(cli_main, "_dispatch", _raise)
        monkeypatch.setenv("AEP_LOG_LEVEL", "debug")
        with pytest.raises(RuntimeError):
            cli_main.main(["demo", "--layer", "1"])


class TestDemo:
    @pytest.mark.parametrize("layer", [1, 2, 3, 4, 5])
    def test_demo_layers(self, layer: int, capsys: pytest.CaptureFixture[str]) -> None:
        assert demo.run(_ns(layer=layer, lane="fast")) == EXIT_SUCCESS
        assert "=== DONE ===" in capsys.readouterr().out

    def test_unknown_layer_falls_through_success(self) -> None:
        assert demo.run(_ns(layer=99, lane="fast")) == EXIT_SUCCESS


class TestAudit:
    def test_audit_no_subcommand(self) -> None:
        assert audit.run(_ns(audit_command=None)) == EXIT_VALIDATION

    def test_audit_ls_requires_session(self) -> None:
        assert audit.run(_ns(audit_command="ls", path="unused.db", session=None)) == EXIT_VALIDATION

    def test_audit_ls_database_missing(self, monkeypatch: pytest.MonkeyPatch) -> None:
        import aethermesh.tools.audit_db as audit_db

        def _missing(_path: str, _session_hash: bytes) -> list[dict[str, object]]:
            raise FileNotFoundError

        monkeypatch.setattr(audit_db, "all_for_session", _missing)
        args = _ns(audit_command="ls", path="missing.db", session="00" * 32, format="text")
        assert audit.run(args) == EXIT_VALIDATION

    @pytest.mark.parametrize("fmt", ["text", "json"])
    def test_audit_ls_formats_rows(
        self,
        monkeypatch: pytest.MonkeyPatch,
        capsys: pytest.CaptureFixture[str],
        fmt: str,
    ) -> None:
        import aethermesh.tools.audit_db as audit_db

        def _rows(_path: str, _session_hash: bytes) -> list[dict[str, object]]:
            return [
                {
                    "receipt_id": b"\x01" * 32,
                    "message_index": 7,
                    "caller_did": "did:web:example.org",
                    "policy_decision": "ALLOW",
                }
            ]

        monkeypatch.setattr(audit_db, "all_for_session", _rows)
        args = _ns(audit_command="ls", path="audit.db", session="00" * 32, format=fmt)
        assert audit.run(args) == EXIT_SUCCESS
        assert "ALLOW" in capsys.readouterr().out

    def test_audit_ls_empty_text(
        self,
        monkeypatch: pytest.MonkeyPatch,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        import aethermesh.tools.audit_db as audit_db

        monkeypatch.setattr(audit_db, "all_for_session", lambda _p, _s: [])
        args = _ns(audit_command="ls", path="audit.db", session="00" * 32, format="text")
        assert audit.run(args) == EXIT_SUCCESS
        assert "no receipts" in capsys.readouterr().out

    def test_audit_export(self, capsys: pytest.CaptureFixture[str]) -> None:
        args = _ns(audit_command="export", since="2026-01-01", until="2026-01-02", out="out.json")
        assert audit.run(args) == EXIT_SUCCESS
        assert "audit export" in capsys.readouterr().out


class TestNode:
    def test_node_no_subcommand(self) -> None:
        assert node.run(_ns(node_command=None)) == EXIT_VALIDATION

    def test_node_start_invalid_role(self) -> None:
        assert node.run(_ns(node_command="start", role="bad")) == EXIT_VALIDATION

    def test_node_start_refuses_placeholder(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("AEP_PQ_BACKEND", "placeholder")
        assert node.run(_ns(node_command="start", role="mix-layer-1")) == EXIT_STOP

    def test_node_start_liboqs(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("AEP_PQ_BACKEND", "liboqs")
        assert node.run(_ns(node_command="start", role="gateway-entry")) == EXIT_SUCCESS

    def test_node_health_and_refresh(self) -> None:
        assert (
            node.run(_ns(node_command="health", endpoint="http://127.0.0.1:9100")) == EXIT_SUCCESS
        )
        assert node.run(_ns(node_command="refresh-directory")) == EXIT_SUCCESS

    def test_node_diagnose_uses_supplied_path(self, monkeypatch: pytest.MonkeyPatch) -> None:
        handle = mock_open()
        monkeypatch.setattr(builtins, "open", handle)
        assert node.run(_ns(node_command="diagnose", out="diagnose.json")) == EXIT_SUCCESS
        handle.assert_called_once_with("diagnose.json", "w")


class TestKeyring:
    def test_keyring_no_subcommand(self) -> None:
        assert keyring.run(_ns(keyring_command=None)) == EXIT_VALIDATION

    def test_keyring_serve_requires_liboqs(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv("AEP_PQ_BACKEND", raising=False)
        assert keyring.run(_ns(keyring_command="serve", socket="keyring.sock")) == EXIT_STOP

    def test_keyring_serve_liboqs(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("AEP_PQ_BACKEND", "liboqs")
        assert keyring.run(_ns(keyring_command="serve", socket="keyring.sock")) == EXIT_SUCCESS


class TestTools:
    def test_tools_no_subcommand(self) -> None:
        assert tools.run(_ns(tools_command=None)) == EXIT_VALIDATION

    def test_tools_smoke(self, capsys: pytest.CaptureFixture[str]) -> None:
        assert tools.run(_ns(tools_command="smoke")) == EXIT_SUCCESS
        assert "smoke test: ok" in capsys.readouterr().out

    def test_init_audit_db_uses_tool(self, monkeypatch: pytest.MonkeyPatch) -> None:
        import aethermesh.tools.audit_db as audit_db

        called: list[str] = []
        monkeypatch.setattr(audit_db, "init", lambda path: called.append(path))
        assert tools.run(_ns(tools_command="init-audit-db", path="audit.db")) == EXIT_SUCCESS
        assert called == ["audit.db"]

    def test_bootstrap_directory_writes_json(self, monkeypatch: pytest.MonkeyPatch) -> None:
        handle = mock_open()
        monkeypatch.setattr(builtins, "open", handle)
        assert (
            tools.run(_ns(tools_command="bootstrap-directory", out="directory.json"))
            == EXIT_SUCCESS
        )
        handle.assert_called_once_with("directory.json", "w")
