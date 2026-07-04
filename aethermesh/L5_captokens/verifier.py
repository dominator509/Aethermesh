"""CapToken verifier — evaluates caveat chains against requests.

SPEC-005 § Caveat DSL + Security Rules. EP-006 M4.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from aethermesh.common.errors import VerificationDecision
from aethermesh.L5_captokens.caveats import CaveatType, EvaluationContext, eval_caveat

if TYPE_CHECKING:
    from aethermesh.common.did_resolver import DIDResolver
    from aethermesh.L5_captokens import CapToken, Caveat, Discharge


def verify_token(
    token: CapToken,
    request: object,
    resolver: DIDResolver,
    discharges: list[Discharge] | None = None,
) -> tuple[VerificationDecision, str]:
    """Verify a CapToken against a request context.

    Checks:
    1. Root issuer signature (via DID resolver)
    2. Attenuation chain integrity
    3. Every caveat against the request context
    4. Required discharges are present and valid

    Returns (decision, reason).
    """
    discharges = discharges or []

    # 1. Verify root issuer
    if not token.verify_root(resolver):
        return VerificationDecision.DENY_ISSUER_SIG, "root issuer signature invalid"

    # 2. Verify chain
    if not token.verify_chain():
        return VerificationDecision.DENY_CHAIN, "attenuation chain verification failed"

    # 3. Build evaluation context from request
    ctx = _build_context(request, token)

    # 4. Evaluate every caveat (fail-closed on first denial)
    for caveat in token.caveats:
        if caveat.caveat_type == CaveatType.THIRD_PARTY and not _third_party_applies(caveat, ctx):
            continue

        if caveat.discharge_required:
            discharge_decision = _discharge_decision(caveat, discharges, ctx)
            if discharge_decision is not None:
                return discharge_decision

        if not eval_caveat(caveat, ctx):
            decision = _caveat_denial_code(caveat.caveat_type)
            return decision, f"caveat '{caveat.caveat_type}' not satisfied (value={caveat.value})"

    return VerificationDecision.ALLOW, "all caveats satisfied"


def _build_context(request: object, token: CapToken) -> EvaluationContext:
    """Build an EvaluationContext from a request object.

    Accepts dict or IntentHeader-like objects.
    """
    import time

    if isinstance(request, dict):
        return EvaluationContext(
            current_time=int(request.get("current_time", time.time())),
            action=request.get("action", ""),
            scope=tuple(request.get("scope", ())),
            session_root=request.get("session_root", b""),
            principal_did=request.get("caller_did", ""),
            lane=request.get("lane", "fast"),
            intent_path=tuple(request.get("intent_path", ())),
            budget_calls_remaining=request.get("budget_calls_remaining", 0),
            budget_tokens_remaining=request.get("budget_tokens_remaining", 0),
            budget_wall_ms_elapsed=request.get("budget_wall_ms_elapsed", 0),
            rate_calls_last_minute=request.get("rate_calls_last_minute", 0),
            device_posture=tuple(request.get("device_posture", ())),
            geo_region=request.get("geo_region", ""),
        )

    # IntentHeader-like
    return EvaluationContext(
        current_time=int(time.time()),
        action=getattr(request, "action", ""),
        scope=tuple(getattr(request, "scope", ())),
        session_root=getattr(request, "session_root", b""),
        principal_did=getattr(request, "caller_did", ""),
        lane=getattr(request, "lane", "fast"),
        intent_path=tuple(getattr(request, "intent_path", ())),
        budget_calls_remaining=getattr(request, "budget", 0),
    )


def _third_party_applies(caveat: Caveat, ctx: EvaluationContext) -> bool:
    """Return whether a third-party caveat applies to this request."""
    attrs = _parse_third_party_value(caveat.value)
    action_predicate = attrs.get("action") or attrs.get("action.in")
    if not action_predicate:
        return True
    allowed = {action.strip() for action in action_predicate.split(",") if action.strip()}
    return ctx.action in allowed


def _discharge_decision(
    caveat: Caveat,
    discharges: list[Discharge],
    ctx: EvaluationContext,
) -> tuple[VerificationDecision, str] | None:
    """Return a denial for missing/invalid discharges, or None when valid."""
    saw_candidate = False
    for discharge in discharges:
        if discharge.caveat_type != caveat.caveat_type:
            continue
        saw_candidate = True
        if _discharge_matches(caveat, discharge, ctx):
            return None

    if not saw_candidate:
        return (
            VerificationDecision.PENDING_DISCHARGE,
            f"missing discharge for caveat '{caveat.caveat_type}'",
        )
    return (
        VerificationDecision.DENY_DISCHARGE_INVALID,
        f"invalid discharge for caveat '{caveat.caveat_type}'",
    )


def _discharge_matches(caveat: Caveat, discharge: Discharge, ctx: EvaluationContext) -> bool:
    """Validate SPEC-005 discharge binding fields against the request context."""
    attrs = _parse_third_party_value(caveat.value)

    expected_did = attrs.get("discharger_did")
    if expected_did and discharge.discharger_did != expected_did:
        return False

    if discharge.session_root != ctx.session_root:
        return False

    expected_nonce_hex = attrs.get("binding_nonce")
    if expected_nonce_hex:
        try:
            expected_nonce = bytes.fromhex(expected_nonce_hex)
        except ValueError:
            return False
        if discharge.binding_nonce != expected_nonce:
            return False

    freshness_window = attrs.get("freshness_window")
    if freshness_window:
        try:
            max_age = int(freshness_window)
        except ValueError:
            return False
        age = ctx.current_time - discharge.issued_at
        if discharge.issued_at <= 0 or age < 0 or age > max_age:
            return False

    return True


def _parse_third_party_value(value: str) -> dict[str, str]:
    """Parse a compact third-party caveat value into key/value fields."""
    if "=" not in value:
        return {"discharger_did": value} if value else {}

    attrs: dict[str, str] = {}
    for part in value.split(";"):
        key, sep, raw_value = part.partition("=")
        if not sep:
            continue
        key = key.strip()
        if key:
            attrs[key] = raw_value.strip()
    return attrs


def _caveat_denial_code(caveat_type: str) -> VerificationDecision:
    """Map caveat type to the closest VerificationDecision."""
    mapping = {
        CaveatType.TIME_BEFORE: VerificationDecision.DENY_TIME,
        CaveatType.TIME_AFTER: VerificationDecision.DENY_TIME,
        CaveatType.ACTION_IN: VerificationDecision.DENY_ACTION,
        CaveatType.SCOPE_SUBSET: VerificationDecision.DENY_SCOPE,
        CaveatType.BUDGET_CALLS: VerificationDecision.DENY_BUDGET,
        CaveatType.BUDGET_TOKENS: VerificationDecision.DENY_BUDGET,
        CaveatType.BUDGET_WALL_MS: VerificationDecision.DENY_BUDGET,
        CaveatType.RATE_PER_MINUTE: VerificationDecision.DENY_RATE,
        CaveatType.BOUND_TO_SESSION: VerificationDecision.DENY_SESSION_BINDING,
        CaveatType.BOUND_TO_INSTANCE: VerificationDecision.DENY_INSTANCE_BINDING,
        CaveatType.BOUND_TO_ATTESTATION: VerificationDecision.DENY_ATTESTATION_BINDING,
        CaveatType.BOUND_TO_PRINCIPAL: VerificationDecision.DENY_PRINCIPAL_BINDING,
        CaveatType.BOUND_TO_LANE: VerificationDecision.DENY_LANE,
        CaveatType.INTENT_PATH_DEPTH: VerificationDecision.DENY_INTENT_PATH,
        CaveatType.INTENT_PATH_ROOT: VerificationDecision.DENY_INTENT_PATH,
        CaveatType.DEVICE_POSTURE: VerificationDecision.DENY_POSTURE,
        CaveatType.GEO_REGION: VerificationDecision.DENY_GEO,
        CaveatType.THIRD_PARTY: VerificationDecision.PENDING_DISCHARGE,
    }
    return mapping.get(caveat_type, VerificationDecision.DENY_UNKNOWN_CAVEAT)  # type: ignore[no-any-return, call-overload]
