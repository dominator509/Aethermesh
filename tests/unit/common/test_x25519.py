"""Tests for aethermesh.common.x25519 — SPEC-001 § Required Behavior item 4."""

import pytest

from aethermesh.common.x25519 import x25519_dh, x25519_keygen


class TestX25519Keygen:
    def test_generates_valid_keys(self) -> None:
        sk, pk = x25519_keygen()
        assert len(sk) == 32
        assert len(pk) == 32
        assert sk != pk

    def test_generates_different_keys(self) -> None:
        sk1, pk1 = x25519_keygen()
        sk2, pk2 = x25519_keygen()
        assert sk1 != sk2
        assert pk1 != pk2


class TestX25519Dh:
    def test_shared_secret_symmetry(self) -> None:
        """Alice and Bob compute the same shared secret."""
        sk_a, pk_a = x25519_keygen()
        sk_b, pk_b = x25519_keygen()

        ss_a = x25519_dh(sk_a, pk_b)
        ss_b = x25519_dh(sk_b, pk_a)

        assert ss_a == ss_b
        assert len(ss_a) == 32

    def test_shared_secret_not_zero(self) -> None:
        sk_a, pk_a = x25519_keygen()
        sk_b, pk_b = x25519_keygen()
        ss = x25519_dh(sk_a, pk_b)
        assert ss != b"\x00" * 32

    def test_different_peer_different_secret(self) -> None:
        sk, _ = x25519_keygen()
        _, pk1 = x25519_keygen()
        _, pk2 = x25519_keygen()
        ss1 = x25519_dh(sk, pk1)
        ss2 = x25519_dh(sk, pk2)
        assert ss1 != ss2

    def test_deterministic_with_same_keys(self) -> None:
        """Same key pair produces same shared secret every time."""
        sk, pk = x25519_keygen()
        _, peer_pk = x25519_keygen()
        ss1 = x25519_dh(sk, peer_pk)
        ss2 = x25519_dh(sk, peer_pk)
        assert ss1 == ss2

    def test_bad_secret_key_length(self) -> None:
        _, pk = x25519_keygen()
        with pytest.raises(ValueError, match="secret_key must be 32"):
            x25519_dh(b"short", pk)

    def test_bad_peer_key_length(self) -> None:
        sk, _ = x25519_keygen()
        with pytest.raises(ValueError, match="peer_public_key must be 32"):
            x25519_dh(sk, b"short")

    def test_known_test_vector(self) -> None:
        """RFC 7748 § 6.1 X25519 test vector.

        Alice and Bob fixed keys producing known shared secret.
        """
        alice_sk = bytes.fromhex("77076d0a7318a57d3c16c17251b26645df4c2f87ebc0992ab177fba51db92c2a")
        alice_pk = bytes.fromhex("8520f0098930a754748b7ddcb43ef75a0dbf3a0d26381af4eba4a98eaa9b4e6a")
        bob_sk = bytes.fromhex("5dab087e624a8a4b79e17f8b83800ee66f3bb1292618b6fd1c2f8b27ff88e0eb")
        bob_pk = bytes.fromhex("de9edb7d7b7dc1b4d35b61c2ece435373f8343c85b78674dadfc7e146f882b4f")

        # Verify keygen matches (using from_private_bytes internally)
        ss_alice = x25519_dh(alice_sk, bob_pk)
        ss_bob = x25519_dh(bob_sk, alice_pk)

        expected = bytes.fromhex("4a5d9d5ba4ce2de1728e3bf480350f25e07e21c947d19e3376f09b3c1e161742")
        assert ss_alice == expected
        assert ss_bob == expected
