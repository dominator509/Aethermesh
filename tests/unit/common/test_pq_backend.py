"""Tests for aethermesh.common.pq_backend — SPEC-001 § Required Behavior items 5-6."""

import pytest

from aethermesh.common.pq_backend import (
    MLDSA65_PK_SIZE,
    MLDSA65_SIG_SIZE,
    MLDSA65_SK_SIZE,
    MLKEM768_CT_SIZE,
    MLKEM768_PK_SIZE,
    MLKEM768_SK_SIZE,
    MLKEM768_SS_SIZE,
    hybrid_sign,
    hybrid_verify,
    mldsa_keygen,
    mldsa_sign,
    mldsa_verify,
    mlkem_decaps,
    mlkem_encaps,
    mlkem_keygen,
)

# ---------------------------------------------------------------------------
# ML-KEM-768
# ---------------------------------------------------------------------------


class TestMlKem768:
    def test_keygen_sizes(self) -> None:
        kp = mlkem_keygen()
        assert len(kp.public_key) == MLKEM768_PK_SIZE
        assert len(kp.secret_key) == MLKEM768_SK_SIZE

    def test_encaps_sizes(self) -> None:
        kp = mlkem_keygen()
        ct, ss = mlkem_encaps(kp.public_key)
        assert len(ct) == MLKEM768_CT_SIZE
        assert len(ss) == MLKEM768_SS_SIZE

    def test_decaps_roundtrip(self) -> None:
        """Encaps + decaps yields the same shared secret."""
        kp = mlkem_keygen()
        ct, ss_enc = mlkem_encaps(kp.public_key)
        ss_dec = mlkem_decaps(kp.secret_key, ct)
        assert ss_enc == ss_dec

    def test_different_keys_different_secrets(self) -> None:
        kp1 = mlkem_keygen()
        kp2 = mlkem_keygen()
        ct, ss_enc = mlkem_encaps(kp1.public_key)
        # Decrypting with wrong key should give different result
        ss_wrong = mlkem_decaps(kp2.secret_key, ct)
        assert ss_wrong != ss_enc

    def test_each_encaps_unique(self) -> None:
        kp = mlkem_keygen()
        cts = set()
        for _ in range(10):
            ct, _ = mlkem_encaps(kp.public_key)
            cts.add(ct)
        assert len(cts) == 10  # All encapsulations unique

    def test_bad_public_key_length(self) -> None:
        with pytest.raises(ValueError, match="public_key must be"):
            mlkem_encaps(b"short")

    def test_bad_secret_key_length(self) -> None:
        with pytest.raises(ValueError, match="secret_key must be"):
            mlkem_decaps(b"short", b"\x00" * MLKEM768_CT_SIZE)

    def test_bad_ciphertext_length(self) -> None:
        kp = mlkem_keygen()
        with pytest.raises(ValueError, match="ciphertext must be"):
            mlkem_decaps(kp.secret_key, b"short")


# ---------------------------------------------------------------------------
# ML-DSA-65
# ---------------------------------------------------------------------------


class TestMlDsa65:
    def test_keygen_sizes(self) -> None:
        kp = mldsa_keygen()
        assert len(kp.public_key) == MLDSA65_PK_SIZE
        assert len(kp.secret_key) == MLDSA65_SK_SIZE

    def test_sign_size(self) -> None:
        kp = mldsa_keygen()
        sig = mldsa_sign(kp.secret_key, b"test message")
        assert len(sig) == MLDSA65_SIG_SIZE

    def test_sign_verify_roundtrip(self) -> None:
        kp = mldsa_keygen()
        msg = b"hello post-quantum world"
        sig = mldsa_sign(kp.secret_key, msg)
        assert mldsa_verify(kp.public_key, msg, sig) is True

    def test_wrong_message_fails(self) -> None:
        kp = mldsa_keygen()
        sig = mldsa_sign(kp.secret_key, b"original")
        assert mldsa_verify(kp.public_key, b"tampered", sig) is False

    def test_wrong_public_key_fails(self) -> None:
        kp1 = mldsa_keygen()
        kp2 = mldsa_keygen()
        sig = mldsa_sign(kp1.secret_key, b"msg")
        assert mldsa_verify(kp2.public_key, b"msg", sig) is False

    def test_signatures_verify_for_repeated_message(self) -> None:
        kp = mldsa_keygen()
        sig1 = mldsa_sign(kp.secret_key, b"msg")
        sig2 = mldsa_sign(kp.secret_key, b"msg")
        # Ed25519 is deterministic, so signatures should be identical
        # But with ML-DSA the placeholder pads — verify both verify
        assert mldsa_verify(kp.public_key, b"msg", sig1)
        assert mldsa_verify(kp.public_key, b"msg", sig2)

    def test_bad_secret_key_length(self) -> None:
        with pytest.raises(ValueError, match="secret_key must be"):
            mldsa_sign(b"short", b"msg")

    def test_bad_public_key_length(self) -> None:
        with pytest.raises(ValueError, match="public_key must be"):
            mldsa_verify(b"short", b"msg", b"\x00" * MLDSA65_SIG_SIZE)

    def test_bad_signature_length(self) -> None:
        kp = mldsa_keygen()
        with pytest.raises(ValueError, match="signature must be"):
            mldsa_verify(kp.public_key, b"msg", b"short")


# ---------------------------------------------------------------------------
# Hybrid
# ---------------------------------------------------------------------------


class TestHybrid:
    def test_hybrid_sign_verify(self) -> None:
        kp = mldsa_keygen()
        sig = hybrid_sign(kp.secret_key, b"hybrid test")
        assert hybrid_verify(kp.public_key, b"hybrid test", sig) is True

    def test_hybrid_wrong_msg_fails(self) -> None:
        kp = mldsa_keygen()
        sig = hybrid_sign(kp.secret_key, b"msg")
        assert hybrid_verify(kp.public_key, b"other", sig) is False


# ---------------------------------------------------------------------------
# Backend selection
# ---------------------------------------------------------------------------


class TestBackendSelection:
    def test_default_placeholder(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Default backend is placeholder."""
        import aethermesh.common.pq_backend as pbm

        monkeypatch.delenv("AEP_PQ_BACKEND", raising=False)
        monkeypatch.setitem(pbm.__dict__, "BACKEND", "placeholder")
        assert pbm._resolve_backend() == "placeholder"
        kp = mlkem_keygen()
        assert len(kp.public_key) == MLKEM768_PK_SIZE

    def test_invalid_backend(self) -> None:
        with pytest.raises(ValueError, match="AEP_PQ_BACKEND must be"):
            import aethermesh.common.pq_backend as pbm

            old = pbm.BACKEND
            try:
                # Force invalid backend (uses object.__setattr__ on module)
                pbm.__dict__["BACKEND"] = "invalid"
                pbm._resolve_backend()
            finally:
                pbm.__dict__["BACKEND"] = old
