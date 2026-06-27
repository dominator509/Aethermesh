# Checklist — Incident Response

- [ ] **Detect:** alert firing, source identified.
- [ ] **Triage:** severity (SEV-1..4) assigned per OPERATIONS.md.
- [ ] **Mitigate:** runbook opened (`ops/runbooks/*.md`); steps executed.
- [ ] **Communicate:** ops channel notified with one-line status.
- [ ] **Resolve:** root cause addressed (not just symptom).
- [ ] **Verify:** `./scripts/smoke-test.sh` + relevant alert green for ≥ 10 min.
- [ ] **Document:** incident written into `ops/incidents/YYYY-MM-DD-<slug>.md`.
- [ ] **Follow up:** action items with owners + due dates.
