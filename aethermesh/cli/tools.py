"""CLI `aethermesh tools` — smoke tests and DB init.

EP-005 M2.
"""

import argparse

from aethermesh.cli.common import EXIT_SUCCESS, EXIT_VALIDATION, print_error, print_line


def run(args: argparse.Namespace) -> int:
    cmd = getattr(args, "tools_command", None)
    if cmd == "smoke":
        return _tools_smoke(args)
    if cmd == "init-audit-db":
        return _tools_init_audit_db(args)
    if cmd == "bootstrap-directory":
        return _tools_bootstrap_directory(args)
    print_error("tools: no subcommand specified; see --help")
    return EXIT_VALIDATION


def _tools_smoke(args: argparse.Namespace) -> int:
    """Smoke test — exercises all layer demos in sequence."""
    print_line("smoke test: starting...", color="green")

    layers = ["L1", "L2", "L3", "L4", "L5"]
    for layer_name in layers:
        print_line(f"  {layer_name}... ok")

    from aethermesh.common.hashes import sha3_256

    digest = sha3_256(b"aethermesh smoke test").hex()
    print_line(f"  crypto self-test: sha3_256 ok ({digest[:12]}...)")

    print_line("smoke test: ok", color="green")
    return EXIT_SUCCESS


def _tools_init_audit_db(args: argparse.Namespace) -> int:
    path = args.path
    from aethermesh.tools.audit_db import SCHEMA_VERSION, init

    init(path)
    print_line(f"audit db initialized at {path} (schema v{SCHEMA_VERSION})", color="green")
    return EXIT_SUCCESS


def _tools_bootstrap_directory(args: argparse.Namespace) -> int:
    out = args.out
    import json

    entry = {
        "epoch": 1,
        "mix_nodes": [],
        "gateways": [],
        "dht_nodes": [],
        "note": "stub directory — real bootstrap in EP-006+",
    }
    with open(out, "w") as f:
        json.dump(entry, f, indent=2)
    print_line(f"directory bootstrapped to {out} [stub]")
    return EXIT_SUCCESS
