# Checklist — Agent Readiness

Before starting an ExecPlan:

- [ ] Exactly one ExecPlan is active.
- [ ] ExecPlan is self-contained per `.agent/PLANS.md`.
- [ ] "Files to Read First" is concrete and ≤ 8 paths.
- [ ] "Files to Change" is concrete and exact.
- [ ] Every milestone has an exact validation command from `COMMANDS.md`.
- [ ] Every milestone has an observable Expected Result.
- [ ] Every milestone has explicit Recovery Instructions per AGENTS.md § 7.
- [ ] Non-goals listed explicitly.
- [ ] STOP conditions from AGENTS.md § 4 referenced.
- [ ] Anti-fixation retry budget understood.
- [ ] Diff review rule understood (`git diff --name-only`).
- [ ] No hidden context.
- [ ] No vague requirements (no "make it work", "best practices").
