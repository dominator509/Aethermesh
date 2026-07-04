"""CLI `aethermesh node` — node lifecycle operations.

EP-005 M2. Honest smoke paths — does NOT start real mix-net nodes.
"""

import argparse

from aethermesh.cli.common import (
    EXIT_STOP,
    EXIT_SUCCESS,
    EXIT_VALIDATION,
    print_error,
    print_line,
)


def run(args: argparse.Namespace) -> int:
    cmd = getattr(args, "node_command", None)
    if cmd == "start":
        return _node_start(args)
    if cmd == "health":
        return _node_health(args)
    if cmd == "diagnose":
        return _node_diagnose(args)
    if cmd == "refresh-directory":
        return _node_refresh(args)
    print_error("node: no subcommand specified; see --help")
    return EXIT_VALIDATION


def _node_start(args: argparse.Namespace) -> int:
    role = args.role
    valid_roles = (
        "mix-layer-1",
        "mix-layer-2",
        "mix-layer-3",
        "gateway-entry",
        "gateway-exit",
        "dht-node",
    )
    if role not in valid_roles:
        print_error(f"node start: invalid role '{role}'")
        return EXIT_VALIDATION

    import os

    pq_backend = os.environ.get("AEP_PQ_BACKEND", "placeholder")
    if pq_backend == "placeholder":
        print_error("node start: AEP_PQ_BACKEND=placeholder refused in production mode")
        return EXIT_STOP

    print_line(f"node start: role={role} [stub — real node body in EP-006+]")
    return EXIT_SUCCESS


def _node_health(args: argparse.Namespace) -> int:
    endpoint = getattr(args, "endpoint", "http://127.0.0.1:9100")
    print_line(f"node health: endpoint={endpoint} [stub]")
    print_line("  status: ok", color="green")
    return EXIT_SUCCESS


def _node_diagnose(args: argparse.Namespace) -> int:
    out = getattr(args, "out", "diagnose-report.json")
    import json

    report = {
        "timestamp": "2026-07-03T00:00:00Z",
        "status": "ok",
        "layers": {"L1": "up", "L2": "up", "L3": "up", "L4": "up", "L5": "up"},
        "note": "stub — real diagnostics in EP-006+",
    }
    with open(out, "w") as f:
        json.dump(report, f, indent=2)
    print_line(f"node diagnose: report written to {out}")
    return EXIT_SUCCESS


def _node_refresh(args: argparse.Namespace) -> int:
    print_line("node refresh-directory: [stub] directory cache refreshed")
    return EXIT_SUCCESS
