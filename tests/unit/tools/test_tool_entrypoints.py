"""Unit coverage for simple tool module entrypoints."""

from __future__ import annotations

import sys

import pytest

from aethermesh.tools import init_audit_db, smoke


def test_smoke_main_exits_success(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as raised:
        smoke.main()
    assert raised.value.code == 0
    assert "smoke test: ok" in capsys.readouterr().out


def test_init_audit_db_main(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    called: list[str] = []
    monkeypatch.setattr(sys, "argv", ["init_audit_db", "--path", "audit.db"])
    monkeypatch.setattr(init_audit_db, "init", lambda path: called.append(path))

    with pytest.raises(SystemExit) as raised:
        init_audit_db.main()

    assert raised.value.code == 0
    assert called == ["audit.db"]
    assert "audit db initialized at audit.db" in capsys.readouterr().out
