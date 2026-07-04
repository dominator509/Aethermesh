"""Hypothesis fuzz target for caveat DSL verifier.

EP-007 M4. Generates random caveat type strings and values,
asserts no uncaught exception escapes eval_caveat / verify_token.
"""

from hypothesis import given, settings
from hypothesis.strategies import sampled_from, text

from aethermesh.common.did_resolver import DIDResolver
from aethermesh.common.errors import VerificationDecision
from aethermesh.L5_captokens import CapToken, Caveat
from aethermesh.L5_captokens.caveats import CaveatType, EvaluationContext, eval_caveat
from aethermesh.L5_captokens.verifier import verify_token

# All known caveat types plus some edge cases
KNOWN_TYPES = [t.value for t in CaveatType]
FUZZ_TYPES = sampled_from(KNOWN_TYPES + ["unknown.fuzz.type", "", "x" * 100])


class TestCaveatFuzz:
    @given(caveat_type=FUZZ_TYPES, value=text(max_size=200))
    @settings(max_examples=200)
    def test_eval_caveat_never_crashes(self, caveat_type: str, value: str) -> None:
        """Any caveat type string + value either returns bool (known) or False (unknown)."""
        ctx = EvaluationContext(
            current_time=1700000000,
            action="read",
            scope=("read",),
            session_root=b"\x00" * 32,
            principal_did="did:web:example.org",
            lane="fast",
        )
        caveat = Caveat(caveat_type, value)
        result = eval_caveat(caveat, ctx)
        assert isinstance(result, bool)

    @given(
        caveat_type=FUZZ_TYPES,
        value=text(max_size=200),
        action=text(max_size=50),
    )
    @settings(max_examples=200)
    def test_verify_token_never_crashes(self, caveat_type: str, value: str, action: str) -> None:
        """verify_token never crashes on random caveat input."""
        resolver = DIDResolver()
        resolver.register("did:web:example.org", b"key")

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
        token = token.attenuate(Caveat(caveat_type, value))

        decision, reason = verify_token(token, {"action": action}, resolver)
        assert isinstance(decision, VerificationDecision)
        assert isinstance(reason, str)
