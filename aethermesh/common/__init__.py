"""Common primitives: hashes, HKDF, AEAD, PQ, X25519, canonical, DID resolver.

SPEC-001 Core Domain.
"""

from aethermesh.common.aead import AeadOpenError, aead_open, aead_seal
from aethermesh.common.canonical import canonical_bytes, canonical_from_bytes
from aethermesh.common.did_resolver import DIDResolver
from aethermesh.common.errors import (
    TRANSLATIONS,
    AbortCode,
    HandshakeAbort,
    L4WireCode,
    PolicyDecision,
    VerificationDecision,
    translate_error,
)
from aethermesh.common.hashes import hkdf_sha3_256, sha3_256
from aethermesh.common.pq_backend import (
    MLDsa65KeyPair,
    MLKem768KeyPair,
    hybrid_sign,
    hybrid_verify,
    mldsa_keygen,
    mldsa_sign,
    mldsa_verify,
    mlkem_decaps,
    mlkem_encaps,
    mlkem_keygen,
)
from aethermesh.common.x25519 import x25519_dh, x25519_keygen

__all__ = [
    # Hashes
    "sha3_256",
    "hkdf_sha3_256",
    # AEAD
    "aead_seal",
    "aead_open",
    "AeadOpenError",
    # X25519
    "x25519_keygen",
    "x25519_dh",
    # PQ backend
    "MLKem768KeyPair",
    "MLDsa65KeyPair",
    "mlkem_keygen",
    "mlkem_encaps",
    "mlkem_decaps",
    "mldsa_keygen",
    "mldsa_sign",
    "mldsa_verify",
    "hybrid_sign",
    "hybrid_verify",
    # Canonical
    "canonical_bytes",
    "canonical_from_bytes",
    # DID resolver
    "DIDResolver",
    # Errors
    "AbortCode",
    "HandshakeAbort",
    "L4WireCode",
    "PolicyDecision",
    "VerificationDecision",
    "TRANSLATIONS",
    "translate_error",
]
