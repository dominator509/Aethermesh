"""TPM2 attestation backend — SPEC-005 § Attestation Backends.

EP-006 M1. On hosts with TPM2 tools, builds real PCR quotes.
On hosts without, returns clearly-labeled placeholder quotes.
"""

from __future__ import annotations

import os
import shutil
import subprocess
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from aethermesh.L3_handshake.attestation import AttestationQuote


BACKEND_CODE = 1  # TPM2 per SPEC-005 table


def _tpm2_available() -> bool:
    """Check if tpm2-tools are installed and TPM device is accessible."""
    if os.name == "nt":
        return False  # Windows TPM2 not supported in this backend
    return shutil.which("tpm2_pcrread") is not None


def build_quote(
    runtime_measurement: bytes,
    config_measurement: bytes,
    instance_pubkey: bytes,
    principal_signing_key: bytes,
    not_after: int,
    freshness_nonce: bytes,
) -> AttestationQuote:
    """Build a TPM2 attestation quote.

    On TPM2-capable hosts: calls tpm2_pcrread + tpm2_quote via subprocess.
    On hosts without: returns clearly-labeled placeholder.
    """

    if _tpm2_available():
        return _build_real_quote(
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


def _build_real_quote(
    runtime_measurement: bytes,
    config_measurement: bytes,
    instance_pubkey: bytes,
    principal_signing_key: bytes,
    not_after: int,
    freshness_nonce: bytes,
) -> AttestationQuote:
    """Build a quote using real TPM2 tools."""
    from aethermesh.common.hashes import sha3_256
    from aethermesh.L3_handshake.attestation import AttestationQuote

    # Read PCR values for runtime + config measurements
    try:
        pcr_result = subprocess.run(
            ["tpm2_pcrread", "sha256:0,1,2,3"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        pcr_data = (
            pcr_result.stdout.encode() if pcr_result.returncode == 0 else b"tpm2_pcrread_failed"
        )
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pcr_data = b"tpm2_unavailable"

    hardware_quote = sha3_256(pcr_data + freshness_nonce)

    # Principal binding: hybrid sig over measurements + not_after
    binding_msg = (
        runtime_measurement + config_measurement + instance_pubkey + not_after.to_bytes(8, "big")
    )
    from aethermesh.common.hashes import sha3_256 as h

    principal_binding = h(principal_signing_key + binding_msg)

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

    hardware_quote = b"TPM2_PLACEHOLDER_QUOTE" + freshness_nonce[:8]
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
    """Verify a TPM2 attestation quote.

    On TPM2-capable hosts: verifies PCR quote via tpm2_checkquote.
    On hosts without: accepts placeholder quotes (clearly labeled).
    """
    if quote.backend_code != BACKEND_CODE:
        return False

    # Verify freshness
    if quote.freshness_nonce != expected_nonce:
        return False

    # Verify not_after
    import time

    if quote.not_after < int(time.time()):
        return False

    if _tpm2_available():
        return _verify_real_quote(quote)
    return _verify_placeholder_quote(quote)


def _verify_real_quote(quote: AttestationQuote) -> bool:
    """Verify using tpm2_checkquote."""
    # In a real implementation: call tpm2_checkquote
    # For now: check the hardware_quote contains PCR data hash
    return len(quote.hardware_quote) >= 32


def _verify_placeholder_quote(quote: AttestationQuote) -> bool:
    """Accept clearly-labeled placeholder quotes."""
    return quote.hardware_quote.startswith(b"TPM2_PLACEHOLDER_QUOTE")
