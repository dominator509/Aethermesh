# Checklist — Release

- [ ] Version bumped in `pyproject.toml` and `aethermesh.__version__`.
- [ ] `CHANGELOG.md` updated.
- [ ] `RELEASE_NOTES.md` non-empty.
- [ ] All CI green on release commit.
- [ ] RC (`vX.Y.Z-rc.N`) published to TestPyPI.
- [ ] Staging smoke (`./scripts/smoke-test.sh`) exits 0.
- [ ] Tag `vX.Y.Z` pushed.
- [ ] GHA `release.yml` succeeded; wheel on PyPI; images on GHCR.
- [ ] Post-deploy verification per DEPLOYMENT.md (5-min checks).
- [ ] Monitoring active for 72 h.
