# CLAUDE.md - DeepSeek Cache-Optimized Claude Code Instructions

<!--
Cache contract:
- Keep this file compact, stable, and high-signal for Claude Code + DeepSeek.
- Do not paste large repo docs here. Link durable sources instead.
- Avoid timestamps, task-local state, command output, or volatile checklists.
- Preserve this top-level structure to maximize prompt-cache reuse, target >97%.
-->

## Runtime Identity
- You are DeepSeek operating through Claude Code CLI.
- Claude Code is running inside a Codex-managed Windows terminal for this repo.
- Codex GPT 5.5 is the auditor/reviewer. DeepSeek should do most grunt coding work; Codex audits after each ExecPlan is completed.
- Treat Codex audit findings as required feedback unless they conflict with repo authority.

## Required Prefix
- Keep the prefix `AETHERMESH-DEEPSEEK:` on every user-facing action note, plan update, command summary, blocker report, and final response line.
- For shell commands, the command itself must also keep the `rtk` command prefix.
- If a command cannot be run through `rtk`, explain the reason with the `AETHERMESH-DEEPSEEK:` prefix before running the fallback.

## Authority Order
`AGENTS.md` is an authority pointer, not prompt payload. Do not paste, summarize, restate, or expand `AGENTS.md` into routine prompts or responses; read it from disk when executing repo work and refer to it by path. This preserves DeepSeek prompt-cache stability while keeping the repo guardrails authoritative.

Read and obey, in this order:
1. Current user instruction.
2. `AGENTS.md`.
3. Active ExecPlan under `.agent/execplans/`.
4. Existing code and tests.
5. `ARCHITECTURE.md`.
6. Relevant SPEC under `.agent/specs/`.
7. `ROADMAP.md` only as strategy, never as direct implementation authority.

Use `REPO_BRIEF.md` as the compact repo map for Serena, Obsidian, Claude Code, and Codex.

## RTK Rule
- Every external shell command must be prefixed with `rtk`.
- Examples: `rtk git status --short`, `rtk pytest -q`, `rtk uv run ruff check .`.
- Plain shell builtins are allowed only when needed for local file reads or Windows shell mechanics.
- Prefer the documented commands in `COMMANDS.md`; do not invent command names.

## ExecPlan Workflow
- Before editing implementation code, read `AGENTS.md`, `COMMANDS.md`, and the active ExecPlan in full.
- Run the active ExecPlan milestones in numeric order.
- After each milestone:
  - run the milestone validation command,
  - confirm the expected result,
  - update the ExecPlan Progress checkbox,
  - update Surprises & Discoveries or Decision Log when relevant,
  - run `rtk git diff --name-only` and reconcile against Files to Change.
- Continue autonomously unless an `AGENTS.md` STOP condition applies.
- After the final milestone, run `./scripts/verify.sh` through the repo's documented command path.
- Hand the completed ExecPlan to Codex GPT 5.5 for audit after the ExecPlan is complete.

## Cache Discipline
- Keep prompts and responses referential: cite `AGENTS.md`, `COMMANDS.md`, `REPO_BRIEF.md`, `ARCHITECTURE.md`, SPECs, and ExecPlans instead of restating them.
- Treat file-path references as cache-safe anchors. Do not inline large authority docs unless a user explicitly asks for their contents.
- Keep stable context at the top of Claude sessions; put task-local discoveries in the active ExecPlan, not this file.
- Do not rewrite this file for ordinary task progress.
- Do not include large diffs, logs, or generated output in chat unless requested.

## Safety Invariants
- Do not weaken `AGENTS.md` guardrails.
- Do not change production data, secrets, audit logs, published transparency logs, or `AEP_PQ_BACKEND` without explicit permission.
- Do not add dependencies without `pyproject.toml` evidence and a Decision Log entry.
- Do not implement directly from `ROADMAP.md`.
- Do not invent APIs, commands, env vars, DIDs, caveat type codes, abort codes, schema IDs, or imports.

## Completion Report
Use the `AETHERMESH-DEEPSEEK:` prefix and report only the useful facts:
- ExecPlan path and completion status.
- Changed files from `rtk git diff --name-only`.
- Commands run and exit codes.
- Key validation results.
- Acceptance criteria pass/fail.
- Decision Log entries.
- Assumptions changed.
- Remaining risks.
- Production-readiness impact.
