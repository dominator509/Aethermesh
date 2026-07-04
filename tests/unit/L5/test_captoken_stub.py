"""Tests for L5 CapToken, Caveat, CapTokenVerifier, KeyringService, AuditLog — coverage backfill.

EP-007 M2.
"""

from aethermesh.common.did_resolver import DIDResolver
from aethermesh.common.errors import VerificationDecision
from aethermesh.L5_captokens import (
    AuditLog,
    AuditReceipt,
    CapToken,
    CapTokenVerifier,
    Caveat,
    Discharge,
    KeyringService,
    VerificationResult,
)


class TestCapToken:
    def test_mint(self) -> None:
        token = CapToken.mint(
            "did:web:example.org", "r", "r/{}", ("schema1",), 0, 9999999999, 0, b"\x00" * 32
        )
        assert token.issuer == "did:web:example.org"
        assert token.root_resource == "r"
        assert token.resource_template == "r/{}"
        assert token.schema_pins == ("schema1",)
        assert token.not_before == 0
        assert token.not_after == 9999999999
        assert token.revocation_epoch == 0

    def test_attenuate(self) -> None:
        token = CapToken.mint(
            "did:web:example.org",
            "r",
            "r/{}",
            (),
            0,
            9999999999,
            0,
            b"\x00" * 32,
        )
        attenuated = token.attenuate(Caveat("time.before", "2099-01-01T00:00:00+00:00"))
        assert attenuated.issuer == token.issuer
        assert len(attenuated.caveats) == 1
        assert len(token.caveats) == 0  # original unchanged

    def test_multiple_attenuations(self) -> None:
        token = CapToken.mint(
            "did:web:example.org",
            "r",
            "r/{}",
            (),
            0,
            9999999999,
            0,
            b"\x00" * 32,
        )
        token = token.attenuate(Caveat("time.before", "2099-01-01T00:00:00"))
        token = token.attenuate(Caveat("action.in", "read"))
        assert len(token.caveats) == 2

    def test_verify_root(self) -> None:
        token = CapToken.mint(
            "did:web:example.org",
            "r",
            "r/{}",
            (),
            0,
            9999999999,
            0,
            b"\x00" * 32,
        )
        resolver = DIDResolver()
        resolver.register("did:web:example.org", b"key")
        assert token.verify_root(resolver) is True

    def test_verify_chain(self) -> None:
        token = CapToken.mint(
            "did:web:example.org",
            "r",
            "r/{}",
            (),
            0,
            9999999999,
            0,
            b"\x00" * 32,
        )
        assert token.verify_chain() is True

    def test_constructor(self) -> None:
        token = CapToken("did:web:example.org", "r", "r/{}", ("s",), 100, 200, 0)
        assert token.issuer == "did:web:example.org"
        assert token.not_before == 100
        assert token.not_after == 200


class TestCaveat:
    def test_construct(self) -> None:
        c = Caveat("time.before", "2026-12-31")
        assert c.caveat_type == "time.before"
        assert c.value == "2026-12-31"
        assert c.discharge_required is False

    def test_discharge_required(self) -> None:
        c = Caveat("third_party", "did:web:org.example", discharge_required=True)
        assert c.discharge_required is True


class TestCapTokenVerifier:
    def test_construct(self) -> None:
        resolver = DIDResolver()
        verifier = CapTokenVerifier(resolver, revocation_registry=object())
        assert verifier._resolver is resolver

    def test_construct_with_schema_registry(self) -> None:
        resolver = DIDResolver()
        verifier = CapTokenVerifier(resolver, revocation_registry=object(), schema_registry={})
        assert verifier._resolver is resolver

    def test_verify_allow(self) -> None:
        resolver = DIDResolver()
        resolver.register("did:web:example.org", b"key")
        verifier = CapTokenVerifier(resolver, revocation_registry=object())
        token = CapToken.mint(
            "did:web:example.org",
            "r",
            "r/{}",
            (),
            0,
            9999999999,
            0,
            b"\x00" * 32,
        )
        result = verifier.verify(token, request={})
        assert result.decision == VerificationDecision.ALLOW


class TestVerificationResult:
    def test_defaults(self) -> None:
        vr = VerificationResult(decision=VerificationDecision.ALLOW)
        assert vr.decision == VerificationDecision.ALLOW
        assert vr.reason == ""


class TestDischarge:
    def test_construct(self) -> None:
        d = Discharge("third_party", b"\x00" * 32, "did:web:org.example")
        assert d.caveat_type == "third_party"
        assert d.session_root == b"\x00" * 32
        assert d.discharger_did == "did:web:org.example"


class TestKeyringService:
    def test_create(self) -> None:
        ks = KeyringService.create("did:web:example.org", "did:web:org.example")
        assert ks.principal_did == "did:web:example.org"
        assert ks.discharger_did == "did:web:org.example"

    def test_mint_root_captoken(self) -> None:
        ks = KeyringService.create("did:web:example.org", "did:web:org.example")
        token = ks.mint_root_captoken(
            resource="api", not_before=0, not_after=9999999999, revocation_epoch=0
        )
        assert token.issuer == "did:web:example.org"

    def test_issue_discharge_consent(self) -> None:
        ks = KeyringService.create("did:web:example.org", "did:web:org.example")
        d = ks.issue_discharge(Caveat("third_party", "dc"), b"\x00" * 32, True)
        assert d is not None
        assert d.discharger_did == "did:web:org.example"

    def test_issue_discharge_no_consent(self) -> None:
        ks = KeyringService.create("did:web:example.org", "did:web:org.example")
        d = ks.issue_discharge(Caveat("third_party", "dc"), b"\x00" * 32, False)
        assert d is None


class TestAuditLog:
    def test_init(self) -> None:
        log = AuditLog()
        assert log is not None

    def test_init_with_path(self) -> None:
        log = AuditLog(db_path="/tmp/test.db")
        assert log._db_path == "/tmp/test.db"

    def test_append(self) -> None:
        log = AuditLog()
        receipt = AuditReceipt(
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
        log.append(receipt)

    def test_all_for_session(self) -> None:
        log = AuditLog()
        result = log.all_for_session(b"\x00" * 32)
        assert result == []


class TestAuditReceipt:
    def test_construct(self) -> None:
        receipt = AuditReceipt(
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
        assert receipt.caller_did == "did:web:example.org"
        assert receipt.policy_decision == "ALLOW"
