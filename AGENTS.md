# AGENTS.md — Control Plane for Coding Agents

@C:\Users\domin\.codex\RTK.md

Read this entire file before editing anything.

Durable repo context for Serena, Codex, and Obsidian lives in `REPO_BRIEF.md`. Keep it compact and update it when the repository shape or command surface changes.

## 1. Mission
Promote the AetherMesh / AEP reference implementation (5 layers: L1 Sphinx mixnet, L2 capability-hashed DHT, L3 Noise-PQ XK + mutual attestation, L4 PQ Double Ratchet + MLS, L5 macaroon-style CapTokens) to a production-ready 1.0. Replace PQ placeholders with liboqs, achieve two-implementation interop, and pass every gate in `PRODUCTION_READINESS.md`.

## 2. Source-of-Truth Priority
On conflict, this strict order:
1. Current user instruction.
2. `AGENTS.md` (this file).
3. The active ExecPlan (`.agent/execplans/EP-XXX-*.md`).
4. Existing repository code and tests.
5. `ARCHITECTURE.md`.
6. The relevant SPEC.
7. `ROADMAP.md` (strategic only — never implement directly from it).

## 3. Required Workflow
1. Read `AGENTS.md`, `COMMANDS.md`, and the active ExecPlan in full.
2. Run `./scripts/preflight.sh` → confirm `preflight: ok`.
3. Complete milestones in numeric order.
4. After every milestone: run its validation command, confirm the expected result, tick the Progress checkbox, update Surprises & Discoveries / Decision Log if relevant.
5. Continue autonomously to the next milestone unless a STOP condition applies.
6. After the final milestone: run `./scripts/verify.sh` and follow `.agent/prompts/final-review.md`.

**Do not ask the user for next steps. Proceed autonomously through the active ExecPlan unless a STOP condition applies.**

## 4. STOP Conditions
- A required secret, credential, paid service, or external account is missing (liboqs unavailable, GHA permission missing, TEE missing when the ExecPlan mandates one).
- An action may destroy user data, audit logs, production keys, or the published transparency log.
- A legal / security / financial judgement is required that no SPEC resolves (e.g., adopting a new platform attestation root, accepting a CVE).
- A user-visible behavior change is required that no SPEC authorizes (e.g., changing the constant-rate cover-traffic budget).
- Required tests cannot run after the documented anti-fixation recovery steps were attempted.
- A production deployment, irreversible migration, RevocationManifest publication, or `AEP_PQ_BACKEND` change without explicit permission in the current user instruction.

## 5. Anti-Drift Rules
- Implement only the active ExecPlan's Scope.
- No broad refactors, dependency swaps, file reorganizations, or stylistic rewrites unless the ExecPlan mandates them.
- Run `git diff --name-only` after every milestone; reconcile against "Files to Change."
- No second ExecPlan until the active one's Outcomes & Retrospective is filled.

## 6. Anti-Hallucination Rules
- Do not invent package APIs — open the source.
- Do not invent command names — use `COMMANDS.md`; update it first with evidence if a needed command is missing.
- Do not invent environment variables — they must appear in `ENVIRONMENT.md` first.
- Do not invent CapToken caveat type codes, abort codes, or schema ids. Read `aethermesh.L5_captokens.caveat_types`, `aethermesh.L3_handshake.aborts`, and the relevant SPEC.
- Do not invent DIDs — use only `did:web:example.org`, `did:web:peer.example`, `did:web:org.example`, `did:key:z6Mk-...`.
- Confirm every imported name by reading the file you are importing from.
- Record every assumption in the active ExecPlan's Decision Log.

## 7. Anti-Fixation Rules
For any failing validation command:
1. **First failure:** read the exact error, smallest targeted fix, rerun.
2. **Second same-root failure:** narrower diagnostic (`pytest -k`, `mypy <file>`); isolate, do not broaden.
3. **Third same-root failure:** stop this approach; record failed hypotheses in `Surprises & Discoveries`; pick a simpler path consistent with the SPEC.

If three same-root failures and no simpler path exists, this is a STOP condition.

## 8. Dependency Rules
- Before adding any dependency: check `pyproject.toml`; check if stdlib or existing deps suffice; prefer a present dep; record in Decision Log.
- No transitive crypto deps without ADR. Crypto = `cryptography`, `oqs` (liboqs), `hashlib` / `hmac` only.
- No pre-release pins.
- Update `ENVIRONMENT.md` and `pyproject.toml` together.

## 9. File Creation Rules
- New source files: `aethermesh/<layer>/`; tests: `tests/<scope>/`.
- New top-level directories require an ADR.
- Every new public module has a docstring tying back to a SPEC section.
- Every new file must appear in the ExecPlan's "Files to Change."

## 10. Testing Rules
- Every behavior change includes a test that fails before, passes after.
- Unit tests touch neither network nor real filesystem outside `tests/vectors/`.
- Never delete a passing test as part of a fix unless the test asserted incorrect behavior (Decision Log entry required).
- Coverage thresholds in `TESTING.md` are enforced in CI.

## 11. Documentation Update Rules
- Public contract change → relevant SPEC updated in same commit.
- Command behavior change → `COMMANDS.md` updated in same commit.
- Architectural change → `ARCHITECTURE.md` + new ADR in same commit.
- `ROADMAP.md` is strategic only.

## 12. Security Rules
- Never commit secrets, private keys, attestation signing keys, or discharger keys. Test vectors with key material live under `tests/vectors/` labeled `TEST_ONLY`.
- Logging redaction is mandatory: no message bodies, `intent_key`, `message_key`, principal / discharger secret keys, DH private keys, or `ck` / `ck_final` may appear in any log record. See `SECURITY.md` § Logging Redaction Rules.
- Crypto-touching changes run `./scripts/security-check.sh` pre-commit.
- Replacing PQ placeholders with liboqs requires an ADR + STOP acknowledgement.

## 13. Production Data Rules
- Never read / write / delete files under `/var/lib/aethermesh/` or `~/.aethermesh/` without explicit user permission.
- Never publish a `RevocationManifest` from CI.
- Never connect to a real public mixnet, gateway, or DHT node from CI; use loopback or in-process fakes.
- Never overwrite or truncate an existing audit-log SQLite file.

## 14. Definition of Done
- Every Acceptance Criterion in the active ExecPlan passes.
- `./scripts/verify.sh` returns `verify: ok`.
- ExecPlan Progress fully ticked.
- `git diff --name-only` matches "Files to Change" (extras justified in Decision Log).
- Outcomes & Retrospective filled.
- Remaining risks recorded in Surprises & Discoveries.

## 15. Final Response Requirements
When ending (complete or stopped):
1. ExecPlan completed: `<path>` — full / partial / stopped.
2. Changed files: full `git diff --name-only` output.
3. Commands run: ordered list with exit codes.
4. Command results: key outputs (`verify: ok`, etc.).
5. Acceptance criteria status: per-criterion pass/fail.
6. Decisions made: new Decision Log entries.
7. Assumptions confirmed / changed: `ASSUMPTIONS.md` updates.
8. Remaining risks: from Surprises & Discoveries.
9. Production-readiness status: which gates pass / fail now.

If stopped at a STOP condition, additionally:
- Exact blocker (1 sentence).
- Evidence (terminal output or file excerpt).
- Smallest decision needed (1 sentence).
- Recommended default (1 sentence).
