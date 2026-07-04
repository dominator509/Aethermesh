"""E2E tests: NO_COLOR=1 suppresses ANSI escape sequences.

EP-005 M3. SPEC-004 § Accessibility.
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


class TestNoColor:
    def test_no_color_flag(self) -> None:
        """--no-color flag suppresses ANSI."""
        result = _run(["demo", "--layer", "1"], NO_COLOR="1")
        assert result.returncode == 0
        assert "\033" not in result.stdout

    def test_no_color_env(self) -> None:
        """NO_COLOR=1 env var suppresses ANSI."""
        result = _run(["tools", "smoke"], NO_COLOR="1")
        assert result.returncode == 0
        assert "\033" not in result.stdout

    def test_no_color_true(self) -> None:
        """NO_COLOR=true also suppresses ANSI."""
        result = _run(["demo", "--layer", "3"], NO_COLOR="true")
        assert result.returncode == 0
        assert "\033" not in result.stdout

    def test_color_by_default(self) -> None:
        """Without NO_COLOR, green ANSI codes appear."""
        result = _run(["demo", "--layer", "1"], NO_COLOR="0")
        assert result.returncode == 0
        assert "\033" in result.stdout

    def test_demo_plain_text(self) -> None:
        """NO_COLOR=1 aethermesh demo --layer 1 succeeds plain-text."""
        result = _run(["demo", "--layer", "1"], NO_COLOR="1")
        assert result.returncode == 0
        assert "=== AetherMesh L1 Demo" in result.stdout
        assert "=== DONE ===" in result.stdout
        assert "\033" not in result.stdout
