"""X25519 key generation and Diffie-Hellman.

SPEC-001 § Required Behavior item 4.
"""

from cryptography.hazmat.primitives.asymmetric.x25519 import (
    X25519PrivateKey,
    X25519PublicKey,
)


def x25519_keygen() -> tuple[bytes, bytes]:
    """Generate a new X25519 key pair.

    Returns:
        (secret_key, public_key) — each 32 bytes.
    """
    sk = X25519PrivateKey.generate()
    pk = sk.public_key()
    return (
        sk.private_bytes_raw(),
        pk.public_bytes_raw(),
    )


def x25519_dh(secret_key: bytes, peer_public_key: bytes) -> bytes:
    """Compute X25519 Diffie-Hellman shared secret.

    Args:
        secret_key: 32-byte X25519 private key.
        peer_public_key: 32-byte peer's X25519 public key.

    Returns:
        32-byte shared secret.

    Raises:
        ValueError: If either key has wrong length.
    """
    if len(secret_key) != 32:
        raise ValueError(f"secret_key must be 32 bytes, got {len(secret_key)}")
    if len(peer_public_key) != 32:
        raise ValueError(f"peer_public_key must be 32 bytes, got {len(peer_public_key)}")

    sk = X25519PrivateKey.from_private_bytes(secret_key)
    pk = X25519PublicKey.from_public_bytes(peer_public_key)
    return sk.exchange(pk)
