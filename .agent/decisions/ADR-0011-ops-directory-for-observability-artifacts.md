# ADR-0011 — Ops Directory For Observability Artifacts

- **Status:** Proposed
- **Date:** 2026-07-04
- **Owner:** Observability

## Context
EP-008 and SPEC-007 require dashboards, Prometheus alert rules, and per-role
runbooks. These artifacts are operational configuration rather than Python
source, tests, or durable project instructions, so placing them under existing
source or docs directories would blur ownership.

## Decision
Create a top-level `ops/` directory with `dashboards/`, `alerts/`, and
`runbooks/` subdirectories for observability and operations artifacts.

## Alternatives Considered
- Store under `docs/ops/` — rejected because dashboards and alert rules are
  machine-consumed operational artifacts, not only prose documentation.
- Store under `.agent/` — rejected because the artifacts are runtime/operator
  assets, not agent planning state.

## Consequences
- Positive: Keeps deployable operational artifacts in one predictable location.
- Negative: Adds one top-level directory that must be governed by this ADR.
- Neutral: Future EPs may add deployment files under `ops/` if scoped by their
  ExecPlan.

## References
- SPECs: SPEC-007 Observability
- ExecPlans: EP-008 Observability and Operations
- Prior ADRs: ADR-0009 Observability
