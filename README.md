# AetherMesh / AEP — Agent Exchange Protocol

**Status: Foundation established (EP-001 complete).** `verify: ok` — CI baseline, package stubs, test harness, and build pipeline operational.

## Quick Start
```sh
uv sync --all-extras --dev
./scripts/verify.sh   # preflight + lint + format + typecheck + unit + integration + e2e + build + security + audit + smoke
```

## Project
AetherMesh / AEP is a reference implementation for a vendor-neutral Agent Exchange Protocol with five layers: L1 Sphinx mixnet, L2 capability-hashed DHT, L3 Noise-PQ XK with mutual attestation, L4 PQ Double Ratchet + MLS, and L5 macaroon-style CapTokens.

## Development
- Agent guardrails: `AGENTS.md`
- Command reference: `COMMANDS.md`
- Active ExecPlan: `.agent/execplans/`
- Architecture: `ARCHITECTURE.md`
- Next: EP-002 (core domain)

## License
MIT.
