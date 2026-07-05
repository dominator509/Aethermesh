# AetherMesh / AEP

AetherMesh / AEP is a reference implementation and production-readiness harness for a vendor-neutral Agent Exchange Protocol. Its goal is to let autonomous agents find peers, establish post-quantum-secure sessions, exchange policy-checked messages, and authorize actions without a central vendor account or metadata-rich relay.

The project is still pre-production. The liboqs-backed local baseline is now verified, but EP-010 remains blocked on two-implementation interop, a real performance suite and baseline, and human security sign-off.

## What It Is

AetherMesh is organized as five protocol layers plus shared tooling:

| Layer | Purpose |
|---|---|
| L1 Sphinx mixnet | Fixed-size anonymous transport, mix nodes, gateways, cover traffic |
| L2 capability DHT | Capability-hashed discovery records, DHT lookup, revocation/endorsement data |
| L3 Noise-PQ XK | Hybrid post-quantum handshake with mutual attestation |
| L4 PQ ratchet / MLS | Session messaging, policy split between intent and message body keys |
| L5 CapTokens | Macaroon-style capability tokens, caveats, discharges, revocation, audit receipts |

Current implementation status is mixed by layer. The repo has concrete common crypto/canonical/DID helpers, CLI/tooling, audit DB migrations, logging/metrics, CapToken caveat verification, and attestation scaffolding. Several protocol bodies remain stubs, and production launch is intentionally blocked until those stubs are replaced and the readiness gates pass.

## Current Status

- Package version: `0.1.0.dev0`.
- License: MIT.
- Package manager: `uv`.
- Python: 3.11+.
- Latest verified development gate: `AEP_PQ_BACKEND=liboqs ./scripts/verify.sh` passes.
- Latest production gate: `./scripts/production-readiness-check.sh` now reaches Gate 16 and fails because ADR-0010 is still `Proposed`, not `Accepted`.
- ADR-0010 security sign-off is still `Proposed`, not `Accepted`.
- No v1.0.0 tag should be pushed until every production-readiness gate passes.

Known production blockers:

- Replace remaining protocol stubs with real L1/L2/L3/L4/L5 implementations where marked.
- Populate and pass the two-implementation interop matrix against a second implementation.
- Record and review real performance baselines on the reference environment; the repo-local perf suite now writes `tests/perf/results/baseline.json`, but L1/L3/L4 still exercise placeholder or stub-level paths.
- Obtain human security lead sign-off and mark ADR-0010 accepted.

## Quick Start

From the repository root:

```sh
uv sync --all-extras --dev
./scripts/preflight.sh
./scripts/verify.sh
```

Note: `uv sync --all-extras --dev` now resolves `liboqs-python` from the upstream Git tag pinned in `pyproject.toml`, so the machine needs GitHub access during sync.

Expected result:

```text
preflight: ok
verify: ok
```

On Windows, if your shell cannot execute `.sh` scripts directly, run them through Git Bash or `sh.exe`:

```cmd
sh.exe scripts\preflight.sh
sh.exe scripts\verify.sh
```

Repo command authority lives in `COMMANDS.md`. Coding agents must use that file rather than inventing command names.

## Common Commands

| Task | Command |
|---|---|
| Sync dev environment | `uv sync --all-extras --dev` |
| Preflight | `./scripts/preflight.sh` |
| Lint | `uv run ruff check .` |
| Format check | `uv run ruff format --check .` |
| Typecheck | `uv run mypy aethermesh tests` |
| Unit tests | `uv run pytest tests/unit -q` |
| Integration tests | `uv run pytest tests/integration -q` |
| E2E tests | `uv run pytest tests/e2e -q` |
| Property tests | `uv run pytest tests/property -q` |
| Security check | `./scripts/security-check.sh` |
| Dependency audit | `./scripts/dependency-audit.sh` |
| Build wheel/sdist | `uv build` |
| Smoke test | `uv run python -m aethermesh.tools.smoke` |
| Full verification | `./scripts/verify.sh` |
| Production readiness | `./scripts/production-readiness-check.sh` |

Production readiness is expected to fail until the blockers listed above are resolved.

## CLI Examples

```sh
uv run aethermesh --help
uv run aethermesh demo --layer 1
uv run aethermesh node health
uv run aethermesh tools smoke
uv run python -m aethermesh.tools.init_audit_db --path ./audit.db
```

Development uses the placeholder PQ backend unless explicitly configured otherwise:

```sh
AEP_PQ_BACKEND=placeholder uv run python -m aethermesh.tools.smoke
```

Production-mode smoke rejects the placeholder backend:

```sh
AEP_PQ_BACKEND=placeholder uv run python -m aethermesh.tools.smoke --prod
```

With a valid liboqs install, this now passes locally:

```sh
AEP_PQ_BACKEND=liboqs uv run python -m aethermesh.tools.smoke --prod
```

## What Is liboqs?

`liboqs` is the Open Quantum Safe project's C library for quantum-safe cryptographic algorithms. It provides implementations and a common API for post-quantum key encapsulation mechanisms and signature algorithms, including standardized families such as ML-KEM and ML-DSA.

AetherMesh uses liboqs for the production post-quantum backend:

- ML-KEM-768 for KEM operations.
- ML-DSA-65 for signature operations.
- Hybrid operation alongside classical primitives; the project forbids classical-only and PQ-only production modes.

There are two pieces:

- `liboqs`: the native C library and shared library (`oqs.dll`, `liboqs.so`, or `liboqs.dylib`).
- `liboqs-python`: Python bindings that expose an importable `oqs` module with APIs such as `KeyEncapsulation` and `Signature`.

Important: the package name `oqs` by itself is not enough evidence that the correct binding is installed. This repo's production smoke gate checks for the actual liboqs-python API.

Official upstream references:

- https://github.com/open-quantum-safe/liboqs
- https://github.com/open-quantum-safe/liboqs-python
- https://openquantumsafe.org/liboqs/

## Installing liboqs

The exact commands depend on platform and compiler setup. The safest path is to follow the upstream liboqs and liboqs-python READMEs, then run the AetherMesh verification commands below.

### Windows

Prerequisites:

- Git.
- CMake.
- Ninja.
- Visual Studio Build Tools with the C++ toolchain.
- Python/uv already working for this repo.

Open an x64 Native Tools Command Prompt or another shell with the MSVC compiler on `PATH`.

```cmd
cd /d C:\src
git clone --depth=1 https://github.com/open-quantum-safe/liboqs
cmake -S liboqs -B liboqs\build -G Ninja -DCMAKE_INSTALL_PREFIX=C:\liboqs -DCMAKE_WINDOWS_EXPORT_ALL_SYMBOLS=TRUE -DBUILD_SHARED_LIBS=ON
cmake --build liboqs\build --parallel 8
cmake --install liboqs\build
```

For the current shell:

```cmd
set OQS_INSTALL_PATH=C:\liboqs
set PATH=C:\liboqs\bin;%PATH%
```

Persist those values through Windows Environment Variables if you want them available in future shells.

Then install the Python wrapper into the AetherMesh uv environment:

```cmd
cd /d C:\src
git clone --depth=1 https://github.com/open-quantum-safe/liboqs-python
cd liboqs-python
uv pip install .
```

Verify from this repo:

```cmd
cd /d C:\dev\Aethermesh
set OQS_INSTALL_PATH=C:\liboqs
set PATH=C:\liboqs\bin;%PATH%
uv run python -c "import oqs; print(hasattr(oqs, 'KeyEncapsulation'), hasattr(oqs, 'Signature'))"
set AEP_PQ_BACKEND=liboqs
uv run python -m aethermesh.tools.smoke --prod
```

Expected:

```text
True True
smoke test: ok
```

### Linux

Install build dependencies first. On Ubuntu-like systems:

```sh
sudo apt install cmake gcc ninja-build libssl-dev python3-dev
```

Build and install liboqs:

```sh
git clone --depth=1 https://github.com/open-quantum-safe/liboqs
cmake -S liboqs -B liboqs/build -GNinja -DBUILD_SHARED_LIBS=ON
cmake --build liboqs/build --parallel 8
sudo cmake --install liboqs/build
export LD_LIBRARY_PATH="${LD_LIBRARY_PATH}:/usr/local/lib"
```

Install the Python wrapper:

```sh
git clone --depth=1 https://github.com/open-quantum-safe/liboqs-python
cd liboqs-python
uv pip install .
```

Verify from this repo:

```sh
cd /path/to/Aethermesh
uv run python -c "import oqs; print(hasattr(oqs, 'KeyEncapsulation'), hasattr(oqs, 'Signature'))"
AEP_PQ_BACKEND=liboqs uv run python -m aethermesh.tools.smoke --prod
```

### macOS

Install dependencies with Homebrew:

```sh
brew install cmake ninja openssl@3
```

Build and install liboqs:

```sh
git clone --depth=1 https://github.com/open-quantum-safe/liboqs
cmake -S liboqs -B liboqs/build -GNinja -DBUILD_SHARED_LIBS=ON
cmake --build liboqs/build --parallel 8
sudo cmake --install liboqs/build
export DYLD_LIBRARY_PATH="${DYLD_LIBRARY_PATH}:/usr/local/lib"
```

Install the Python wrapper:

```sh
git clone --depth=1 https://github.com/open-quantum-safe/liboqs-python
cd liboqs-python
uv pip install .
```

Verify from this repo:

```sh
cd /path/to/Aethermesh
uv run python -c "import oqs; print(hasattr(oqs, 'KeyEncapsulation'), hasattr(oqs, 'Signature'))"
AEP_PQ_BACKEND=liboqs uv run python -m aethermesh.tools.smoke --prod
```

## Configuration

Important environment variables are documented in `ENVIRONMENT.md`.

| Variable | Purpose |
|---|---|
| `AEP_PQ_BACKEND` | `placeholder` for dev only, `liboqs` for staging/prod |
| `AEP_NODE_ROLE` | Mix/gateway/DHT role, such as `mix-layer-1` or `gateway-entry` |
| `AEP_NODE_ID_HEX` | 32-hex-character node identifier |
| `AEP_KEYRING_SOCKET` | Unix socket path for keyring service |
| `AEP_AUDIT_DB_PATH` | Local SQLite audit DB path |
| `AEP_LOG_LEVEL` | `debug`, `info`, `warning`, or `error` |
| `AEP_OTEL_ENDPOINT` | OTLP endpoint for production observability |

Never use `AEP_PQ_BACKEND=placeholder` for production-targeted work.

## Docker and Staging

EP-009 added Dockerfiles and a local staging compose file:

```sh
docker build -f Dockerfile.mix-node -t aethermesh-mix-node:test .
docker build -f Dockerfile.gateway -t aethermesh-gateway:test .
docker compose -f ops/staging/docker-compose.yml config
docker compose -f ops/staging/docker-compose.yml up -d
./scripts/smoke-test.sh
docker compose -f ops/staging/docker-compose.yml down -v
```

The staging compose file runs:

- 3 mix nodes.
- 1 entry gateway.
- 1 exit gateway.
- 1 DHT node.
- 1 keyring stub.

The current staging service bodies are still scaffold/stub level; the compose stack is useful for packaging, health, and workflow scaffolding, not for a live public mesh.

## Repository Map

| Path | Purpose |
|---|---|
| `aethermesh/common/` | Hashing, AEAD, canonical encoding, DID resolver, PQ backend dispatch, logging/metrics |
| `aethermesh/L3_handshake/` | Handshake and attestation scaffolding |
| `aethermesh/L4_ratchet/` | Ratchet/session scaffolding |
| `aethermesh/L5_captokens/` | CapToken caveats and verifier logic |
| `aethermesh/cli/` | `aethermesh` CLI entrypoint and subcommands |
| `aethermesh/tools/` | Smoke, health, keyring, audit DB, migrations |
| `tests/` | Unit, integration, E2E, property, security, interop scaffolding |
| `ops/` | Dashboards, alerts, runbooks, staging compose, incident notes |
| `scripts/` | Canonical local validation commands |
| `.agent/` | Specs, ExecPlans, ADRs, prompts, checklists |
| `.github/workflows/` | CI, release, staging workflows |

## Security Notes

- Hybrid PQ is mandatory for production.
- Message bodies, private keys, chain keys, and session roots must never be logged.
- Audit receipts store content hashes only.
- Policy logic must fail closed on unknown caveats or missing discharges.
- Keyring-held principal/discharger secrets must not enter the agent runtime address space.
- Production data paths such as `/var/lib/aethermesh/` and `~/.aethermesh/` are off limits unless explicitly authorized.

Read `SECURITY.md`, `PRODUCTION_READINESS.md`, and `.agent/specs/SPEC-008-production-readiness.md` before production-targeted work.

## Working With Agents

Repo-local agent authority is in `AGENTS.md`.

Important rules:

- Read `AGENTS.md`, `COMMANDS.md`, and the active ExecPlan before editing.
- Implement only the active ExecPlan scope.
- Run the milestone validation commands.
- Record decisions and surprises in the active ExecPlan.
- Do not weaken security or production guardrails.
- Do not push release tags or publish artifacts unless explicitly authorized.

Durable compact context for Codex, Serena, Claude Code, and Obsidian lives in `REPO_BRIEF.md`.

## Production Readiness

Production-ready means all of the following are true:

- `./scripts/verify.sh` exits 0.
- `./scripts/production-readiness-check.sh` exits 0.
- Real liboqs-backed ML-KEM/ML-DSA replaces placeholder PQ.
- Two independent implementations pass the interop matrix.
- Performance budgets are recorded and met.
- ADR-0010 is accepted by a human security lead.
- Release and rollback drills are complete.
- PyPI/GHCR publication has been rehearsed safely.

As of the current repo state, only the development verification baseline is green. Production readiness remains blocked.

## License

MIT.
