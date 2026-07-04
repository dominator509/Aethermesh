"""E2E tests: every subcommand --help and happy path.

EP-005 M5.
"""

# mypy: allow-untyped-defs

import contextlib
import os
import subprocess
import sys
import tempfile


def _run(args: list[str]) -> "subprocess.CompletedProcess[str]":
    return subprocess.run(
        [sys.executable, "-m", "aethermesh.cli", *args],
        capture_output=True,
        text=True,
    )


class TestHelpOutput:
    def test_top_level_help(self) -> None:
        result = _run(["--help"])
        assert result.returncode == 0
        assert "demo" in result.stdout
        assert "node" in result.stdout
        assert "keyring" in result.stdout
        assert "audit" in result.stdout
        assert "tools" in result.stdout

    def test_demo_help(self) -> None:
        result = _run(["demo", "--help"])
        assert result.returncode == 0
        assert "--layer" in result.stdout

    def test_node_help(self) -> None:
        result = _run(["node", "--help"])
        assert result.returncode == 0
        assert "start" in result.stdout
        assert "health" in result.stdout

    def test_keyring_help(self) -> None:
        result = _run(["keyring", "--help"])
        assert result.returncode == 0
        assert "serve" in result.stdout

    def test_audit_help(self) -> None:
        result = _run(["audit", "--help"])
        assert result.returncode == 0
        assert "ls" in result.stdout

    def test_tools_help(self) -> None:
        result = _run(["tools", "--help"])
        assert result.returncode == 0
        assert "smoke" in result.stdout


class TestDemoSubcommand:
    def test_demo_l1(self) -> None:
        result = _run(["demo", "--layer", "1"])
        assert result.returncode == 0
        assert "=== DONE ===" in result.stdout

    def test_demo_l3(self) -> None:
        result = _run(["demo", "--layer", "3"])
        assert result.returncode == 0
        assert "=== DONE ===" in result.stdout

    def test_demo_l5(self) -> None:
        result = _run(["demo", "--layer", "5"])
        assert result.returncode == 0
        assert "=== DONE ===" in result.stdout


class TestNodeSubcommand:
    def test_node_health(self) -> None:
        result = _run(["node", "health"])
        assert result.returncode == 0

    def test_node_refresh_directory(self) -> None:
        result = _run(["node", "refresh-directory"])
        assert result.returncode == 0


class TestKeyringSubcommand:
    def test_keyring_serve_with_liboqs(self) -> None:
        """keyring serve exits 0 when AEP_PQ_BACKEND=liboqs."""
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "aethermesh.cli",
                "keyring",
                "serve",
                "--socket",
                "/tmp/ks.sock",
            ],
            capture_output=True,
            text=True,
            env={**os.environ, "AEP_PQ_BACKEND": "liboqs"},
        )
        assert result.returncode == 0


class TestAuditSubcommand:
    def test_audit_ls(self) -> None:
        """audit ls exits 0 (with test DB)."""
        fd, dbpath = tempfile.mkstemp(suffix=".db", prefix="aep_audit_")
        os.close(fd)
        try:
            # Init DB first
            subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "aethermesh.cli",
                    "tools",
                    "init-audit-db",
                    "--path",
                    dbpath,
                ],
                capture_output=True,
                text=True,
            )
            result = _run(["audit", "ls", "--path", dbpath, "--session", "00" * 32])
            assert result.returncode == 0
            assert "(no receipts found)" in result.stdout

            json_result = _run(
                [
                    "--format",
                    "json",
                    "audit",
                    "ls",
                    "--path",
                    dbpath,
                    "--session",
                    "00" * 32,
                ]
            )
            assert json_result.returncode == 0
            assert json_result.stdout == ""
        finally:
            with contextlib.suppress(OSError):
                os.unlink(dbpath)


class TestToolsSubcommand:
    def test_tools_smoke(self) -> None:
        result = _run(["tools", "smoke"])
        assert result.returncode == 0
        assert "smoke test: ok" in result.stdout

    def test_tools_init_audit_db(self) -> None:
        fd, dbpath = tempfile.mkstemp(suffix=".db")
        os.close(fd)
        try:
            result = _run(["tools", "init-audit-db", "--path", dbpath])
            assert result.returncode == 0
            assert "audit db initialized" in result.stdout
        finally:
            with contextlib.suppress(OSError):
                os.unlink(dbpath)

    def test_tools_bootstrap_directory(self) -> None:
        fd, outpath = tempfile.mkstemp(suffix=".json")
        os.close(fd)
        try:
            result = _run(["tools", "bootstrap-directory", "--out", outpath])
            assert result.returncode == 0
            assert "directory bootstrapped" in result.stdout
        finally:
            with contextlib.suppress(OSError):
                os.unlink(outpath)
