# SPEC-004 — CLI Behavior

- **Status:** Draft  - **Owner:** DX  - **Phase:** 4  - **ExecPlans:** EP-005

## User-Visible Goal
Single `aethermesh` console script driving demos, node ops, keyring, audit. No GUI.

## Non-Goals
TUI / curses; interactive prompts that block scripts.

## Terms
- **Subcommand:** `aethermesh <verb> [...]`.

## Required Behavior

### Subcommands
```
aethermesh demo --layer N [--lane fast|slow|slow+]
aethermesh node start --role <mix-layer-N|gateway-entry|gateway-exit|dht-node>
aethermesh node health
aethermesh node diagnose [--out diagnose-report.json]
aethermesh node refresh-directory
aethermesh keyring serve --socket <path>
aethermesh audit ls [--session <hash>]
aethermesh audit export --since <iso-ts> --until <iso-ts> --out <path>
aethermesh tools smoke
aethermesh tools init-audit-db --path <path>
aethermesh tools bootstrap-directory --out <path>
```

### Output
- Default plain text to stdout; one line per record where applicable.
- `--format json` switches to JSON Lines.
- Honors `NO_COLOR=1`; color not sole state indicator.

### Exit Codes
- `0` — success.
- `1` — invalid usage.
- `2` — validation / preflight failure.
- `3` — STOP condition (e.g., `AEP_PQ_BACKEND=placeholder` in prod).

## Inputs / Outputs
Inputs: CLI args + env vars (ENVIRONMENT.md). Outputs: stdout (records), stderr (diagnostics), exit code.

## Error States
Stderr `aethermesh: <subcommand>: <message>`. No stack traces unless `AEP_LOG_LEVEL=debug`.

## Security Rules
- `keyring serve` refuses to start outside TEE in production.
- No subcommand reads `/var/lib/aethermesh/` without `--explicit-path`.

## Accessibility
- Plain-text default; `NO_COLOR=1` honored; no color-as-sole-state.

## Performance
- `aethermesh node health` returns within 200 ms.
- `aethermesh tools smoke` returns within 5 s.

## Required Tests
- `tests/e2e/test_cli_subcommands.py` covers every `--help`.
- `tests/e2e/test_cli_no_color.py` confirms `NO_COLOR=1` suppresses ANSI.
- `tests/e2e/test_cli_exit_codes.py` covers exit-code matrix.

## Acceptance Criteria
- `aethermesh --help` lists every subcommand.
- `NO_COLOR=1 aethermesh demo --layer 1` succeeds with plain text.
- `aethermesh node health` exits 0 when up; non-zero otherwise.
