# Task Completion

- For ExecPlan work, after each milestone run its validation command, verify expected output, tick Progress, update Surprises/Decision Log as needed, and run `git diff --name-only` to reconcile against Files to Change.
- Final repo completion requires: all acceptance criteria pass, `./scripts/verify.sh` prints `verify: ok`, ExecPlan Progress fully ticked, Outcomes & Retrospective filled, risks recorded.
- For setup/doc-only tasks in this blueprint checkout, safe validation is limited to formatting/readability checks plus Serena activation; full gates are blocked until `.git`, `pyproject.toml`, package, tests, and executable shell semantics exist.
- Required final report shape is defined by `AGENTS.md` section 15 for ExecPlan work; for onboarding tasks also report changed files, Serena config status, Obsidian config status, memories, checks/results, blockers, acceptance.