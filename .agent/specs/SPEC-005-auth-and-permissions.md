# SPEC-005 — Auth, Attestation, and Permissions

- **Status:** Draft  - **Owner:** Security  - **Phase:** 5  - **ExecPlans:** EP-006

## User-Visible Goal
Mutual remote attestation at L3 + macaroon-style authorization at L5, with hardware TEEs in production and SoftSign for development.

## Non-Goals
OAuth/OIDC bridging; federated identity providers.

## Required Behavior

### Attestation Backends (L3)
| Backend | Code | Production? |
|---|---|---|
| TPM2 | 1 | yes |
| SEV-SNP | 2 | yes |
| TDX | 3 | yes |
| Apple SEP | 4 | yes |
| Android StrongBox | 5 | yes |
| SoftSign | 10 | dev / read-class only |

`AttestationQuote` binds:
- `runtime_measurement = SHA3-256(H(model) || H(engine) || H(safety) || ver)`.
- `config_measurement = SHA3-256(H(prompt) || H(tools) || H(memory) || H(safety_policy))`.
- `instance_pubkey` (hybrid).
- `principal_binding` = hybrid sig over above + `not_after`.
- `freshness.nonce` provided by the peer, echoed into `hardware_quote.report_data`.

### Caveat DSL (L5)
First-party (locally evaluated): `time.before/after`, `action.in`, `scope.subset_of`, `budget.{calls,tokens,wall_ms}`, `rate.per_minute`, `bound_to_session/instance/attestation_class/principal/lane`, `intent_path.depth_max/root_in`, `device.posture_in`, `geo.region_in`.

Third-party: `third_party {discharger_did, discharger_pub, predicate, freshness_window, binding_nonce, audit_class}`.

Unknown caveat type → `DENY_UNKNOWN_CAVEAT` (fail-closed).

### Discharge Predicates
- `user_touch_v1 {kind, action, resource_hint?}`.
- `device_posture_v1 {requires: [str]}`.
- `anti_phish_v1 {approved_origin, approved_capability}`.
- `spending_v1 {max_usd, vendor_did}`.

### Keyring IPC
- Unix socket at `AEP_KEYRING_SOCKET`.
- Wire: length-prefixed CBOR messages.
- Requests: `discharge_request`, `mint_request`.
- Responses: `discharge_response` (signed Discharge), `mint_response` (signed CapToken root).

## Inputs / Outputs
- `RequestContext` from L4 policy layer.
- `VerificationResult` to L4 policy layer.

## Error States
`VerificationDecision` taxonomy (SPEC-006).

## Security Rules
- Verifier fails closed on every unknown caveat type and every check failure.
- Third-party caveats with an `action` predicate only trigger when the request matches.
- Discharge `binding_nonce`, `session_root`, `freshness_window` must all match.

## Required Tests
- One test per attestation backend (mocked) confirming verify path.
- One test per caveat type for pass and fail paths.
- Negative: unknown caveat → DENY_UNKNOWN_CAVEAT.
- Discharge replay across different session → DENY_DISCHARGE_INVALID.

## Acceptance Criteria
- `tests/unit/L3/attestation/` coverage ≥ 85% per backend module.
- `tests/unit/L5/verifier/` branch coverage ≥ 70%.
- Keyring IPC integration test passes against local socket.
