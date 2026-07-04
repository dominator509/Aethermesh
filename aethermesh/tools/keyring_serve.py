"""Keyring service — Unix socket IPC per SPEC-005 § Keyring IPC.

EP-006 M5. Binds to $AEP_KEYRING_SOCKET.
Reads length-prefixed JSON development-stand-in requests until a CBOR dependency
is approved.
Responds with signed Discharge / CapToken.
"""

from __future__ import annotations

import contextlib
import json
import os
import socket
import struct
import sys
from typing import Any


def serve(socket_path: str | None = None) -> None:
    """Start the keyring service on *socket_path*.

    If socket_path is None, reads $AEP_KEYRING_SOCKET env var.
    """
    path = socket_path or os.environ.get("AEP_KEYRING_SOCKET")
    if not path:
        print("aethermesh: keyring serve: AEP_KEYRING_SOCKET not set", file=sys.stderr)
        sys.exit(2)

    # Remove stale socket
    with contextlib.suppress(OSError):
        os.unlink(path)

    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)  # type: ignore[attr-defined]
    try:
        sock.bind(path)
        sock.listen(5)
        os.chmod(path, 0o600)

        while True:
            conn, _ = sock.accept()
            try:
                _handle_connection(conn)
            except Exception:
                pass
            finally:
                conn.close()
    finally:
        sock.close()
        with contextlib.suppress(OSError):
            os.unlink(path)


def _handle_connection(conn: socket.socket) -> None:
    """Handle a single keyring request."""
    # Read 4-byte length prefix (big-endian)
    header = _recv_exact(conn, 4)
    if not header:
        return
    msg_len = struct.unpack(">I", header)[0]
    if msg_len > 65536:
        return  # refuse oversized messages

    body = _recv_exact(conn, msg_len)
    if not body:
        return

    try:
        request = json.loads(body.decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        _send_error(conn, "invalid JSON")
        return

    response = _dispatch_request(request)
    resp_bytes = json.dumps(response).encode("utf-8")
    conn.sendall(struct.pack(">I", len(resp_bytes)) + resp_bytes)


def _recv_exact(conn: socket.socket, n: int) -> bytes | None:
    buf = b""
    while len(buf) < n:
        chunk = conn.recv(n - len(buf))
        if not chunk:
            return None
        buf += chunk
    return buf


def _send_error(conn: socket.socket, message: str) -> None:
    resp = json.dumps({"error": message}).encode("utf-8")
    conn.sendall(struct.pack(">I", len(resp)) + resp)


def _dispatch_request(req: dict[str, Any]) -> dict[str, Any]:
    req_type = req.get("type", "")
    if req_type == "discharge_request":
        return _handle_discharge_request(req)
    if req_type == "mint_request":
        return _handle_mint_request(req)
    return {"error": f"unknown request type: {req_type}"}


def _handle_discharge_request(req: dict[str, Any]) -> dict[str, Any]:
    """Issue a signed Discharge for a third-party caveat."""
    caveat_type = req.get("caveat_type", "")
    try:
        session_root = bytes.fromhex(req.get("session_root_hex", ""))
        binding_nonce = bytes.fromhex(req.get("binding_nonce_hex", ""))
    except ValueError:
        return {"type": "discharge_response", "status": "error", "reason": "invalid hex"}
    user_consent = req.get("user_consent", False)
    try:
        issued_at = int(req.get("issued_at", 0))
    except (TypeError, ValueError):
        return {"type": "discharge_response", "status": "error", "reason": "invalid issued_at"}

    if not user_consent:
        return {"type": "discharge_response", "status": "denied", "reason": "no user consent"}

    from aethermesh.L5_captokens import Discharge

    d = Discharge(
        caveat_type,
        session_root,
        req.get("discharger_did", ""),
        binding_nonce,
        issued_at,
    )
    return {
        "type": "discharge_response",
        "status": "ok",
        "discharge": {
            "caveat_type": d.caveat_type,
            "session_root": d.session_root.hex(),
            "discharger_did": d.discharger_did,
            "binding_nonce": d.binding_nonce.hex(),
            "issued_at": d.issued_at,
        },
    }


def _handle_mint_request(req: dict[str, Any]) -> dict[str, Any]:
    """Mint a root CapToken."""
    from aethermesh.L5_captokens import CapToken

    try:
        issuer_sk = bytes.fromhex(req.get("issuer_sk_hex", "00" * 32))
    except ValueError:
        return {"type": "mint_response", "status": "error", "reason": "invalid issuer_sk_hex"}

    token = CapToken.mint(
        issuer=req.get("issuer", "did:web:example.org"),
        root_resource=req.get("root_resource", ""),
        resource_template=req.get("resource_template", ""),
        schema_pins=tuple(req.get("schema_pins", ())),
        not_before=req.get("not_before", 0),
        not_after=req.get("not_after", 9999999999),
        revocation_epoch=req.get("revocation_epoch", 0),
        issuer_sk=issuer_sk,
    )
    return {
        "type": "mint_response",
        "status": "ok",
        "captoken": {
            "issuer": token.issuer,
            "root_resource": token.root_resource,
        },
    }
