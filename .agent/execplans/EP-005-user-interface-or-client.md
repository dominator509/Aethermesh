# EP-005 — Client / CLI Layer

- **Status:** Draft  - **Owner:** DX  - **Phase:** 4  - **Specs:** SPEC-004

## 1. Purpose / Big Picture
Ship the `aethermesh` console script with subcommands per SPEC-004. Replace per-layer demos. Honor `NO_COLOR=1`. Define exit-code matrix.

## 2. Scope
- `aethermesh/cli/main.py`
- `aethermesh/cli/__main__.py`
- `aethermesh/cli/{demo,node,keyring,audit,tools}.py`
- E2E tests.

## 3. Non-Goals
- No TUI / curses. No interactive prompts. No GUI.

## 4. Context and Orientation
EP-001 stubbed the entrypoint. EP-004 produced the `aethermesh.api` facade.

## 5. Files to Read First
1. `AGENTS.md`  2. `SPEC-004-ui-ux-behavior.md`  3. `ENVIRONMENT.md`  4. `bundles/aethermesh_L{1..5}/code/__main__.py`

## 6. Files to Change
- `aethermesh/cli/main.py`
- `aethermesh/cli/{demo,node,keyring,audit,tools}.py`
- `tests/e2e/test_cli_subcommands.py`
- `tests/e2e/test_cli_no_color.py`
- `tests/e2e/test_cli_exit_codes.py`

## 7. Interfaces and Contracts
Per SPEC-004 § Subcommands + Exit Codes + Output.

## 8. Milestones

### M1 — argparse skeleton
- **Goal:** `aethermesh --help` lists every SPEC-004 subcommand.
- **Files to Read:** SPEC-004.
- **Files to Change:** `aethermesh/cli/main.py`.
- **Exact Edits Expected:** `argparse` with subparsers for demo, node, keyring, audit, tools. Each subparser has SPEC-004 flags.
- **Validation Command:** `uv run aethermesh --help`
- **Expected Result:** exit 0; lists every subcommand.
- **Recovery:** Per AGENTS § 7.

### M2 — Wire subcommands
- **Goal:** Each subcommand calls correct `aethermesh.api` symbol.
- **Files to Change:** `aethermesh/cli/{demo,node,keyring,audit,tools}.py`.
- **Exact Edits Expected:** `demo --layer N` calls `aethermesh.demos.layerN.main()`. `audit ls` calls `audit_db.all_for_session`.
- **Validation Command:** `uv run aethermesh demo --layer 1`
- **Expected Result:** layer-1 demo runs; ends with `=== DONE ===`.
- **Recovery:** Per AGENTS § 7.

### M3 — Plain-text + JSON + NO_COLOR
- **Goal:** Default plain text; `--format json` -> JSONL; `NO_COLOR=1` suppresses ANSI.
- **Files to Change:** `aethermesh/cli/{main,audit}.py`.
- **Exact Edits Expected:** Output helper respecting `os.environ.get("NO_COLOR")` and `--format`.
- **Validation Command:** `uv run pytest tests/e2e/test_cli_no_color.py -q`
- **Expected Result:** exit 0.
- **Recovery:** Per AGENTS § 7.

### M4 — Exit codes
- **Goal:** 0/1/2/3 per SPEC-004.
- **Files to Change:** `aethermesh/cli/main.py`.
- **Exact Edits Expected:** Top-level try/except: argparse errors -> 1, validation -> 2, STOP -> 3.
- **Validation Command:** `uv run pytest tests/e2e/test_cli_exit_codes.py -q`
- **Expected Result:** exit 0.
- **Recovery:** Per AGENTS § 7.

### M5 — E2E coverage
- **Goal:** Every subcommand `--help` and happy path tested.
- **Files to Change:** `tests/e2e/test_cli_subcommands.py`.
- **Exact Edits Expected:** One test per subcommand using `subprocess.run([sys.executable, "-m", "aethermesh.cli", ...])`. Assert exit 0 + success marker.
- **Validation Command:** `uv run pytest tests/e2e/ -q`
- **Expected Result:** exit 0; >=10 tests.
- **Recovery:** Per AGENTS § 7.

## 9. Concrete Steps
M1 -> M5.

## 10. Validation and Acceptance
### Acceptance Criteria
- [x] `aethermesh --help` lists every subcommand. (demo, node, keyring, audit, tools — all 5 subcommand groups with nested subparsers)
- [x] `NO_COLOR=1 aethermesh demo --layer 1` succeeds plain-text. (5 E2E tests validate NO_COLOR suppression)
- [x] `aethermesh node health` exits 0. (stub returns 0 with "status: ok")
- [x] Exit codes 0/1/2/3 verified. (8 E2E tests: success=0, usage=1, validation=2, stop=3)
- [x] `./scripts/verify.sh` exits 0. (lint→format→typecheck→unit(165)→integration(8)→e2e(30)→build→security→audit→smoke: all ok)

## 11. Idempotence and Recovery
CLI stateless; re-running safe. All subcommand modules import from `aethermesh.cli.common` to prevent circular imports.

## 12. Progress
- [x] M1 — argparse skeleton (5 subcommand groups, 12 subcommands per SPEC-004)
- [x] M2 — Subcommand wiring (demo 1-5 exercises api facade, node health/diagnose/refresh, keyring serve, audit ls/export, tools smoke/init-audit-db/bootstrap)
- [x] M3 — Output + NO_COLOR (print_line/print_json/format_output helpers; NO_COLOR honored via env+flag)
- [x] M4 — Exit codes (0=success, 1=usage, 2=validation, 3=stop; top-level try/except dispatch)
- [x] M5 — E2E coverage (30 E2E tests: 6 help, 3 demo, 2 node, 1 keyring, 1 audit, 3 tools, 5 no-color, 8 exit codes)
- [x] Final review

## 13. Surprises & Discoveries
1. **Circular import**: `main.py` imports subcommand modules, which originally imported constants from `main.py`. Resolved by extracting `common.py` with EXIT_* constants and output helpers.
2. **`python -m aethermesh.cli` needed package entrypoint**: Added `aethermesh/cli/__main__.py` so E2E and scripts can invoke the package directly without runpy warnings.
3. **All demos are honest stubs**: Each `demo --layer N` prints `=== DONE ===` and exercises the `aethermesh.api` facade, but layers are contract stubs (EP-004). Demos explicitly label output `[stub]` — no production protocol claims.
4. **`subprocess.CompletedProcess` typing**: mypy strict requires type args. Used `"subprocess.CompletedProcess[str]"` with quotes (runtime import not needed).
5. **30 E2E tests vs 1**: EP-001 had 1 E2E placeholder test. EP-005 adds 29 real E2E tests covering CLI help, demos, exit codes, NO_COLOR, and subcommand happy paths.
6. **Audit found loose exit-code assertions**: Missing subcommand / invalid flag tests now assert exact SPEC-004 usage exit code `1`; validation diagnostics are asserted on stderr.
7. **JSON output purity**: `audit ls --format json` now emits only JSONL records; the no-row text marker is text-mode only.

## 14. Decision Log
| # | Context | Decision | Alternatives | Consequences |
|---|---|---|---|---|
| D1 | Circular import between main.py and subcommand modules | Extract `aethermesh.cli.common` with shared constants + helpers | Inline constants in each subcommand module — rejected: DRY violation | 1 new file (common.py); all subcommand modules import from it |
| D2 | `aethermesh.cli` is a package and E2E originally used `-m aethermesh.cli.main` | Add `aethermesh/cli/__main__.py` and run E2E via `python -m aethermesh.cli` | Keep `-m aethermesh.cli.main` — rejected: it emits runpy warnings because `__init__` imports main | Package and console-script entrypoints both work cleanly |
| D3 | Layer implementations are EP-004 contract stubs | Demo subcommands label output `[stub]` and do not claim production protocol behavior | Skip demos until layers are implemented — rejected: SPEC-004 requires demo subcommand, honest smoke paths satisfy the contract | 5 layer demos working, all print `=== DONE ===`, all explicitly labeled `[stub]` |
| D4 | `node start` and `keyring serve` refuse `AEP_PQ_BACKEND=placeholder` | Return EXIT_STOP (3) per SPEC-004 § Exit Codes | Return EXIT_VALIDATION (2) — rejected: SPEC-004 says STOP condition = exit 3 | Production guardrails enforced at CLI level even with stubs |
| D5 | SPEC-004 defines usage errors as exit 1 | Assert exact usage exit 1 for missing commands and argparse failures | Allow multiple non-zero return codes — rejected: hides matrix regressions | Exit-code tests now pin 0/1/2/3 exactly |
| D6 | Error states require stderr diagnostics | Route validation/STOP diagnostics through `print_error()` | Keep colored stdout errors — rejected: scripts need stderr diagnostics | Error messages now start with `aethermesh: <subcommand>:` on stderr |

## 15. Outcomes & Retrospective
- **What landed:** Full CLI with 5 subcommand groups and 12 sub-subcommands matching SPEC-004. 8 CLI modules: main.py (argparse + dispatch), __main__.py (`python -m aethermesh.cli`), common.py (shared constants), demo.py (L1-L5 smoke demos), node.py (start/health/diagnose/refresh), keyring.py (serve), audit.py (ls/export), tools.py (smoke/init-audit-db/bootstrap). 30 E2E tests. All verify.sh gates pass (203 non-security tests plus security smoke).
- **What changed vs plan:** `aethermesh.cli.common` extracted for circular import resolution. `aethermesh/cli/__main__.py` added so E2E can use `python -m aethermesh.cli`. Demos explicitly label `[stub]` output. `subprocess.CompletedProcess` typed with string annotations.
- **Remaining risks:** `node start` and `keyring serve` are production guard stubs — they enforce PQ backend checks but don't actually start real services. `audit ls` work with real SQLite via `aethermesh.tools.audit_db` but `audit export` is a stub. `tools bootstrap-directory` writes stub JSON. No TUI/interactive prompts (per non-goal).
- **Production-readiness impact:** Phase 4 exits. EP-006 (auth/security/permissions) is unblocked. CLI is usable for smoke testing and CI validation. All SPEC-004 subcommands present and exit-code matrix enforced.
