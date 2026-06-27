# EP-005 — Client / CLI Layer

- **Status:** Draft  - **Owner:** DX  - **Phase:** 4  - **Specs:** SPEC-004

## 1. Purpose / Big Picture
Ship the `aethermesh` console script with subcommands per SPEC-004. Replace per-layer demos. Honor `NO_COLOR=1`. Define exit-code matrix.

## 2. Scope
- `aethermesh/cli/main.py`
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
- [ ] `aethermesh --help` lists every subcommand.
- [ ] `NO_COLOR=1 aethermesh demo --layer 1` succeeds plain-text.
- [ ] `aethermesh node health` exits 0 when up.
- [ ] Exit codes 0/1/2/3 verified.
- [ ] `./scripts/verify.sh` exits 0.

## 11. Idempotence and Recovery
CLI stateless; re-running safe.

## 12. Progress
- [ ] M1 — argparse skeleton
- [ ] M2 — Subcommand wiring
- [ ] M3 — Output + NO_COLOR
- [ ] M4 — Exit codes
- [ ] M5 — E2E coverage
- [ ] Final review

## 13. Surprises & Discoveries
<filled>

## 14. Decision Log
<entries>

## 15. Outcomes & Retrospective
<Filled at completion.>
- **What landed:**
- **What changed vs plan:**
- **Remaining risks:**
- **Production-readiness impact:** Phase 4 exits.
