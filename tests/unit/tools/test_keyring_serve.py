"""Unit coverage for keyring IPC helpers."""

from __future__ import annotations

import json
import struct
from typing import cast

import pytest

from aethermesh.tools import keyring_serve


class FakeConn:
    def __init__(self, chunks: list[bytes]) -> None:
        self._chunks = chunks
        self.sent = b""

    def recv(self, n: int) -> bytes:
        if not self._chunks:
            return b""
        chunk = self._chunks.pop(0)
        if len(chunk) > n:
            self._chunks.insert(0, chunk[n:])
            return chunk[:n]
        return chunk

    def sendall(self, data: bytes) -> None:
        self.sent += data


def _decode_sent(conn: FakeConn) -> dict[str, object]:
    length = struct.unpack(">I", conn.sent[:4])[0]
    return cast(dict[str, object], json.loads(conn.sent[4 : 4 + length].decode("utf-8")))


def test_dispatch_unknown_request_type() -> None:
    assert "error" in keyring_serve._dispatch_request({"type": "bad"})


def test_discharge_request_denied() -> None:
    response = keyring_serve._dispatch_request(
        {
            "type": "discharge_request",
            "caveat_type": "third_party",
            "session_root_hex": "00" * 32,
            "discharger_did": "did:web:org.example",
            "user_consent": False,
        }
    )
    assert response["status"] == "denied"


def test_discharge_request_ok() -> None:
    response = keyring_serve._dispatch_request(
        {
            "type": "discharge_request",
            "caveat_type": "third_party",
            "session_root_hex": "00" * 32,
            "binding_nonce_hex": "11" * 16,
            "discharger_did": "did:web:org.example",
            "issued_at": 100,
            "user_consent": True,
        }
    )
    assert response["status"] == "ok"
    discharge = response["discharge"]
    assert isinstance(discharge, dict)
    assert discharge["binding_nonce"] == "11" * 16


@pytest.mark.parametrize(
    "req",
    [
        {"type": "discharge_request", "session_root_hex": "not-hex", "user_consent": True},
        {
            "type": "discharge_request",
            "session_root_hex": "00" * 32,
            "issued_at": "not-an-int",
            "user_consent": True,
        },
        {"type": "mint_request", "issuer_sk_hex": "not-hex"},
    ],
)
def test_request_validation_errors(req: dict[str, object]) -> None:
    response = keyring_serve._dispatch_request(req)
    assert response["status"] == "error"


def test_mint_request_defaults_to_allowed_did() -> None:
    response = keyring_serve._dispatch_request(
        {
            "type": "mint_request",
            "root_resource": "demo",
            "resource_template": "demo/{}",
            "issuer_sk_hex": "00" * 32,
        }
    )
    assert response["status"] == "ok"
    captoken = response["captoken"]
    assert isinstance(captoken, dict)
    assert captoken["issuer"] == "did:web:example.org"


def test_handle_connection_invalid_json() -> None:
    body = b"{"
    conn = FakeConn([struct.pack(">I", len(body)), body])
    keyring_serve._handle_connection(conn)  # type: ignore[arg-type]
    assert _decode_sent(conn)["error"] == "invalid JSON"


def test_handle_connection_valid_request() -> None:
    body = json.dumps({"type": "mint_request", "issuer_sk_hex": "00" * 32}).encode()
    conn = FakeConn([struct.pack(">I", len(body)), body])
    keyring_serve._handle_connection(conn)  # type: ignore[arg-type]
    assert _decode_sent(conn)["status"] == "ok"


def test_handle_connection_no_header_returns() -> None:
    conn = FakeConn([])
    keyring_serve._handle_connection(conn)  # type: ignore[arg-type]
    assert conn.sent == b""


def test_handle_connection_oversized_returns() -> None:
    conn = FakeConn([struct.pack(">I", 65537)])
    keyring_serve._handle_connection(conn)  # type: ignore[arg-type]
    assert conn.sent == b""
