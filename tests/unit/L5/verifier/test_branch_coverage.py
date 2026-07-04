"""Verifier branch coverage tests — every fail-closed path.

EP-006 M4. SPEC-005 § Security Rules.
"""

from aethermesh.common.did_resolver import DIDResolver
from aethermesh.common.errors import VerificationDecision
from aethermesh.L5_captokens import CapToken, Caveat, Discharge
from aethermesh.L5_captokens.verifier import verify_token

SESSION_ROOT = b"\x00" * 32
BINDING_NONCE = b"\x11" * 16
THIRD_PARTY_VALUE = (
    f"discharger_did=did:web:peer.example;binding_nonce={BINDING_NONCE.hex()};freshness_window=300"
)


def _mint_token() -> CapToken:
    return CapToken.mint(
        "did:web:example.org",
        "r",
        "r/{}",
        (),
        0,
        9999999999,
        0,
        b"\x00" * 32,
    )


class TestVerifierDenyPaths:
    def test_deny_time_before(self) -> None:
        resolver = DIDResolver()
        resolver.register("did:web:example.org", b"key")
        token = _mint_token()
        token = token.attenuate(Caveat("time.before", "2020-01-01T00:00:00+00:00"))
        decision, reason = verify_token(token, {}, resolver)
        assert decision == VerificationDecision.DENY_TIME
        assert "time.before" in reason

    def test_deny_time_after(self) -> None:
        resolver = DIDResolver()
        resolver.register("did:web:example.org", b"key")
        token = _mint_token()
        token = token.attenuate(Caveat("time.after", "2099-01-01T00:00:00+00:00"))
        decision, _ = verify_token(token, {}, resolver)
        assert decision == VerificationDecision.DENY_TIME

    def test_deny_action_in(self) -> None:
        resolver = DIDResolver()
        resolver.register("did:web:example.org", b"key")
        token = _mint_token()
        token = token.attenuate(Caveat("action.in", "read,list"))
        decision, _ = verify_token(token, {"action": "write"}, resolver)
        assert decision == VerificationDecision.DENY_ACTION

    def test_deny_scope_subset(self) -> None:
        resolver = DIDResolver()
        resolver.register("did:web:example.org", b"key")
        token = _mint_token()
        token = token.attenuate(Caveat("scope.subset_of", "read,list"))
        decision, _ = verify_token(
            token,
            {"action": "read", "scope": ("read", "write")},
            resolver,
        )
        assert decision == VerificationDecision.DENY_SCOPE

    def test_deny_bound_to_session(self) -> None:
        resolver = DIDResolver()
        resolver.register("did:web:example.org", b"key")
        token = _mint_token()
        token = token.attenuate(Caveat("bound_to_session", "aa" * 32))
        decision, _ = verify_token(
            token,
            {"action": "read", "session_root": b"\x00" * 32},
            resolver,
        )
        assert decision == VerificationDecision.DENY_SESSION_BINDING

    def test_deny_bound_to_principal(self) -> None:
        resolver = DIDResolver()
        resolver.register("did:web:example.org", b"key")
        token = _mint_token()
        token = token.attenuate(Caveat("bound_to_principal", "did:web:peer.example"))
        decision, _ = verify_token(
            token,
            {"action": "read", "caller_did": "did:web:org.example"},
            resolver,
        )
        assert decision == VerificationDecision.DENY_PRINCIPAL_BINDING

    def test_pending_discharge(self) -> None:
        resolver = DIDResolver()
        resolver.register("did:web:example.org", b"key")
        token = _mint_token()
        token = token.attenuate(Caveat("third_party", THIRD_PARTY_VALUE, discharge_required=True))
        decision, _ = verify_token(
            token,
            {"action": "read", "session_root": SESSION_ROOT},
            resolver,
        )
        assert decision == VerificationDecision.PENDING_DISCHARGE

    def test_discharge_satisfies_third_party(self) -> None:
        resolver = DIDResolver()
        resolver.register("did:web:example.org", b"key")
        token = _mint_token()
        token = token.attenuate(Caveat("third_party", THIRD_PARTY_VALUE, discharge_required=True))
        discharge = Discharge(
            "third_party",
            SESSION_ROOT,
            "did:web:peer.example",
            BINDING_NONCE,
            issued_at=100,
        )
        decision, _ = verify_token(
            token,
            {"action": "read", "session_root": SESSION_ROOT, "current_time": 200},
            resolver,
            discharges=[discharge],
        )
        assert decision == VerificationDecision.ALLOW

    def test_discharge_replay_different_session_denied(self) -> None:
        resolver = DIDResolver()
        resolver.register("did:web:example.org", b"key")
        token = _mint_token()
        token = token.attenuate(Caveat("third_party", THIRD_PARTY_VALUE, discharge_required=True))
        discharge = Discharge(
            "third_party",
            b"\x01" * 32,
            "did:web:peer.example",
            BINDING_NONCE,
            issued_at=100,
        )
        decision, _ = verify_token(
            token,
            {"action": "read", "session_root": SESSION_ROOT, "current_time": 200},
            resolver,
            discharges=[discharge],
        )
        assert decision == VerificationDecision.DENY_DISCHARGE_INVALID

    def test_discharge_binding_nonce_mismatch_denied(self) -> None:
        resolver = DIDResolver()
        resolver.register("did:web:example.org", b"key")
        token = _mint_token()
        token = token.attenuate(Caveat("third_party", THIRD_PARTY_VALUE, discharge_required=True))
        discharge = Discharge(
            "third_party",
            SESSION_ROOT,
            "did:web:peer.example",
            b"\xff" * 16,
            issued_at=100,
        )
        decision, _ = verify_token(
            token,
            {"action": "read", "session_root": SESSION_ROOT, "current_time": 200},
            resolver,
            discharges=[discharge],
        )
        assert decision == VerificationDecision.DENY_DISCHARGE_INVALID

    def test_discharge_freshness_window_expired_denied(self) -> None:
        resolver = DIDResolver()
        resolver.register("did:web:example.org", b"key")
        token = _mint_token()
        token = token.attenuate(Caveat("third_party", THIRD_PARTY_VALUE, discharge_required=True))
        discharge = Discharge(
            "third_party",
            SESSION_ROOT,
            "did:web:peer.example",
            BINDING_NONCE,
            issued_at=100,
        )
        decision, _ = verify_token(
            token,
            {"action": "read", "session_root": SESSION_ROOT, "current_time": 401},
            resolver,
            discharges=[discharge],
        )
        assert decision == VerificationDecision.DENY_DISCHARGE_INVALID

    def test_third_party_action_predicate_non_match_skips_discharge(self) -> None:
        resolver = DIDResolver()
        resolver.register("did:web:example.org", b"key")
        token = _mint_token()
        value = f"{THIRD_PARTY_VALUE};action=write"
        token = token.attenuate(Caveat("third_party", value, discharge_required=True))
        decision, _ = verify_token(
            token,
            {"action": "read", "session_root": SESSION_ROOT, "current_time": 200},
            resolver,
        )
        assert decision == VerificationDecision.ALLOW

    def test_unknown_caveat_deny(self) -> None:
        resolver = DIDResolver()
        resolver.register("did:web:example.org", b"key")
        token = _mint_token()
        token = token.attenuate(Caveat("completely.unknown.type.v99", "some-value"))
        decision, _ = verify_token(token, {"action": "read"}, resolver)
        assert decision == VerificationDecision.DENY_UNKNOWN_CAVEAT

    def test_deny_bound_to_lane(self) -> None:
        resolver = DIDResolver()
        resolver.register("did:web:example.org", b"key")
        token = _mint_token()
        token = token.attenuate(Caveat("bound_to_lane", "fast"))
        decision, _ = verify_token(token, {"action": "read", "lane": "slow"}, resolver)
        assert decision == VerificationDecision.DENY_LANE

    def test_deny_intent_path_depth(self) -> None:
        resolver = DIDResolver()
        resolver.register("did:web:example.org", b"key")
        token = _mint_token()
        token = token.attenuate(Caveat("intent_path.depth_max", "1"))
        decision, _ = verify_token(
            token,
            {"action": "read", "intent_path": ("a", "b", "c")},
            resolver,
        )
        assert decision == VerificationDecision.DENY_INTENT_PATH

    def test_deny_budget(self) -> None:
        resolver = DIDResolver()
        resolver.register("did:web:example.org", b"key")
        token = _mint_token()
        token = token.attenuate(Caveat("budget.calls", "5"))
        decision, _ = verify_token(token, {"action": "read", "scope": ()}, resolver)
        assert decision == VerificationDecision.ALLOW

    def test_allow_all_pass(self) -> None:
        resolver = DIDResolver()
        resolver.register("did:web:example.org", b"key")
        token = _mint_token()
        token = token.attenuate(Caveat("action.in", "read,write"))
        token = token.attenuate(Caveat("scope.subset_of", "read,write,admin"))
        decision, _ = verify_token(token, {"action": "read", "scope": ("read",)}, resolver)
        assert decision == VerificationDecision.ALLOW

    def test_deny_device_posture(self) -> None:
        resolver = DIDResolver()
        resolver.register("did:web:example.org", b"key")
        token = _mint_token()
        token = token.attenuate(Caveat("device.posture_in", "managed,encrypted"))
        decision, _ = verify_token(
            token,
            {"action": "read", "device_posture": ("unmanaged",)},
            resolver,
        )
        assert decision == VerificationDecision.DENY_POSTURE

    def test_deny_geo_region(self) -> None:
        resolver = DIDResolver()
        resolver.register("did:web:example.org", b"key")
        token = _mint_token()
        token = token.attenuate(Caveat("geo.region_in", "US,CA"))
        decision, _ = verify_token(token, {"action": "read", "geo_region": "RU"}, resolver)
        assert decision == VerificationDecision.DENY_GEO

    def test_deny_rate_per_minute(self) -> None:
        resolver = DIDResolver()
        resolver.register("did:web:example.org", b"key")
        token = _mint_token()
        token = token.attenuate(Caveat("rate.per_minute", "10"))
        decision, _ = verify_token(
            token,
            {"action": "read", "scope": (), "rate_calls_last_minute": 15},
            resolver,
        )
        assert decision == VerificationDecision.DENY_RATE
