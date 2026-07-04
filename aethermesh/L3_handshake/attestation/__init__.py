"""L3 Attestation — hardware-backed remote attestation.

SPEC-005 § Attestation Backends.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class AttestationQuote:
    """A platform attestation quote — SPEC-005 § Attestation Backends."""

    runtime_measurement: bytes  # SHA3-256(H(model)||H(engine)||H(safety)||ver)
    config_measurement: bytes  # SHA3-256(H(prompt)||H(tools)||H(memory)||H(safety_policy))
    instance_pubkey: bytes  # hybrid PQ public key
    principal_binding: bytes  # hybrid signature over above + not_after
    not_after: int  # expiry timestamp
    freshness_nonce: bytes  # peer-provided nonce, echoed into hardware_quote
    hardware_quote: bytes  # raw TEE quote (empty for SoftSign)
    backend_code: int  # per SPEC-005 table


def discover_backends() -> list[str]:
    """Return list of available attestation backend names on this host."""
    import platform

    available = ["softsign"]
    system = platform.system()
    if system == "Linux":
        # TPM2: check if tpm2_pcrread is available
        import shutil

        if shutil.which("tpm2_pcrread"):
            available.append("tpm2")
    elif system == "Darwin":
        available.append("apple_sep")
    return available
