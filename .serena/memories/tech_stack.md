# Tech Stack

- Intended runtime: Python 3.11+ package managed by `uv`; PEP 621 metadata expected in `pyproject.toml` once implementation files are present.
- Intended tooling from docs: `ruff`, `mypy`, `pytest`, `hypothesis`, `bandit`, `pip-audit`, coverage, SQLite utilities.
- Intended crypto/integration deps: `cryptography`, `oqs`/liboqs for ML-KEM-768 and ML-DSA-65, QUIC integration boundary, MLS library boundary, TEE attestation backends, Sigstore Rekor boundary.
- Current checkout lacks package metadata and implementation tree; treat documented stack as intended until EP-000 verifies actual files.
- Serena config: `.serena/project.yml`, Python language, LSP backend, headless/quiet, ignores caches/build/local DB/Obsidian workspace state only.