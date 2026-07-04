"""Caveat DSL — all SPEC-005 caveat types.

EP-006 M3. First-party + third-party caveats with evaluation logic.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from aethermesh.L5_captokens import Caveat


# ---------------------------------------------------------------------------
# Caveat type registry
# ---------------------------------------------------------------------------


class CaveatType(StrEnum):
    """All registered caveat type strings per SPEC-005 § Caveat DSL."""

    # First-party
    TIME_BEFORE = "time.before"
    TIME_AFTER = "time.after"
    ACTION_IN = "action.in"
    SCOPE_SUBSET = "scope.subset_of"
    BUDGET_CALLS = "budget.calls"
    BUDGET_TOKENS = "budget.tokens"
    BUDGET_WALL_MS = "budget.wall_ms"
    RATE_PER_MINUTE = "rate.per_minute"
    BOUND_TO_SESSION = "bound_to_session"
    BOUND_TO_INSTANCE = "bound_to_instance"
    BOUND_TO_ATTESTATION = "bound_to_attestation_class"
    BOUND_TO_PRINCIPAL = "bound_to_principal"
    BOUND_TO_LANE = "bound_to_lane"
    INTENT_PATH_DEPTH = "intent_path.depth_max"
    INTENT_PATH_ROOT = "intent_path.root_in"
    DEVICE_POSTURE = "device.posture_in"
    GEO_REGION = "geo.region_in"

    # Third-party
    THIRD_PARTY = "third_party"


# ---------------------------------------------------------------------------
# Caveat evaluation context
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class EvaluationContext:
    """Context provided by the L4 policy layer for caveat evaluation."""

    current_time: int = 0
    action: str = ""
    scope: tuple[str, ...] = ()
    budget_calls_remaining: int = 0
    budget_tokens_remaining: int = 0
    budget_wall_ms_elapsed: int = 0
    rate_calls_last_minute: int = 0
    session_root: bytes = b""
    instance_id: str = ""
    attestation_class: str = ""
    principal_did: str = ""
    lane: str = ""
    intent_path: tuple[str, ...] = ()
    device_posture: tuple[str, ...] = ()
    geo_region: str = ""


# ---------------------------------------------------------------------------
# Caveat evaluation
# ---------------------------------------------------------------------------


def eval_caveat(caveat: Caveat, ctx: EvaluationContext) -> bool:
    """Evaluate a single caveat against *ctx*. Returns True if satisfied.

    Unknown caveat types → fail-closed (returns False).
    """
    ct = caveat.caveat_type

    if ct == CaveatType.TIME_BEFORE:
        return _eval_time_before(caveat.value, ctx)
    if ct == CaveatType.TIME_AFTER:
        return _eval_time_after(caveat.value, ctx)
    if ct == CaveatType.ACTION_IN:
        return _eval_action_in(caveat.value, ctx)
    if ct == CaveatType.SCOPE_SUBSET:
        return _eval_scope_subset(caveat.value, ctx)
    if ct == CaveatType.BUDGET_CALLS:
        return _eval_budget_calls(caveat.value, ctx)
    if ct == CaveatType.BUDGET_TOKENS:
        return _eval_budget_tokens(caveat.value, ctx)
    if ct == CaveatType.BUDGET_WALL_MS:
        return _eval_budget_wall_ms(caveat.value, ctx)
    if ct == CaveatType.RATE_PER_MINUTE:
        return _eval_rate_per_minute(caveat.value, ctx)
    if ct == CaveatType.BOUND_TO_SESSION:
        return _eval_bound_to_session(caveat.value, ctx)
    if ct == CaveatType.BOUND_TO_INSTANCE:
        return _eval_bound_to_instance(caveat.value, ctx)
    if ct == CaveatType.BOUND_TO_ATTESTATION:
        return _eval_bound_to_attestation(caveat.value, ctx)
    if ct == CaveatType.BOUND_TO_PRINCIPAL:
        return _eval_bound_to_principal(caveat.value, ctx)
    if ct == CaveatType.BOUND_TO_LANE:
        return _eval_bound_to_lane(caveat.value, ctx)
    if ct == CaveatType.INTENT_PATH_DEPTH:
        return _eval_intent_path_depth(caveat.value, ctx)
    if ct == CaveatType.INTENT_PATH_ROOT:
        return _eval_intent_path_root(caveat.value, ctx)
    if ct == CaveatType.DEVICE_POSTURE:
        return _eval_device_posture(caveat.value, ctx)
    if ct == CaveatType.GEO_REGION:
        return _eval_geo_region(caveat.value, ctx)
    if ct == CaveatType.THIRD_PARTY:
        return _eval_third_party(caveat, ctx)

    # Unknown caveat → fail-closed per SPEC-005 § Security Rules
    return False


# ---------------------------------------------------------------------------
# First-party evaluators
# ---------------------------------------------------------------------------


def _eval_time_before(value: str, ctx: EvaluationContext) -> bool:
    """value is ISO-8601 timestamp. Succeeds if now < value."""
    import datetime

    try:
        deadline = datetime.datetime.fromisoformat(value)
        now = datetime.datetime.fromtimestamp(ctx.current_time, tz=datetime.UTC)
        return now < deadline
    except (ValueError, OSError):
        return False


def _eval_time_after(value: str, ctx: EvaluationContext) -> bool:
    """value is ISO-8601 timestamp. Succeeds if now > value."""
    import datetime

    try:
        start = datetime.datetime.fromisoformat(value)
        now = datetime.datetime.fromtimestamp(ctx.current_time, tz=datetime.UTC)
        return now > start
    except (ValueError, OSError):
        return False


def _eval_action_in(value: str, ctx: EvaluationContext) -> bool:
    """value is comma-separated allowed actions."""
    allowed = {a.strip() for a in value.split(",")}
    return ctx.action in allowed


def _eval_scope_subset(value: str, ctx: EvaluationContext) -> bool:
    """value is comma-separated allowed scopes. Request scope must be subset."""
    allowed = {s.strip() for s in value.split(",")}
    return set(ctx.scope).issubset(allowed)


def _eval_budget_calls(value: str, ctx: EvaluationContext) -> bool:
    """value is max call count."""
    try:
        return ctx.budget_calls_remaining <= int(value)
    except ValueError:
        return False


def _eval_budget_tokens(value: str, ctx: EvaluationContext) -> bool:
    try:
        return ctx.budget_tokens_remaining <= int(value)
    except ValueError:
        return False


def _eval_budget_wall_ms(value: str, ctx: EvaluationContext) -> bool:
    try:
        return ctx.budget_wall_ms_elapsed <= int(value)
    except ValueError:
        return False


def _eval_rate_per_minute(value: str, ctx: EvaluationContext) -> bool:
    try:
        return ctx.rate_calls_last_minute <= int(value)
    except ValueError:
        return False


def _eval_bound_to_session(value: str, ctx: EvaluationContext) -> bool:
    """value is hex-encoded session_root hash."""
    try:
        expected = bytes.fromhex(value)
        return ctx.session_root == expected
    except ValueError:
        return False


def _eval_bound_to_instance(value: str, ctx: EvaluationContext) -> bool:
    return ctx.instance_id == value


def _eval_bound_to_attestation(value: str, ctx: EvaluationContext) -> bool:
    """value is comma-separated acceptable attestation classes."""
    allowed = {a.strip() for a in value.split(",")}
    return ctx.attestation_class in allowed


def _eval_bound_to_principal(value: str, ctx: EvaluationContext) -> bool:
    return ctx.principal_did == value


def _eval_bound_to_lane(value: str, ctx: EvaluationContext) -> bool:
    allowed = {a.strip() for a in value.split(",")}
    return ctx.lane in allowed


def _eval_intent_path_depth(value: str, ctx: EvaluationContext) -> bool:
    try:
        return len(ctx.intent_path) <= int(value)
    except ValueError:
        return False


def _eval_intent_path_root(value: str, ctx: EvaluationContext) -> bool:
    allowed = {a.strip() for a in value.split(",")}
    return ctx.intent_path[0] in allowed if ctx.intent_path else False


def _eval_device_posture(value: str, ctx: EvaluationContext) -> bool:
    """value is comma-separated required posture classes."""
    required = {r.strip() for r in value.split(",")}
    return required.issubset(set(ctx.device_posture))


def _eval_geo_region(value: str, ctx: EvaluationContext) -> bool:
    allowed = {r.strip() for r in value.split(",")}
    return ctx.geo_region in allowed


def _eval_third_party(caveat: Caveat, ctx: EvaluationContext) -> bool:
    """Third-party caveats require a discharge."""
    # Third-party caveats always require a discharge
    # The verifier checks if a valid discharge was provided
    return caveat.discharge_required
