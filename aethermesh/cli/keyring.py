"""CLI `aethermesh keyring` — keyring server operations.

EP-005 M2. Honest stub — does NOT expose real key material.
"""

import argparse
import os

from aethermesh.cli.common import (
    EXIT_STOP,
    EXIT_SUCCESS,
    EXIT_VALIDATION,
    print_error,
    print_line,
)


def run(args: argparse.Namespace) -> int:
    cmd = getattr(args, "keyring_command", None)
    if cmd == "serve":
        return _keyring_serve(args)
    print_error("keyring: no subcommand specified; see --help")
    return EXIT_VALIDATION


def _keyring_serve(args: argparse.Namespace) -> int:
    socket_path = args.socket

    # SPEC-004: refuse outside TEE in production
    pq_backend = os.environ.get("AEP_PQ_BACKEND", "placeholder")
    if pq_backend != "liboqs":
        print_error("keyring serve: AEP_PQ_BACKEND must be 'liboqs' for production keyring")
        return EXIT_STOP

    print_line(f"keyring serve: socket={socket_path} [stub — real keyring in EP-006+]")
    return EXIT_SUCCESS
