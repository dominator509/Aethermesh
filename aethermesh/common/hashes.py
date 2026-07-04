"""SHA3-256 hash and HKDF-SHA3-256 key derivation.

SPEC-001 § Required Behavior items 1-2.
"""

import hashlib
import hmac


def sha3_256(data: bytes) -> bytes:
    """Compute SHA3-256 digest of *data*.

    Returns 32-byte digest.
    """
    if not isinstance(data, bytes):
        raise TypeError("data must be bytes")
    return hashlib.sha3_256(data).digest()


def hkdf_sha3_256(
    ikm: bytes,
    salt: bytes = b"",
    info: bytes = b"",
    length: int = 32,
) -> bytes:
    """HKDF-SHA3-256 key derivation (RFC 5869).

    Args:
        ikm: Input keying material.
        salt: Optional salt (default empty).
        info: Optional context/domain separator.
        length: Output key length in bytes (default 32).

    Returns:
        Derived key material of *length* bytes.
    """
    if not isinstance(ikm, bytes):
        raise TypeError("ikm must be bytes")
    if not isinstance(salt, bytes):
        raise TypeError("salt must be bytes")
    if not isinstance(info, bytes):
        raise TypeError("info must be bytes")
    if length <= 0 or length > 255 * 32:
        raise ValueError(f"length must be 1..{255 * 32}")

    # HKDF-Extract: PRK = HMAC-SHA3-256(salt, IKM)
    prk = hmac.new(salt or b"\x00" * 32, ikm, hashlib.sha3_256).digest()

    # HKDF-Expand: T(n) per RFC 5869 §2.3
    okm = b""
    t = b""
    i = 1
    while len(okm) < length:
        t = hmac.new(prk, t + info + bytes([i]), hashlib.sha3_256).digest()
        okm += t
        i += 1

    return okm[:length]
