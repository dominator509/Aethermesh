# AetherMesh / AEP — Blueprint Pack (Pass 1)

This is the **Pass 1** blueprint pack for the AetherMesh / AEP project. It contains every file the prompt asked for **except the 11 ExecPlans**, which ship separately as `aethermesh_blueprint_pass2.zip` (delivered immediately after this one in the same conversation).

## What's in this pack
- **17 top-level docs** at the repo root (AGENTS.md, ASSUMPTIONS.md, PROJECT_BRIEF.md, ROADMAP.md, ARCHITECTURE.md, DECISIONS.md, COMMANDS.md, TESTING.md, SECURITY.md, ENVIRONMENT.md, DEPLOYMENT.md, OPERATIONS.md, OBSERVABILITY.md, PRODUCTION_READINESS.md, RELEASE.md, ROLLBACK.md, CONTRIBUTING.md).
- **`.agent/PLANS.md`** and **`.agent/EXECUTION_RULES.md`**.
- **4 reusable prompts** under `.agent/prompts/`.
- **9 SPECs** (SPEC-000..SPEC-008) under `.agent/specs/`.
- **9 checklists** under `.agent/checklists/`.
- **5 templates** under `.agent/templates/`.
- **14 shell scripts** under `scripts/` (all `chmod 755`).

## What ships in Pass 2
- `.agent/execplans/EP-000-repository-discovery.md`
- `.agent/execplans/EP-001-foundation.md`
- `.agent/execplans/EP-002-core-domain.md`
- `.agent/execplans/EP-003-data-and-persistence.md`
- `.agent/execplans/EP-004-api-or-service-layer.md`
- `.agent/execplans/EP-005-user-interface-or-client.md`
- `.agent/execplans/EP-006-auth-security-and-permissions.md`
- `.agent/execplans/EP-007-testing-hardening.md`
- `.agent/execplans/EP-008-observability-and-operations.md`
- `.agent/execplans/EP-009-deployment-and-release.md`
- `.agent/execplans/EP-010-production-readiness.md`

# How to Use This Blueprint Pack

## 1. Place files into the repository
Unzip this archive at the repository root. Every file in this pack maps 1:1 to a path in the repo. Do not rename files. Scripts under `scripts/` ship with `chmod 755` set; preserve permissions on Unix.

```sh
unzip aethermesh_blueprint_pass1.zip
mv aethermesh_blueprint/* aethermesh_blueprint/.[!.]* /path/to/your/repo/
# (or copy in place)
```

When Pass 2 arrives, repeat with `aethermesh_blueprint_pass2.zip` — its files all land under `.agent/execplans/`.

## 2. Choose the active ExecPlan
After both passes are in place:
- For this project (status = existing partially built repository per ASSUMPTIONS.md A12), the first active ExecPlan is `.agent/execplans/EP-000-repository-discovery.md`.
- After EP-000, proceed sequentially: EP-001 → EP-010.
- Do not implement directly from `ROADMAP.md` (it is strategic only).

## 3. Run preflight
```sh
./scripts/preflight.sh
# expected: preflight: ok
```
Fix any blocker before proceeding.

## 4. Run a lower-tier coding LLM against an ExecPlan
Use this generic invocation prompt (substitute `[EXECPLAN_PATH]`):

```
Read AGENTS.md, COMMANDS.md, .agent/PLANS.md, and [EXECPLAN_PATH].
Implement [EXECPLAN_PATH] to completion.
Do not ask for next steps.
Do not implement from ROADMAP.md directly.
Do not broaden scope.
Complete milestones in order.
Validate after each milestone.
Update the ExecPlan as you work.
Use only commands from COMMANDS.md.
Stop only for STOP conditions in AGENTS.md.
At the end, run the required verification command, run git diff --name-only, update Outcomes & Retrospective, and report changed files, commands run, results, decisions, risks, and acceptance status.
```

Codex CLI example:
```sh
codex --cd . \
  --ask-for-approval never \
  --sandbox workspace-write \
  "Read AGENTS.md, COMMANDS.md, .agent/PLANS.md, and .agent/execplans/EP-001-foundation.md. Implement EP-001-foundation.md to completion. Do not ask for next steps. Stop only for STOP conditions in AGENTS.md. Update the ExecPlan as you work. Run validation after each milestone."
```

If the runner does not support those flags, the same instruction can be pasted into any coding agent that can read files, edit files, and run terminal commands.

## 5. Continue a partially completed plan
Use `.agent/prompts/continue-execplan.md`.

## 6. Debug failing validation
Use `.agent/prompts/debug-validation-failure.md`. Anti-fixation rule applies (AGENTS.md § 7).

## 7. Perform final review
Use `.agent/prompts/final-review.md`. The final report must include all 9 items from AGENTS.md § 15.

## 8. Decide production readiness
Run `./scripts/production-readiness-check.sh`. It runs the 16 gates from `SPEC-008-production-readiness.md`. Exits 0 → production ready.

## 9. Avoid roadmap-only implementation
`ROADMAP.md` is strategic. If a roadmap item looks unaddressed, open or finish its corresponding ExecPlan rather than coding from the roadmap.

## 10. Update plans as the repository evolves
- Per-feature: open or update the relevant SPEC and create an ExecPlan from `.agent/templates/execplan-template.md`.
- Per architecture change: update `ARCHITECTURE.md` + add an ADR in `DECISIONS.md` in the same commit.
- Per command change: update `COMMANDS.md` in the same commit.

## License
MIT.
