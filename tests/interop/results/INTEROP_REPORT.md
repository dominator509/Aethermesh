# Interoperability Report

**Generated:** 2026-07-04
**Commit:** `b191b28`
**Implementations tested:** aethermesh (reference); no second implementation available

## Summary
| Vector Set | Tests | Passed | Failed | Skipped |
|---|---|---|---|---|
| SHA3-256 vector scaffold | 1 | 1 | 0 | 0 |
| External wire-format interop | 0 | 0 | 0 | 0 |
| AEAD roundtrip | 0 | 0 | 0 | 0 |
| X25519 DH | 0 | 0 | 0 | 0 |
| CapToken chain | 0 | 0 | 0 | 0 |

## Details
- Validation command `AEP_PQ_BACKEND=liboqs uv run pytest tests/interop --slow -q` exits 0 after repo-local `--slow` option support was added in `tests/conftest.py`.
- The only executed test is `tests/interop/test_vectors_scaffold.py::test_sha3_vectors_load`.
- `tests/interop/external/` is absent, so the required two-implementation matrix from EP-010 cannot be exercised yet.
- No layer-to-layer wire exchange against an external implementation has been performed in this repository state.

## Notes
- All vectors under `tests/vectors/` are labeled `TEST_ONLY`.
- This report is scaffold-only and is not a production interop sign-off artifact.
- Wire-format vectors still need to be tested against two independent implementations.
- Any failure is a protocol bug — do not modify wire format without SPEC change + ADR.
