"""CLI `aethermesh audit` — audit log query and export.

EP-005 M2, M3. Uses aethermesh.tools.audit_db for real persistence.
"""

import argparse

from aethermesh.cli.common import (
    EXIT_SUCCESS,
    EXIT_VALIDATION,
    format_output,
    print_error,
    print_line,
)


def run(args: argparse.Namespace) -> int:
    cmd = getattr(args, "audit_command", None)
    if cmd == "ls":
        return _audit_ls(args)
    if cmd == "export":
        return _audit_export(args)
    print_error("audit: no subcommand specified; see --help")
    return EXIT_VALIDATION


def _audit_ls(args: argparse.Namespace) -> int:
    path = args.path
    session_hex = args.session
    fmt = getattr(args, "format", "text")

    from aethermesh.tools.audit_db import all_for_session

    try:
        if session_hex:
            session_hash = bytes.fromhex(session_hex)
            rows = all_for_session(path, session_hash)
        else:
            print_error("audit ls: --session is required for listing")
            return EXIT_VALIDATION
    except FileNotFoundError:
        print_error(f"audit ls: database not found at {path}")
        return EXIT_VALIDATION

    items = [
        {
            "receipt_id": row["receipt_id"].hex()
            if isinstance(row["receipt_id"], bytes)
            else str(row["receipt_id"]),
            "message_index": row["message_index"],
            "caller_did": row["caller_did"],
            "policy_decision": row["policy_decision"],
        }
        for row in rows
    ]
    format_output(items, fmt)
    if not items and fmt != "json":
        print_line("  (no receipts found)")
    return EXIT_SUCCESS


def _audit_export(args: argparse.Namespace) -> int:
    since = args.since
    until = args.until
    out = args.out

    print_line(f"audit export: since={since} until={until} out={out}")
    print_line("  [stub] audit export writes all matching receipts")
    return EXIT_SUCCESS
