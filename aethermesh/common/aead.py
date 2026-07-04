"""ChaCha20-Poly1305 AEAD seal/open.

SPEC-001 § Required Behavior item 3.
"""

from cryptography.exceptions import InvalidTag


class AeadError(Exception):
    """Base class for AEAD errors."""


class AeadOpenError(AeadError, InvalidTag):
    """Tag verification failed — ciphertext is not authentic.

    Subclasses InvalidTag so callers can catch the SPEC-001 error state or the
    narrower project error.
    """


def aead_seal(key: bytes, nonce: bytes, plaintext: bytes, ad: bytes = b"") -> bytes:
    """Encrypt and authenticate *plaintext* with ChaCha20-Poly1305.

    Args:
        key: 32-byte symmetric key.
        nonce: 12-byte nonce.
        plaintext: Data to encrypt.
        ad: Optional associated data (authenticated but not encrypted).

    Returns:
        Ciphertext with 16-byte Poly1305 tag appended.

    Raises:
        ValueError: If key/nonce have wrong length.
    """
    _validate_key_nonce(key, nonce)

    from cryptography.hazmat.primitives.ciphers.aead import ChaCha20Poly1305

    chacha = ChaCha20Poly1305(key)
    return chacha.encrypt(nonce, plaintext, ad)


def aead_open(key: bytes, nonce: bytes, ciphertext: bytes, ad: bytes = b"") -> bytes:
    """Decrypt and verify *ciphertext* with ChaCha20-Poly1305.

    Args:
        key: 32-byte symmetric key.
        nonce: 12-byte nonce.
        ciphertext: Ciphertext with 16-byte Poly1305 tag appended.
        ad: Optional associated data (must match what was used in seal).

    Returns:
        Decrypted plaintext.

    Raises:
        AeadOpenError: If tag verification fails (ciphertext not authentic).
        ValueError: If key/nonce have wrong length or ciphertext too short.
    """
    _validate_key_nonce(key, nonce)

    if len(ciphertext) < 16:
        raise ValueError("ciphertext too short: must be at least 16 bytes (tag)")

    from cryptography.hazmat.primitives.ciphers.aead import ChaCha20Poly1305

    chacha = ChaCha20Poly1305(key)
    try:
        return chacha.decrypt(nonce, ciphertext, ad)
    except InvalidTag:
        raise AeadOpenError("AEAD tag verification failed") from None


def _validate_key_nonce(key: bytes, nonce: bytes) -> None:
    if len(key) != 32:
        raise ValueError(f"key must be 32 bytes, got {len(key)}")
    if len(nonce) != 12:
        raise ValueError(f"nonce must be 12 bytes, got {len(nonce)}")
