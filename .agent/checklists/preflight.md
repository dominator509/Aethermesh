# Checklist — Preflight

Before each session:

- [ ] `git status` clean (correct branch).
- [ ] `command -v uv` returns path; `uv --version` ≥ 0.4.
- [ ] `uv sync --all-extras --dev` exits 0.
- [ ] `AEP_PQ_BACKEND` set (`placeholder` dev only; `liboqs` otherwise).
- [ ] `AEP_KEYRING_SOCKET` set to dev value if ExecPlan exercises L5.
- [ ] `./scripts/preflight.sh` exits 0 with `preflight: ok`.
- [ ] All required scripts executable.
- [ ] Test harness importable: `uv run python -c "import aethermesh"` exits 0.
- [ ] No known blockers in Surprises & Discoveries.
