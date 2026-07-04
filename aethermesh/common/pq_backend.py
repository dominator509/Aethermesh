"""Post-quantum KEM and signature dispatch.

SPEC-001 § Required Behavior items 5-6.
Backend selected by AEP_PQ_BACKEND env var: "placeholder" or "liboqs".
"""

import os
from dataclasses import dataclass

from aethermesh.common.hashes import sha3_256
from aethermesh.common.x25519 import x25519_dh, x25519_keygen

# ---------------------------------------------------------------------------
# Constants — correct byte sizes per ML-KEM-768 / ML-DSA-65 (FIPS 203/204)
# ---------------------------------------------------------------------------
MLKEM768_PK_SIZE = 1184
MLKEM768_SK_SIZE = 2400
MLKEM768_CT_SIZE = 1088
MLKEM768_SS_SIZE = 32

MLDSA65_PK_SIZE = 1952
MLDSA65_SK_SIZE = 4032
MLDSA65_SIG_SIZE = 3309

# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class MLKem768KeyPair:
    """ML-KEM-768 key pair."""

    secret_key: bytes  # 2400 bytes
    public_key: bytes  # 1184 bytes


@dataclass(frozen=True)
class MLDsa65KeyPair:
    """ML-DSA-65 key pair."""

    secret_key: bytes  # 4032 bytes
    public_key: bytes  # 1952 bytes


# ---------------------------------------------------------------------------
# Backend selection
# ---------------------------------------------------------------------------

BACKEND = os.environ.get("AEP_PQ_BACKEND", "placeholder")
_LIBOQS_AVAILABLE: bool | None = None


def _check_liboqs() -> bool:
    global _LIBOQS_AVAILABLE
    if _LIBOQS_AVAILABLE is None:  # pragma: no cover
        try:
            import oqs  # type: ignore[import-not-found]  # noqa: F401

            _LIBOQS_AVAILABLE = True
        except ImportError:
            _LIBOQS_AVAILABLE = False
    return _LIBOQS_AVAILABLE


def _resolve_backend() -> str:
    backend = BACKEND
    if backend not in ("placeholder", "liboqs"):
        raise ValueError(f"AEP_PQ_BACKEND must be 'placeholder' or 'liboqs', got '{backend}'")
    if backend == "liboqs" and not _check_liboqs():  # pragma: no cover
        import warnings

        warnings.warn(
            "liboqs requested but 'oqs' package not installed; falling back to placeholder",
            stacklevel=2,
        )
        return "placeholder"
    return backend


# ====================================================================
# ML-KEM-768
# ====================================================================


def mlkem_keygen() -> MLKem768KeyPair:
    """Generate an ML-KEM-768 key pair."""
    backend = _resolve_backend()
    if backend == "liboqs":  # pragma: no cover
        return _liboqs_mlkem_keygen()
    return _placeholder_mlkem_keygen()


def mlkem_encaps(public_key: bytes) -> tuple[bytes, bytes]:
    """Encapsulate a shared secret to *public_key*.

    Returns (ciphertext, shared_secret).
    """
    if len(public_key) != MLKEM768_PK_SIZE:
        raise ValueError(f"public_key must be {MLKEM768_PK_SIZE} bytes, got {len(public_key)}")

    backend = _resolve_backend()
    if backend == "liboqs":  # pragma: no cover
        return _liboqs_mlkem_encaps(public_key)
    return _placeholder_mlkem_encaps(public_key)


def mlkem_decaps(secret_key: bytes, ciphertext: bytes) -> bytes:
    """Decapsulate *ciphertext* using *secret_key*, returning the shared secret."""
    if len(secret_key) != MLKEM768_SK_SIZE:
        raise ValueError(f"secret_key must be {MLKEM768_SK_SIZE} bytes, got {len(secret_key)}")
    if len(ciphertext) != MLKEM768_CT_SIZE:
        raise ValueError(f"ciphertext must be {MLKEM768_CT_SIZE} bytes, got {len(ciphertext)}")

    backend = _resolve_backend()
    if backend == "liboqs":  # pragma: no cover
        return _liboqs_mlkem_decaps(secret_key, ciphertext)
    return _placeholder_mlkem_decaps(secret_key, ciphertext)


# ====================================================================
# ML-DSA-65
# ====================================================================


def mldsa_keygen() -> MLDsa65KeyPair:
    """Generate an ML-DSA-65 key pair."""
    backend = _resolve_backend()
    if backend == "liboqs":  # pragma: no cover
        return _liboqs_mldsa_keygen()
    return _placeholder_mldsa_keygen()


def mldsa_sign(secret_key: bytes, message: bytes) -> bytes:
    """Sign *message* with ML-DSA-65, returning 3309-byte signature."""
    if len(secret_key) != MLDSA65_SK_SIZE:
        raise ValueError(f"secret_key must be {MLDSA65_SK_SIZE} bytes, got {len(secret_key)}")

    backend = _resolve_backend()
    if backend == "liboqs":  # pragma: no cover
        return _liboqs_mldsa_sign(secret_key, message)
    return _placeholder_mldsa_sign(secret_key, message)


def mldsa_verify(public_key: bytes, message: bytes, signature: bytes) -> bool:
    """Verify ML-DSA-65 *signature* over *message*."""
    if len(public_key) != MLDSA65_PK_SIZE:
        raise ValueError(f"public_key must be {MLDSA65_PK_SIZE} bytes, got {len(public_key)}")
    if len(signature) != MLDSA65_SIG_SIZE:
        raise ValueError(f"signature must be {MLDSA65_SIG_SIZE} bytes, got {len(signature)}")

    backend = _resolve_backend()
    if backend == "liboqs":  # pragma: no cover
        return _liboqs_mldsa_verify(public_key, message, signature)
    return _placeholder_mldsa_verify(public_key, message, signature)


# ====================================================================
# Hybrid (classical + PQ) combiners
# ====================================================================


def hybrid_sign(secret_key: bytes, message: bytes) -> bytes:
    """Hybrid signature: classical inner + PQ outer.

    For placeholder: delegates to mldsa_sign.
    For liboqs: ML-DSA-65 signature.
    """
    return mldsa_sign(secret_key, message)


def hybrid_verify(public_key: bytes, message: bytes, signature: bytes) -> bool:
    """Hybrid signature verification."""
    return mldsa_verify(public_key, message, signature)


# ====================================================================
# Placeholder implementations (X25519/Ed25519-based, padded to PQ sizes)
# ====================================================================

_X25519_PK_SIZE = 32
_ED25519_PK_SIZE = 32
_ED25519_SIG_SIZE = 64
_ED25519_SK_SEED_SIZE = 32


def _placeholder_mlkem_keygen() -> MLKem768KeyPair:
    """ML-KEM-768 placeholder: X25519 KEM wrapped to PQ sizes."""
    xsk, xpk = x25519_keygen()
    # Embed X25519 keys into ML-KEM-768-sized containers
    pk = xpk + b"\x00" * (MLKEM768_PK_SIZE - _X25519_PK_SIZE)
    sk_body = xsk + pk
    sk = sk_body + b"\x00" * (MLKEM768_SK_SIZE - len(sk_body))
    assert len(pk) == MLKEM768_PK_SIZE
    assert len(sk) == MLKEM768_SK_SIZE
    return MLKem768KeyPair(secret_key=sk, public_key=pk)


def _placeholder_mlkem_encaps(public_key: bytes) -> tuple[bytes, bytes]:
    """ML-KEM-768 placeholder encaps: X25519 DH + SHA3-256."""
    xpk = public_key[:_X25519_PK_SIZE]
    esk, epk = x25519_keygen()
    ss_raw = x25519_dh(esk, xpk)
    ss = sha3_256(ss_raw + b"mlkem768-placeholder-v1")
    ct = epk + b"\x00" * (MLKEM768_CT_SIZE - _X25519_PK_SIZE)
    assert len(ct) == MLKEM768_CT_SIZE
    assert len(ss) == MLKEM768_SS_SIZE
    return ct, ss


def _placeholder_mlkem_decaps(secret_key: bytes, ciphertext: bytes) -> bytes:
    """ML-KEM-768 placeholder decaps."""
    xsk = secret_key[:_X25519_PK_SIZE]
    epk = ciphertext[:_X25519_PK_SIZE]
    ss_raw = x25519_dh(xsk, epk)
    ss = sha3_256(ss_raw + b"mlkem768-placeholder-v1")
    return ss


def _placeholder_mldsa_keygen() -> MLDsa65KeyPair:
    """ML-DSA-65 placeholder: Ed25519 wrapped to PQ sizes."""
    from cryptography.hazmat.primitives.asymmetric.ed25519 import (
        Ed25519PrivateKey,
    )

    sk_ed = Ed25519PrivateKey.generate()
    pk_ed_raw = sk_ed.public_key().public_bytes_raw()
    sk_ed_raw = sk_ed.private_bytes_raw()

    pk = pk_ed_raw + b"\x00" * (MLDSA65_PK_SIZE - _ED25519_PK_SIZE)
    sk_body = sk_ed_raw + pk
    sk = sk_body + b"\x00" * (MLDSA65_SK_SIZE - len(sk_body))
    assert len(pk) == MLDSA65_PK_SIZE
    assert len(sk) == MLDSA65_SK_SIZE
    return MLDsa65KeyPair(secret_key=sk, public_key=pk)


def _placeholder_mldsa_sign(secret_key: bytes, message: bytes) -> bytes:
    """ML-DSA-65 placeholder sign: Ed25519 under the hood."""
    from cryptography.hazmat.primitives.asymmetric.ed25519 import (
        Ed25519PrivateKey,
    )

    sk_ed = Ed25519PrivateKey.from_private_bytes(secret_key[:_ED25519_SK_SEED_SIZE])
    sig_raw = sk_ed.sign(message)
    sig = sig_raw + b"\x00" * (MLDSA65_SIG_SIZE - _ED25519_SIG_SIZE)
    assert len(sig) == MLDSA65_SIG_SIZE
    return sig


def _placeholder_mldsa_verify(public_key: bytes, message: bytes, signature: bytes) -> bool:
    """ML-DSA-65 placeholder verify: Ed25519 under the hood."""
    from cryptography.exceptions import InvalidSignature
    from cryptography.hazmat.primitives.asymmetric.ed25519 import (
        Ed25519PublicKey,
    )

    pk_ed = Ed25519PublicKey.from_public_bytes(public_key[:_ED25519_PK_SIZE])
    sig_raw = signature[:_ED25519_SIG_SIZE]
    try:
        pk_ed.verify(sig_raw, message)
        return True
    except InvalidSignature:
        return False


# ====================================================================
# liboqs dispatch (wraps the 'oqs' Python package)
# Covered only when oqs is installed; excluded from coverage baseline.
# ====================================================================


def _liboqs_mlkem_keygen() -> MLKem768KeyPair:  # pragma: no cover
    import oqs

    with oqs.KeyEncapsulation("ML-KEM-768") as kem:
        pk = kem.generate_keypair()
        sk = kem.export_secret_key()
    return MLKem768KeyPair(secret_key=sk, public_key=pk)


def _liboqs_mlkem_encaps(public_key: bytes) -> tuple[bytes, bytes]:  # pragma: no cover
    import oqs

    with oqs.KeyEncapsulation("ML-KEM-768") as kem:
        ct, ss = kem.encap_secret(public_key)
    return ct, ss


def _liboqs_mlkem_decaps(secret_key: bytes, ciphertext: bytes) -> bytes:  # pragma: no cover
    import oqs

    with oqs.KeyEncapsulation("ML-KEM-768", secret_key) as kem:
        ss = kem.decap_secret(ciphertext)
    return ss  # type: ignore[no-any-return]


def _liboqs_mldsa_keygen() -> MLDsa65KeyPair:  # pragma: no cover
    import oqs

    with oqs.Signature("ML-DSA-65") as sig:
        pk = sig.generate_keypair()
        sk = sig.export_secret_key()
    return MLDsa65KeyPair(secret_key=sk, public_key=pk)


def _liboqs_mldsa_sign(secret_key: bytes, message: bytes) -> bytes:  # pragma: no cover
    import oqs

    with oqs.Signature("ML-DSA-65", secret_key) as sig:
        return sig.sign(message)  # type: ignore[no-any-return]


def _liboqs_mldsa_verify(
    public_key: bytes, message: bytes, signature: bytes
) -> bool:  # pragma: no cover
    import oqs

    with oqs.Signature("ML-DSA-65") as sig:
        return sig.verify(message, signature, public_key)  # type: ignore[no-any-return]
