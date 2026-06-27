# Checklist — Rollback

- [ ] Rollback trigger identified per ROLLBACK.md.
- [ ] Decision owner (release lead) notified.
- [ ] Rollback type chosen: library / image / config / feature-flag / DB.
- [ ] DB rollback considered: `aethermesh.tools.audit_db migrate --to (N-1)` available?
- [ ] Action executed.
- [ ] Verification per ROLLBACK.md "Verification After Rollback."
- [ ] Communication posted in ops channel (at-decision + at-completion).
- [ ] Postmortem scheduled (within 24 h).
