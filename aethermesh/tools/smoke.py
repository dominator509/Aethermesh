"""Smoke test — validates install is functional.

Body lands in EP-002+. Currently a no-op pass for CI baseline.
"""

import sys


def main() -> None:
    """Run smoke test."""
    print("smoke test: ok")
    sys.exit(0)


if __name__ == "__main__":
    main()
