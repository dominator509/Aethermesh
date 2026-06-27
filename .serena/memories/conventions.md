# Conventions

- Anti-drift: implement only active ExecPlan scope; no broad refactors, dependency swaps, file reorganizations, or style rewrites unless the ExecPlan mandates them.
- Anti-hallucination: do not invent package APIs, env vars, commands, DIDs, caveat type codes, abort codes, schema IDs, or imported names. Open the authoritative file first.
- Public modules require docstrings tying back to SPEC sections; new files must appear in the ExecPlan Files to Change.
- Layer import rules are strict: common imports no layer; L1 common only; L2 common+L1; L3 common+L1+L2; L4 common+L1+L3; L5 common only; demos/tools may import any layer.
- Security invariants: hybrid PQ mandatory; no plaintext body persistence; no forbidden log keys; production `AEP_PQ_BACKEND=liboqs`; liboqs replacement requires ADR plus STOP acknowledgement.
- Documentation rule: public contract changes update SPEC; command changes update `COMMANDS.md`; architecture changes update `ARCHITECTURE.md` plus ADR.