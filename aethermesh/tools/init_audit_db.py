"""Initialize audit database. CLI: python -m aethermesh.tools.init_audit_db --path <path>.

EP-003 M1.
"""

import argparse
import sys

from aethermesh.tools.audit_db import SCHEMA_VERSION, init


def main() -> None:
    parser = argparse.ArgumentParser(description="Initialize AetherMesh audit database")
    parser.add_argument("--path", required=True, help="Path to SQLite database file")
    args = parser.parse_args()

    init(args.path)
    print(f"audit db initialized at {args.path} (schema v{SCHEMA_VERSION})")
    sys.exit(0)


if __name__ == "__main__":
    main()
