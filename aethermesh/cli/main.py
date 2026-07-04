"""CLI main — argparse skeleton, exit code handling.

EP-005 M1, M3, M4. SPEC-004.
"""

import argparse
import os
import sys
from typing import NoReturn

from aethermesh.cli import audit, demo, keyring, node, tools
from aethermesh.cli.common import (
    EXIT_STOP,
    EXIT_SUCCESS,
    EXIT_USAGE,
    EXIT_VALIDATION,
    print_error,
)


def _die(msg: str, code: int = EXIT_USAGE) -> NoReturn:
    """Print error to stderr and exit."""
    print_error(msg)
    sys.exit(code)


# ---------------------------------------------------------------------------
# Top-level parser
# ---------------------------------------------------------------------------


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="aethermesh",
        description="AetherMesh / AEP - Agent Exchange Protocol CLI",
    )
    parser.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        help="Output format (default: text)",
    )
    parser.add_argument(
        "--no-color",
        action="store_true",
        default=False,
        help="Disable ANSI color output",
    )
    sub = parser.add_subparsers(dest="command", title="subcommands")

    # demo
    demo_p = sub.add_parser("demo", help="Run layer demos")
    demo_p.add_argument(
        "--layer", type=int, choices=(1, 2, 3, 4, 5), required=True, help="Layer to demo"
    )
    demo_p.add_argument(
        "--lane", choices=("fast", "slow", "slow+"), default="fast", help="Cover lane"
    )

    # node
    node_p = sub.add_parser("node", help="Mix-node / gateway / DHT operations")
    node_sub = node_p.add_subparsers(dest="node_command")
    node_start = node_sub.add_parser("start", help="Start a node")
    node_start.add_argument("--role", required=True, help="Node role")
    node_health = node_sub.add_parser("health", help="Node health check")
    node_health.add_argument("--endpoint", default="http://127.0.0.1:9100", help="Health endpoint")
    node_diag = node_sub.add_parser("diagnose", help="Run diagnostics")
    node_diag.add_argument("--out", default="diagnose-report.json", help="Output path")
    node_sub.add_parser("refresh-directory", help="Refresh directory cache")

    # keyring
    keyring_p = sub.add_parser("keyring", help="Keyring operations")
    keyring_sub = keyring_p.add_subparsers(dest="keyring_command")
    keyring_serve = keyring_sub.add_parser("serve", help="Start keyring server")
    keyring_serve.add_argument("--socket", required=True, help="Unix socket path")

    # audit
    audit_p = sub.add_parser("audit", help="Audit log operations")
    audit_sub = audit_p.add_subparsers(dest="audit_command")
    audit_ls = audit_sub.add_parser("ls", help="List audit receipts")
    audit_ls.add_argument("--session", default=None, help="Session root hash (hex)")
    audit_ls.add_argument("--path", default="./audit.db", help="Database path")
    audit_export = audit_sub.add_parser("export", help="Export audit receipts")
    audit_export.add_argument("--since", required=True, help="ISO-8601 start timestamp")
    audit_export.add_argument("--until", required=True, help="ISO-8601 end timestamp")
    audit_export.add_argument("--out", required=True, help="Output file path")

    # tools
    tools_p = sub.add_parser("tools", help="Utilities")
    tools_sub = tools_p.add_subparsers(dest="tools_command")
    tools_sub.add_parser("smoke", help="Smoke test")
    tools_init = tools_sub.add_parser("init-audit-db", help="Initialize audit database")
    tools_init.add_argument("--path", required=True, help="Database path")
    tools_bootstrap = tools_sub.add_parser("bootstrap-directory", help="Bootstrap directory")
    tools_bootstrap.add_argument("--out", required=True, help="Output file path")

    return parser


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------


def main(argv: list[str] | None = None) -> int:
    """CLI entry point. Returns exit code."""
    parser = _build_parser()

    try:
        args = parser.parse_args(argv)
    except SystemExit as e:
        return EXIT_SUCCESS if e.code == 0 else EXIT_USAGE

    if getattr(args, "no_color", False):
        os.environ["NO_COLOR"] = "1"

    if not args.command:
        parser.print_help()
        return EXIT_USAGE

    try:
        return _dispatch(args)
    except PermissionError as e:
        _die(f"{args.command}: {e}", EXIT_STOP)
    except ValueError as e:
        _die(f"{args.command}: {e}", EXIT_VALIDATION)
    except Exception as e:
        if os.environ.get("AEP_LOG_LEVEL") == "debug":
            raise
        _die(f"{args.command}: {e}", EXIT_VALIDATION)
    return EXIT_SUCCESS


def _dispatch(args: argparse.Namespace) -> int:
    if args.command == "demo":
        return demo.run(args)
    if args.command == "node":
        return node.run(args)
    if args.command == "keyring":
        return keyring.run(args)
    if args.command == "audit":
        return audit.run(args)
    if args.command == "tools":
        return tools.run(args)
    return EXIT_USAGE


if __name__ == "__main__":
    sys.exit(main())
