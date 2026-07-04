"""Keyring Unix socket integration test — EP-006 M5.

Uses temp socket path, length-prefixed JSON development stand-in for CBOR.
AF_UNIX not available at type-check time on Windows.
"""

# mypy: ignore-errors

import contextlib
import json
import os
import socket
import struct
import sys
import tempfile
import threading
import time

import pytest

from aethermesh.tools.keyring_serve import serve

pytestmark = pytest.mark.skipif(
    sys.platform == "win32",
    reason="Unix domain sockets not available on Windows",
)


def _send_recv(sock: socket.socket, request: dict[str, object]) -> dict[str, object]:
    """Send a length-prefixed JSON request, receive response."""
    body = json.dumps(request).encode("utf-8")
    sock.sendall(struct.pack(">I", len(body)) + body)

    # Read response
    header = b""
    while len(header) < 4:
        chunk = sock.recv(4 - len(header))
        if not chunk:
            raise ConnectionError("no response")
        header += chunk
    msg_len = struct.unpack(">I", header)[0]
    resp = b""
    while len(resp) < msg_len:
        chunk = sock.recv(msg_len - len(resp))
        if not chunk:
            break
        resp += chunk
    return json.loads(resp.decode("utf-8"))


@pytest.fixture
def keyring_socket():
    """Start keyring server on a temp socket, yield path, teardown."""
    fd, path = tempfile.mkstemp(suffix=".sock", prefix="aep_keyring_")
    os.close(fd)
    os.unlink(path)

    server_started = threading.Event()

    def _run() -> None:
        # Signal ready, then serve
        server_started.set()
        serve(path)

    t = threading.Thread(target=_run, daemon=True)
    t.start()

    # Wait for server to be ready
    if not server_started.wait(timeout=5):
        pytest.skip("keyring server did not start")

    time.sleep(0.1)  # Let socket bind

    yield path

    # Cleanup
    with contextlib.suppress(OSError):
        os.unlink(path)


class TestKeyringIpc:
    def test_discharge_request_consent(self, keyring_socket: str) -> None:
        """discharge_request with user_consent=True returns signed Discharge."""
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        sock.settimeout(5)
        try:
            sock.connect(keyring_socket)
            resp = _send_recv(
                sock,
                {
                    "type": "discharge_request",
                    "caveat_type": "third_party",
                    "session_root_hex": "00" * 32,
                    "binding_nonce_hex": "11" * 16,
                    "discharger_did": "did:web:peer.example",
                    "issued_at": 100,
                    "user_consent": True,
                },
            )
            assert resp["type"] == "discharge_response"
            assert resp["status"] == "ok"
            assert "discharge" in resp
        finally:
            sock.close()

    def test_discharge_request_no_consent(self, keyring_socket: str) -> None:
        """discharge_request with user_consent=False is denied."""
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        sock.settimeout(5)
        try:
            sock.connect(keyring_socket)
            resp = _send_recv(
                sock,
                {
                    "type": "discharge_request",
                    "caveat_type": "third_party",
                    "session_root_hex": "00" * 32,
                    "discharger_did": "did:web:peer.example",
                    "user_consent": False,
                },
            )
            assert resp["status"] == "denied"
        finally:
            sock.close()

    def test_mint_request(self, keyring_socket: str) -> None:
        """mint_request returns a new CapToken."""
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        sock.settimeout(5)
        try:
            sock.connect(keyring_socket)
            resp = _send_recv(
                sock,
                {
                    "type": "mint_request",
                    "issuer": "did:web:example.org",
                    "root_resource": "demo",
                    "resource_template": "demo/{}",
                    "issuer_sk_hex": "00" * 32,
                },
            )
            assert resp["type"] == "mint_response"
            assert resp["status"] == "ok"
            assert "captoken" in resp
        finally:
            sock.close()

    def test_unknown_request_type(self, keyring_socket: str) -> None:
        """Unknown request type returns error."""
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        sock.settimeout(5)
        try:
            sock.connect(keyring_socket)
            resp = _send_recv(sock, {"type": "garbage"})
            assert "error" in resp
        finally:
            sock.close()
