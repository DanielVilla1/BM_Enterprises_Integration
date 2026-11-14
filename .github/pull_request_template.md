## What changed

## Definition of Done (spec section 12 / proposal)

- [ ] Acceptance criteria demonstrated
- [ ] Formatting, lint and tests pass (CI green)
- [ ] OpenAPI snapshot updated (`python -m backend.scripts.export_openapi`) when the contract changed
- [ ] Role / permission checks present; new endpoints have a capability in the permission matrix
- [ ] Migrations apply cleanly
- [ ] No secrets, real personal data or production credentials in the change

## AI assistance

- [ ] This change was AI-assisted
- Verification performed (what was checked by a human):

## Security review

Required from the named security reviewer when the change touches authentication, authorization, payroll, billing, uploads or migrations.

- [ ] Not applicable
- [ ] Reviewer approved: @
- New or changed dependencies (exist, real history, needed):
