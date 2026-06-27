# .agent/EXECUTION_RULES.md — Execution Rules for Lower-Tier Coding Agents

Consolidated rules. Companion to AGENTS.md and .agent/PLANS.md.

## One Active ExecPlan Rule
Work on exactly one ExecPlan at a time. Don't start a new one until the current Outcomes & Retrospective is filled and `./scripts/verify.sh` passes.

## No Hidden Context Rule
Don't assume facts that aren't in AGENTS.md, COMMANDS.md, ARCHITECTURE.md, the relevant SPEC, the ExecPlan, or repository code.

## No Roadmap-Only Implementation Rule
`ROADMAP.md` is strategic. If a roadmap item looks unaddressed, open or finish the corresponding ExecPlan.

## Continue-By-Default Rule
After completing a milestone, immediately proceed to the next. Don't summarize unless asked. Stop only for STOP conditions.

## STOP-Only Rule
Pause only for explicit STOP conditions in AGENTS.md § 4. Report per AGENTS.md § 15.

## Anti-Drift Rule
Implement only what the ExecPlan's Scope authorizes. Run `git diff --name-only` after each milestone; reconcile.

## Anti-Hallucination Rule
- Don't invent package APIs, command names, env vars, CapToken caveat codes, abort codes, DIDs, or schema ids.
- Confirm every name by reading the file or package source.
- Use commands from COMMANDS.md only.

## Anti-Fixation Rule
On same-root failure:
1. Smallest targeted fix.
2. Narrower diagnostic; isolate.
3. Stop approach; record hypotheses; pick simpler path.

## Test-Before-Completion Rule
Milestone not complete until validation returned expected result. ExecPlan not complete until `verify.sh` returns `verify: ok`.

## Diff Review Rule
After each milestone and at final review:
```
git diff --name-only
```
Reconcile against ExecPlan's Files to Change.

## Final Response Rule
End every session with 9-point report from AGENTS.md § 15. Append 4-point stop appendix if applicable.
