"""CLI `aethermesh demo --layer N` — honest smoke paths.

EP-005 M2. Exercises the aethermesh.api facade with the layer stubs from EP-004.
Does NOT claim production protocol behavior — stubs return fixed values.
"""

import argparse

from aethermesh.cli.common import EXIT_SUCCESS, print_line


def run(args: argparse.Namespace) -> int:
    """Run a layer demo."""
    layer = args.layer
    lane = getattr(args, "lane", "fast")

    print_line(f"=== AetherMesh L{layer} Demo (lane={lane}) ===", color="green")

    if layer == 1:
        return _demo_l1()
    if layer == 2:
        return _demo_l2()
    if layer == 3:
        return _demo_l3()
    if layer == 4:
        return _demo_l4()
    if layer == 5:
        return _demo_l5()

    return EXIT_SUCCESS


def _demo_l1() -> int:
    """L1 Sphinx transport demo — honest stub path."""
    print_line("L1 Sphinx: fixed 2048-byte packets over q-mix QUIC")
    print_line("  [stub] Sphinx packet assembled (placeholder backend)")
    print_line("  [stub] Fast-lane path via in-process simulator")
    print_line("  [stub] Cover scheduler: 5 pps active, 1 pps idle")
    print_line("=== DONE ===", color="green")
    return EXIT_SUCCESS


def _demo_l2() -> int:
    """L2 DHT discovery demo — honest stub path."""
    print_line("L2 Discovery: capability-hashed DHT lookup")
    print_line("  [stub] CapabilityDescriptor registered")
    print_line("  [stub] Kademlia bucket-PIR lookup (local)")
    print_line("  [stub] SphinxIntroBlock resolved")
    print_line("=== DONE ===", color="green")
    return EXIT_SUCCESS


def _demo_l3() -> int:
    """L3 Handshake demo — honest stub path."""
    from aethermesh.api import HandshakeInitiator

    print_line("L3 Handshake: Noise-PQ XK + mutual attestation")

    initiator = HandshakeInitiator(
        responder_static_x25519_pub=b"\x00" * 32,
        responder_static_mlkem_pub=b"\x00" * 1184,
        prologue=b"AetherMesh demo",
        principal=b"demo-principal-32-bytes-here!",
        instance=b"demo-instance",
        platform_signing_key=b"\x00" * 32,
        platform_root_pub=b"\x00" * 32,
        expected_responder_principal_pub=b"peer-principal-32-bytes-here",
        expected_responder_platform_root_pub=b"\x00" * 32,
        accepted_responder_backends=("softsign",),
        capability_query=b"demo-query",
    )
    msg1 = initiator.build_message_1()
    print_line(f"  [stub] Msg1 built ({len(msg1)} bytes)")

    initiator.process_message_2(b"stub-msg2")
    msg3 = initiator.build_message_3(captoken_bundle=[])
    print_line(f"  [stub] Msg3 built ({len(msg3)} bytes)")

    session = initiator.finalize()
    print_line(f"  [stub] Session finalized (root={session.session_root[:4].hex()}...)")

    print_line("=== DONE ===", color="green")
    return EXIT_SUCCESS


def _demo_l4() -> int:
    """L4 Session demo — honest stub path."""
    from aethermesh.api import IntentHeader, PairRatchet, PolicyLayer

    print_line("L4 Session: PQ Double Ratchet + policy layer")

    alice = PairRatchet.initialize_alice(
        root_key=b"\x00" * 32,
        bob_dh_x25519_pub=b"\x00" * 32,
        bob_dh_mlkem_pub=b"\x00" * 1184,
    )
    msg = alice.encrypt(b"intent-header", b"hello world", session_id=b"\x00" * 32)
    print_line(f"  [stub] Encrypted message ({len(msg.body)} bytes body)")

    intent = IntentHeader(action="read", resource="demo/doc")
    policy = PolicyLayer()
    from aethermesh.api import CapToken

    token = CapToken.mint(
        "did:web:example.org",
        "demo",
        "demo/{}",
        (),
        0,
        9999999999,
        0,
        b"\x00" * 32,
    )
    policy.add_captoken(token)
    result = policy.validate(ns=0, intent=intent)
    print_line(f"  [stub] Policy decision: {result.name}")

    print_line("=== DONE ===", color="green")
    return EXIT_SUCCESS


def _demo_l5() -> int:
    """L5 Authority demo — honest stub path."""
    from aethermesh.api import (
        AuditLog,
        AuditReceipt,
        CapToken,
        CapTokenVerifier,
        Caveat,
    )
    from aethermesh.common.did_resolver import DIDResolver

    print_line("L5 Authority: CapTokens + caveats + audit")

    token = CapToken.mint(
        "did:web:example.org",
        "demo",
        "demo/{}",
        (),
        0,
        9999999999,
        0,
        b"\x00" * 32,
    )
    print_line(f"  [stub] CapToken minted (issuer={token.issuer})")

    attenuated = token.attenuate(Caveat("time", "2026-12-31"))
    print_line(f"  [stub] Attenuated with {len(attenuated.caveats)} caveat(s)")

    resolver = DIDResolver()
    resolver.register("did:web:example.org", b"test-pubkey")
    verifier = CapTokenVerifier(resolver, revocation_registry=object())
    vresult = verifier.verify(token, request={})
    print_line(f"  [stub] Verification: {vresult.decision.name}")

    audit = AuditLog()
    audit.append(
        AuditReceipt(
            receipt_id=b"\x00" * 32,
            session_root_hash=b"\x00" * 32,
            message_index=0,
            intent_header_hash=b"\x00" * 32,
            body_hash=b"\x00" * 32,
            caller_did="did:web:example.org",
            callee_did="did:web:peer.example",
            policy_decision="ALLOW",
            captoken_chain="[]",
            discharge_refs="[]",
            timestamp=1700000000,
            sig=b"\x00" * 64,
        )
    )
    print_line("  [stub] Audit receipt appended")

    print_line("=== DONE ===", color="green")
    return EXIT_SUCCESS
