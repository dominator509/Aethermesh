"""E2E tests: exit codes 0/1/2/3 per SPEC-004 § Exit Codes.

EP-005 M4.
"""

# mypy: allow-untyped-defs

import os
import subprocess
import sys


def _run(args: list[str], **env_extra: str) -> "subprocess.CompletedProcess[str]":
    env = os.environ.copy()
    env.update(env_extra)
    return subprocess.run(
        [sys.executable, "-m", "aethermesh.cli", *args],
        capture_output=True,
        text=True,
        env=env,
    )


class TestExitCodes:
    def test_exit_0_success(self) -> None:
        """Exit 0 on successful command."""
        result = _run(["demo", "--layer", "1"])
        assert result.returncode == 0

    def test_exit_0_node_health(self) -> None:
        result = _run(["node", "health"])
        assert result.returncode == 0

    def test_exit_0_tools_smoke(self) -> None:
        result = _run(["tools", "smoke"])
        assert result.returncode == 0

    def test_exit_1_missing_subcommand(self) -> None:
        """Exit 1 on missing subcommand."""
        result = _run([])
        assert result.returncode == 1

    def test_exit_1_invalid_flag(self) -> None:
        """Exit 1 on invalid usage."""
        result = _run(["--nonexistent"])
        assert result.returncode == 1
        assert "usage:" in result.stderr

    def test_exit_2_validation(self) -> None:
        """Exit 2 on validation failure."""
        result = _run(["node", "start", "--role", "invalid-role"])
        assert result.returncode == 2
        assert result.stderr.startswith("aethermesh: node start:")

    def test_exit_3_prod_placeholder(self) -> None:
        """Exit 3 when AEP_PQ_BACKEND=placeholder in production path."""
        result = _run(
            ["node", "start", "--role", "mix-layer-1"],
            AEP_PQ_BACKEND="placeholder",
        )
        assert result.returncode == 3
        assert result.stderr.startswith("aethermesh: node start:")

    def test_exit_3_keyring_no_liboqs(self) -> None:
        """Exit 3 when keyring serve without liboqs."""
        result = _run(
            ["keyring", "serve", "--socket", "/tmp/test.sock"],
            AEP_PQ_BACKEND="placeholder",
        )
        assert result.returncode == 3
        assert result.stderr.startswith("aethermesh: keyring serve:")
