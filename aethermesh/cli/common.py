"""CLI shared constants and output helpers — no circular imports."""

import os
import sys

# ---------------------------------------------------------------------------
# Exit code constants per SPEC-004 § Exit Codes
# ---------------------------------------------------------------------------

EXIT_SUCCESS = 0
EXIT_USAGE = 1
EXIT_VALIDATION = 2
EXIT_STOP = 3


# ---------------------------------------------------------------------------
# Output helpers
# ---------------------------------------------------------------------------


def use_color() -> bool:
    """Honor NO_COLOR=1 per SPEC-004 § Accessibility."""
    return os.environ.get("NO_COLOR", "").strip() not in ("1", "true", "yes")


def print_line(line: str, *, color: str | None = None) -> None:
    """Print a line; optionally with ANSI color if NO_COLOR is not set."""
    if color and use_color():
        codes = {"green": "\033[32m", "red": "\033[31m", "yellow": "\033[33m"}
        reset = "\033[0m"
        sys.stdout.write(f"{codes.get(color, '')}{line}{reset}\n")
    else:
        sys.stdout.write(f"{line}\n")


def print_error(line: str) -> None:
    """Print a SPEC-004 diagnostic line to stderr."""
    sys.stderr.write(f"aethermesh: {line}\n")


def print_json(obj: dict[str, object]) -> None:
    """Print a JSON Line."""
    import json

    sys.stdout.write(json.dumps(obj, sort_keys=True, default=str) + "\n")


def format_output(items: list[dict[str, object]], fmt: str) -> None:
    """Print *items* in the requested format."""
    if fmt == "json":
        for item in items:
            print_json(item)
    else:
        for item in items:
            parts = [f"{k}={v}" for k, v in item.items()]
            print_line("  ".join(parts))
