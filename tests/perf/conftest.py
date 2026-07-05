"""Shared fixtures for EP-010 M4 performance benchmarks."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

import pytest

from aethermesh.api import (
    CapToken,
    Caveat,
    Discharge,
    HandshakeInitiator,
    HandshakeResponder,
    PairRatchet,
    SessionState,
)
from aethermesh.common.constants import SPHINX_PACKET_SIZE
from aethermesh.common.did_resolver import DIDResolver
from aethermesh.L5_captokens.caveats import CaveatType

ALICE_PRINCIPAL = b"alice-principal-32-bytes!!!"
BOB_PRINCIPAL = b"bob-principal-32-bytes!!!!!"
X25519_PUB = bytes(range(32))
MLKEM_PUB = bytes(i % 256 for i in range(1184))
PROLOGUE = b"AetherMesh v0.1 perf prologue"


def _placeholder_l1_fast_lane(packet: bytes) -> None:
    """Current L1 contract: fixed-size packet validation only."""
    if len(packet) != SPHINX_PACKET_SIZE:
        raise ValueError(f"expected {SPHINX_PACKET_SIZE} bytes, got {len(packet)}")


def _run_l3_handshake() -> tuple[SessionState, SessionState]:
    """Run the current end-to-end L3 handshake facade."""
    token = CapToken.mint(
        issuer="did:web:example.org",
        root_resource="doc-review",
        resource_template="doc-review/{doc_id}",
        schema_pins=(),
        not_before=0,
        not_after=9_999_999_999,
        revocation_epoch=0,
        issuer_sk=b"\x00" * 32,
    )

    initiator = HandshakeInitiator(
        responder_static_x25519_pub=X25519_PUB,
        responder_static_mlkem_pub=MLKEM_PUB,
        prologue=PROLOGUE,
        principal=ALICE_PRINCIPAL,
        instance=b"instance-a",
        platform_signing_key=b"\x00" * 32,
        platform_root_pub=b"\x00" * 32,
        expected_responder_principal_pub=BOB_PRINCIPAL,
        expected_responder_platform_root_pub=b"\x00" * 32,
        accepted_responder_backends=("softsign",),
        capability_query=b"doc-review",
    )
    responder = HandshakeResponder(
        static_x25519_sk=b"\x00" * 32,
        static_mlkem_sk=b"\x00" * 2400,
        prologue=PROLOGUE,
        principal=BOB_PRINCIPAL,
        instance=b"instance-b",
        platform_signing_key=b"\x00" * 32,
        platform_root_pub=b"\x00" * 32,
        expected_initiator_principal_pub=ALICE_PRINCIPAL,
        expected_initiator_platform_root_pub=b"\x00" * 32,
        accepted_initiator_backends=("softsign",),
    )

    msg1 = initiator.build_message_1()
    msg2 = responder.process_message_1(msg1)
    initiator.process_message_2(msg2)
    msg3 = initiator.build_message_3(captoken_bundle=[token])
    responder.process_message_3(msg3)
    return initiator.finalize(), responder.finalize()


@pytest.fixture(scope="session")
def perf_results_dir() -> Path:
    """Tracked output directory for benchmark JSON artifacts."""
    return Path(__file__).parent / "results"


@pytest.fixture(scope="session")
def l1_fast_lane_case() -> tuple[Callable[[bytes], None], bytes]:
    """Current L1 benchmark surface and a fixed-size TEST_ONLY packet."""
    packet = bytes(range(256)) * (SPHINX_PACKET_SIZE // 256)
    return _placeholder_l1_fast_lane, packet


@pytest.fixture(scope="session")
def l3_handshake_case() -> Callable[[], tuple[SessionState, SessionState]]:
    """Callable that executes the current L3 handshake facade."""
    return _run_l3_handshake


@pytest.fixture(scope="session")
def l4_non_dh_case() -> tuple[PairRatchet, bytes, bytes, bytes]:
    """Benchmark input for the current non-DH L4 message path."""
    ratchet = PairRatchet.initialize_alice(
        root_key=b"\x00" * 32,
        bob_dh_x25519_pub=X25519_PUB,
        bob_dh_mlkem_pub=MLKEM_PUB,
    )
    intent_header = b'{"action":"read","resource":"doc-review/42"}'
    body = b"hello world" * 8
    session_id = b"\x55" * 32
    return ratchet, intent_header, body, session_id


@pytest.fixture(scope="session")
def l5_verify_case() -> tuple[CapToken, dict[str, object], DIDResolver, list[Discharge]]:
    """Benchmark input for the current L5 caveat-verification path."""
    resolver = DIDResolver()
    resolver.register("did:web:example.org", b'{"key":"test-pubkey"}')

    current_time = 1_700_000_000
    session_root = bytes(range(32))
    binding_nonce = bytes(range(16))

    token = CapToken.mint(
        issuer="did:web:example.org",
        root_resource="doc-review",
        resource_template="doc-review/{doc_id}",
        schema_pins=("schema:v1",),
        not_before=0,
        not_after=9_999_999_999,
        revocation_epoch=0,
        issuer_sk=b"\x00" * 32,
    )
    caveats = [
        Caveat(CaveatType.TIME_BEFORE, "2100-01-01T00:00:00+00:00"),
        Caveat(CaveatType.TIME_AFTER, "2020-01-01T00:00:00+00:00"),
        Caveat(CaveatType.ACTION_IN, "read,write"),
        Caveat(CaveatType.SCOPE_SUBSET, "read,write"),
        Caveat(CaveatType.BUDGET_CALLS, "5"),
        Caveat(CaveatType.BUDGET_TOKENS, "4096"),
        Caveat(CaveatType.BUDGET_WALL_MS, "250"),
        Caveat(CaveatType.RATE_PER_MINUTE, "60"),
        Caveat(CaveatType.BOUND_TO_SESSION, session_root.hex()),
        Caveat(CaveatType.BOUND_TO_PRINCIPAL, "did:web:example.org"),
        Caveat(CaveatType.BOUND_TO_LANE, "fast"),
        Caveat(CaveatType.INTENT_PATH_ROOT, "doc-review"),
        Caveat(CaveatType.INTENT_PATH_DEPTH, "2"),
        Caveat(
            CaveatType.THIRD_PARTY,
            (
                "discharger_did=did:web:org.example;"
                f"binding_nonce={binding_nonce.hex()};"
                "freshness_window=300;"
                "action.in=read"
            ),
            discharge_required=True,
        ),
    ]
    for caveat in caveats:
        token = token.attenuate(caveat)

    request = {
        "current_time": current_time,
        "action": "read",
        "scope": ("read",),
        "session_root": session_root,
        "caller_did": "did:web:example.org",
        "lane": "fast",
        "intent_path": ("doc-review", "42"),
        "budget_calls_remaining": 1,
        "budget_tokens_remaining": 512,
        "budget_wall_ms_elapsed": 75,
        "rate_calls_last_minute": 10,
    }
    discharges = [
        Discharge(
            CaveatType.THIRD_PARTY,
            session_root=session_root,
            discharger_did="did:web:org.example",
            binding_nonce=binding_nonce,
            issued_at=current_time - 10,
        )
    ]
    return token, request, resolver, discharges
