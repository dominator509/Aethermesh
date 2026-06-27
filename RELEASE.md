# RELEASE

## Release Types
- **Library** (SemVer 1.x): `aethermesh` PyPI wheel.
- **Protocol** (AEP-1.x): wire-format version; backward-compat within major.
- **Mix node / gateway images** (GHCR, mirror library SemVer).

A protocol-breaking release requires a new major (AEP-2.x) and library major.

## Versioning
- Library: SemVer (`MAJOR.MINOR.PATCH`).
- Pre-release: `vX.Y.Z-rc.N`.
- Protocol: `aethermesh.__protocol_version__ = "1.0"`.

## Changelog
Keep a Changelog format in `CHANGELOG.md`. Sections: Added / Changed / Deprecated / Removed / Fixed / Security.

## Branch Strategy
- Trunk-based on `main`.
- Optional release branches `release/x.y` for back-porting security fixes.
- Short-lived feature branches: `feat/<slug>`, `fix/<slug>`, `chore/<slug>`.

## Release Candidate Criteria
- All PRODUCTION_READINESS.md gates pass.
- Two-impl interop matrix passes against pinned reference.
- 72 h staging soak without SEV-1 / SEV-2.
- Release notes draft in `RELEASE_NOTES.md`.

## Release Checklist
- [ ] All CI green on `main` at release commit.
- [ ] `CHANGELOG.md` updated.
- [ ] `RELEASE_NOTES.md` non-empty.
- [ ] Bump `pyproject.toml` version + `aethermesh.__version__`.
- [ ] Tag `vX.Y.Z` (or `vX.Y.Z-rc.N`).
- [ ] GHA workflow `release.yml` succeeds.
- [ ] PyPI page shows the wheel.
- [ ] GHCR shows the new tag.
- [ ] Staging operators pulled new image and smoke succeeded.

## Smoke Tests (Staging)
```sh
./scripts/smoke-test.sh
docker exec aethermesh-mix-1 \
  python -m aethermesh.tools.smoke --target self --lane fast --timeout 5
```

## Approvals
- Library release: 2 reviewers, ≥ 1 `protocol-owner`.
- Image release: 1 reviewer.
- Protocol-affecting change: 2 reviewers + ADR.

## Release Notes Template
```
## vX.Y.Z — YYYY-MM-DD
### Added
- ...
### Changed
- ...
### Deprecated
- ...
### Removed
- ...
### Fixed
- ...
### Security
- ...
```

## Post-Release Monitoring (72 h window)
- Dashboards under continuous watch.
- Burn rate vs SLOs reviewed daily.
- Any SEV-1 / SEV-2 in 72 h triggers ROLLBACK.md.

## Publishing
- PyPI: `uv publish` in GHA with OIDC token.
- GHCR: `docker push ghcr.io/<org>/aethermesh-mix-node:X.Y.Z` and `aethermesh-gateway:X.Y.Z`.
