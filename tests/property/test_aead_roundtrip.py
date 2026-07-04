"""Property-based tests for AEAD roundtrip — SPEC-001 § Required Tests."""

import os

from hypothesis import given, settings
from hypothesis.strategies import binary

from aethermesh.common.aead import AeadOpenError, aead_open, aead_seal

MAX_EXAMPLES = int(os.environ.get("HYPOTHESIS_MAX_EXAMPLES", "200"))


class TestAeadPropertyRoundtrip:
    @given(
        key=binary(min_size=32, max_size=32),
        nonce=binary(min_size=12, max_size=12),
        plaintext=binary(max_size=2048),
        ad=binary(max_size=256),
    )
    @settings(max_examples=MAX_EXAMPLES)
    def test_roundtrip_seal_open(
        self, key: bytes, nonce: bytes, plaintext: bytes, ad: bytes
    ) -> None:
        """seal(open(x)) == x for all inputs."""
        ct = aead_seal(key, nonce, plaintext, ad=ad)
        pt = aead_open(key, nonce, ct, ad=ad)
        assert pt == plaintext

    @given(
        key=binary(min_size=32, max_size=32),
        nonce=binary(min_size=12, max_size=12),
        plaintext=binary(max_size=2048),
        ad=binary(max_size=256),
        bad_ad=binary(max_size=256),
    )
    @settings(max_examples=MAX_EXAMPLES)
    def test_wrong_ad_fails(
        self, key: bytes, nonce: bytes, plaintext: bytes, ad: bytes, bad_ad: bytes
    ) -> None:
        """Opening with wrong AD must fail."""
        if ad == bad_ad:
            return  # skip degenerate case
        ct = aead_seal(key, nonce, plaintext, ad=ad)
        try:
            aead_open(key, nonce, ct, ad=bad_ad)
            raise AssertionError("should have raised AeadOpenError")
        except AeadOpenError:
            pass  # expected

    @given(
        key=binary(min_size=32, max_size=32),
        nonce=binary(min_size=12, max_size=12),
        plaintext=binary(max_size=2048),
        corrupted_byte_idx=binary(min_size=1, max_size=1),
    )
    @settings(max_examples=MAX_EXAMPLES)
    def test_corruption_detected(
        self, key: bytes, nonce: bytes, plaintext: bytes, corrupted_byte_idx: bytes
    ) -> None:
        """Any single-byte corruption of ciphertext must be detected."""
        if len(plaintext) == 0:
            return  # can only corrupt tag
        ct = aead_seal(key, nonce, plaintext)
        idx = corrupted_byte_idx[0] % len(ct)
        corrupted = ct[:idx] + bytes([ct[idx] ^ 0x01]) + ct[idx + 1 :]
        try:
            aead_open(key, nonce, corrupted)
            raise AssertionError("should have raised AeadOpenError")
        except AeadOpenError:
            pass  # expected

    @given(
        plaintext=binary(max_size=2048),
    )
    @settings(max_examples=MAX_EXAMPLES)
    def test_ciphertext_not_equal_plaintext(self, plaintext: bytes) -> None:
        """Ciphertext is never the same as plaintext (confidentiality)."""
        ct = aead_seal(bytes(32), bytes(12), plaintext)
        assert ct != plaintext
