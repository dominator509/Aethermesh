# Core

- Repo authority order: current user instruction -> `AGENTS.md` -> active ExecPlan under `.agent/execplans/` -> code/tests -> `ARCHITECTURE.md` -> SPEC -> `ROADMAP.md` strategic only.
- Durable compact orientation lives in `REPO_BRIEF.md`; read it before deeper docs when re-entering the repo.
- This checkout currently presents as a blueprint/control-plane pack: root docs, `.agent/`, `scripts/`, `.obsidian/`; no `.git`, `pyproject.toml`, `aethermesh/`, `tests/`, or `bundles/` visible at onboarding time.
- First active plan per README: `.agent/execplans/EP-000-repository-discovery.md`; it STOPs if not a Git repo during M1.
- Obsidian vault config exists at `.obsidian/`; avoid copying large repo content into notes. Prefer linking `REPO_BRIEF.md`.
- Read command/tool facts in `mem:tech_stack`; use `mem:suggested_commands` for repo-approved commands; use `mem:conventions` before edits; use `mem:task_completion` before final reports.