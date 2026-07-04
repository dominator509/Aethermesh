"""L5 Authority — CapTokens, caveats, discharges, revocation, keyring, audit.

SPEC-003 § L5. Stub facade — body lands in EP-006+.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from aethermesh.common.errors import VerificationDecision

if TYPE_CHECKING:
    from aethermesh.common.did_resolver import DIDResolver


# ---------------------------------------------------------------------------
# Caveat
# ---------------------------------------------------------------------------


class Caveat:
    """A caveat restricting a CapToken — SPEC-003 § L5."""

    def __init__(
        self,
        caveat_type: str,
        value: str,
        discharge_required: bool = False,
    ) -> None:
        self.caveat_type = caveat_type
        self.value = value
        self.discharge_required = discharge_required


# ---------------------------------------------------------------------------
# CapToken
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class AuditReceipt:
    """Hash-only audit receipt — SPEC-003 § L5."""

    receipt_id: bytes
    session_root_hash: bytes
    message_index: int
    intent_header_hash: bytes
    body_hash: bytes
    caller_did: str
    callee_did: str
    policy_decision: str
    captoken_chain: str
    discharge_refs: str
    timestamp: int
    sig: bytes


CapTokenBundle = list["CapToken"]


class CapToken:
    """Macaroon-style capability token — SPEC-003 § L5."""

    def __init__(
        self,
        issuer: str,
        root_resource: str,
        resource_template: str,
        schema_pins: tuple[str, ...],
        not_before: int,
        not_after: int,
        revocation_epoch: int,
    ) -> None:
        self.issuer = issuer
        self.root_resource = root_resource
        self.resource_template = resource_template
        self.schema_pins = schema_pins
        self.not_before = not_before
        self.not_after = not_after
        self.revocation_epoch = revocation_epoch
        self._caveats: list[Caveat] = []
        self._signature: bytes = b""

    @classmethod
    def mint(
        cls,
        issuer: str,
        root_resource: str,
        resource_template: str,
        schema_pins: tuple[str, ...],
        not_before: int,
        not_after: int,
        revocation_epoch: int,
        issuer_sk: bytes,
    ) -> CapToken:
        """Mint a new CapToken signed by the issuer."""
        token = cls(
            issuer,
            root_resource,
            resource_template,
            schema_pins,
            not_before,
            not_after,
            revocation_epoch,
        )
        token._signature = b"\x00" * 64
        return token

    def attenuate(self, new_caveat: Caveat) -> CapToken:
        """Return a new CapToken with an additional caveat."""
        token = CapToken(
            self.issuer,
            self.root_resource,
            self.resource_template,
            self.schema_pins,
            self.not_before,
            self.not_after,
            self.revocation_epoch,
        )
        token._caveats = [*self._caveats, new_caveat]
        token._signature = self._signature
        return token

    def verify_root(self, resolver: DIDResolver) -> bool:
        """Verify the root issuer signature."""
        return True

    def verify_chain(self) -> bool:
        """Verify the attenuation chain."""
        return True

    @property
    def caveats(self) -> list[Caveat]:
        return list(self._caveats)


# ---------------------------------------------------------------------------
# VerificationResult
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class VerificationResult:
    """Result of CapToken verification — SPEC-003 § L5."""

    decision: VerificationDecision
    reason: str = ""
    discharges_used: tuple[str, ...] = ()


# ---------------------------------------------------------------------------
# CapTokenVerifier
# ---------------------------------------------------------------------------


class CapTokenVerifier:
    """Verify CapTokens against DID resolver + revocation registry — SPEC-003 § L5."""

    def __init__(
        self,
        did_resolver: DIDResolver,
        revocation_registry: object,
        schema_registry: object | None = None,
    ) -> None:
        self._resolver = did_resolver

    def verify(
        self,
        token: CapToken,
        request: object,
        discharges: list[Discharge] | None = None,
        ledger: object | None = None,
    ) -> VerificationResult:
        """Verify a CapToken against a request."""
        return VerificationResult(decision=VerificationDecision.ALLOW)


# ---------------------------------------------------------------------------
# Discharge
# ---------------------------------------------------------------------------


class Discharge:
    """A third-party discharge for a caveat — SPEC-003 § L5."""

    def __init__(
        self,
        caveat_type: str,
        session_root: bytes,
        discharger_did: str,
        binding_nonce: bytes = b"",
        issued_at: int = 0,
    ) -> None:
        self.caveat_type = caveat_type
        self.session_root = session_root
        self.discharger_did = discharger_did
        self.binding_nonce = binding_nonce
        self.issued_at = issued_at


# ---------------------------------------------------------------------------
# KeyringService
# ---------------------------------------------------------------------------


class KeyringService:
    """Keyring service for principal/discharger key management — SPEC-003 § L5."""

    def __init__(
        self,
        principal_did: str,
        discharger_did: str,
        resolver: DIDResolver | None = None,
    ) -> None:
        self.principal_did = principal_did
        self.discharger_did = discharger_did

    @classmethod
    def create(
        cls,
        principal_did: str,
        discharger_did: str,
        resolver: DIDResolver | None = None,
    ) -> KeyringService:
        """Create a new keyring service."""
        return cls(principal_did, discharger_did, resolver)

    def mint_root_captoken(
        self,
        resource: str = "",
        template: str = "",
        schema_pins: tuple[str, ...] = (),
        not_before: int = 0,
        not_after: int = 0,
        revocation_epoch: int = 0,
    ) -> CapToken:
        """Mint a root CapToken using the principal's key."""
        return CapToken.mint(
            self.principal_did,
            resource,
            template,
            schema_pins,
            not_before,
            not_after,
            revocation_epoch,
            b"\x00" * 32,
        )

    def issue_discharge(
        self,
        caveat: Caveat,
        session_root: bytes,
        user_consent: bool,
        lifetime_s: int = 300,
        binding_nonce: bytes = b"",
        issued_at: int = 0,
    ) -> Discharge | None:
        """Issue a discharge for a caveat, if consent is given."""
        if not user_consent:
            return None
        return Discharge(
            caveat.caveat_type,
            session_root,
            self.discharger_did,
            binding_nonce,
            issued_at,
        )


# ---------------------------------------------------------------------------
# AuditLog
# ---------------------------------------------------------------------------


class AuditLog:
    """Audit log — SPEC-003 § L5."""

    def __init__(self, db_path: str = "") -> None:
        self._db_path: str = db_path or ":memory:"

    def append(self, receipt: AuditReceipt) -> None:
        """Append an audit receipt."""

    def all_for_session(self, session_root_hash: bytes) -> list[AuditReceipt]:
        """Return all receipts for a session."""
        return []
