# Interoperability Report

**Generated:** <timestamp>
**Commit:** <commit-hash>
**Implementations tested:** aethermesh (reference)

## Summary
| Vector Set | Tests | Passed | Failed | Skipped |
|---|---|---|---|---|
| SHA3-256 NIST | - | - | - | - |
| AEAD roundtrip | - | - | - | - |
| X25519 DH | - | - | - | - |
| CapToken chain | - | - | - | - |

## Details
<per-vector results>

## Notes
- All vectors under `tests/vectors/` are labeled `TEST_ONLY`.
- Wire-format vectors tested against two independent implementations.
- Any failure is a protocol bug — do not modify wire format without SPEC change + ADR.
