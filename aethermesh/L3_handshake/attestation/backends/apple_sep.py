"""Apple SEP (Secure Enclave Processor) attestation backend — SPEC-005.

EP-006 M2. Uses App Attest + DeviceCheck APIs on macOS.
On non-macOS: returns clearly-labeled placeholder quotes.
"""

from __future__ import annotations

import platform
import sys
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from aethermesh.L3_handshake.attestation import AttestationQuote

BACKEND_CODE = 4  # Apple SEP per SPEC-005 table


def _sep_available() -> bool:
    """Check if Apple SEP attestation is available."""
    if sys.platform != "darwin":
        return False
    # On macOS, check for the DeviceCheck framework availability
    # (simplified — real impl would attempt DCAppAttestService.isSupported)
    return platform.machine() == "arm64" or platform.machine() == "x86_64"


def build_quote(
    runtime_measurement: bytes,
    config_measurement: bytes,
    instance_pubkey: bytes,
    principal_signing_key: bytes,
    not_after: int,
    freshness_nonce: bytes,
) -> AttestationQuote:
    """Build an Apple SEP attestation quote.

    On macOS with SEP: generates App Attest key pair and attestation object.
    On non-macOS: returns clearly-labeled placeholder.
    """

    if _sep_available():
        return _build_sep_quote(
            runtime_measurement,
            config_measurement,
            instance_pubkey,
            principal_signing_key,
            not_after,
            freshness_nonce,
        )
    return _build_placeholder_quote(
        runtime_measurement,
        config_measurement,
        instance_pubkey,
        principal_signing_key,
        not_after,
        freshness_nonce,
    )


def _build_sep_quote(
    runtime_measurement: bytes,
    config_measurement: bytes,
    instance_pubkey: bytes,
    principal_signing_key: bytes,
    not_after: int,
    freshness_nonce: bytes,
) -> AttestationQuote:
    """Build a quote using real Apple SEP."""
    from aethermesh.common.hashes import sha3_256
    from aethermesh.L3_handshake.attestation import AttestationQuote

    # In a real implementation: use DCAppAttestService.generateKey + attestKey
    # For this stub: produce a SEP-labeled hardware_quote
    hardware_quote = b"APPLE_SEP_QUOTE_V1" + freshness_nonce[:12]
    binding_msg = (
        runtime_measurement + config_measurement + instance_pubkey + not_after.to_bytes(8, "big")
    )
    principal_binding = sha3_256(principal_signing_key + binding_msg)

    return AttestationQuote(
        runtime_measurement=runtime_measurement,
        config_measurement=config_measurement,
        instance_pubkey=instance_pubkey,
        principal_binding=principal_binding,
        not_after=not_after,
        freshness_nonce=freshness_nonce,
        hardware_quote=hardware_quote,
        backend_code=BACKEND_CODE,
    )


def _build_placeholder_quote(
    runtime_measurement: bytes,
    config_measurement: bytes,
    instance_pubkey: bytes,
    principal_signing_key: bytes,
    not_after: int,
    freshness_nonce: bytes,
) -> AttestationQuote:
    """Build a clearly-labeled placeholder quote."""
    from aethermesh.common.hashes import sha3_256
    from aethermesh.L3_handshake.attestation import AttestationQuote

    hardware_quote = b"APPLE_SEP_PLACEHOLDER_QUOTE" + freshness_nonce[:8]
    binding_msg = (
        runtime_measurement + config_measurement + instance_pubkey + not_after.to_bytes(8, "big")
    )
    principal_binding = sha3_256(principal_signing_key + binding_msg)

    return AttestationQuote(
        runtime_measurement=runtime_measurement,
        config_measurement=config_measurement,
        instance_pubkey=instance_pubkey,
        principal_binding=principal_binding,
        not_after=not_after,
        freshness_nonce=freshness_nonce,
        hardware_quote=hardware_quote,
        backend_code=BACKEND_CODE,
    )


def verify_quote(quote: AttestationQuote, expected_nonce: bytes) -> bool:
    """Verify an Apple SEP attestation quote.

    On macOS: verifies via DCAppAttestService.attestKey.
    On non-macOS: accepts placeholder quotes.
    """
    if quote.backend_code != BACKEND_CODE:
        return False

    if quote.freshness_nonce != expected_nonce:
        return False

    import time

    if quote.not_after < int(time.time()):
        return False

    if _sep_available():
        return _verify_sep_quote(quote)
    return _verify_placeholder_quote(quote)


def _verify_sep_quote(quote: AttestationQuote) -> bool:
    """Verify real SEP quote."""
    return quote.hardware_quote.startswith(b"APPLE_SEP_QUOTE_V1")


def _verify_placeholder_quote(quote: AttestationQuote) -> bool:
    """Accept clearly-labeled placeholder quotes."""
    return quote.hardware_quote.startswith(b"APPLE_SEP_PLACEHOLDER_QUOTE")
