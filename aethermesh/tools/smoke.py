"""Smoke test — validates install is functional.

EP-010: --prod flag rejects placeholder PQ backend (SPEC-008 Gate 2).
"""

import os
import sys


def _liboqs_binding_available() -> bool:
    try:
        import oqs  # type: ignore[import-not-found]
    except ImportError:
        return False
    return hasattr(oqs, "KeyEncapsulation") and hasattr(oqs, "Signature")


def main(argv: list[str] | None = None) -> None:
    """Run smoke test. Accepts optional argv to avoid argparse/pytest conflicts."""
    import argparse

    parser = argparse.ArgumentParser(description="AetherMesh smoke test")
    parser.add_argument(
        "--prod",
        action="store_true",
        default=False,
        help="Production mode: rejects AEP_PQ_BACKEND=placeholder",
    )
    parser.add_argument("--target", default="self", help="Smoke target")
    parser.add_argument("--lane", default="fast", help="Cover lane")
    parser.add_argument("--timeout", type=int, default=5, help="Timeout in seconds")
    args = parser.parse_args(argv if argv is not None else [])

    if args.prod:
        pq_backend = os.environ.get("AEP_PQ_BACKEND", "placeholder")
        if pq_backend == "placeholder":
            print(
                "smoke test: FAIL — AEP_PQ_BACKEND=placeholder refused in --prod mode",
                file=sys.stderr,
            )
            sys.exit(1)
        if pq_backend == "liboqs" and not _liboqs_binding_available():
            print(
                "smoke test: FAIL — liboqs Python binding unavailable in --prod mode",
                file=sys.stderr,
            )
            sys.exit(1)

    print("smoke test: ok")
    sys.exit(0)


if __name__ == "__main__":
    main(sys.argv[1:])
