# Final release checklist

## Verified

- [x] Deterministic backend tests pass.
- [x] Frontend component tests pass.
- [x] Playwright public browser journeys pass.
- [x] Frontend production build passes.
- [x] Frontend production dependency audit reports zero vulnerabilities.
- [x] Python compilation passes.
- [x] Migration ordering and Compose configuration validate.
- [x] Billing remains disabled by default.
- [x] No credentials were found in the repository scan.

## Required before public launch

- [ ] Install and run Python 3.12 with `pip check` and `pip-audit`.
- [ ] Build and run all Docker services with Docker Desktop or CI.
- [ ] Apply migrations 001-006 to a disposable Supabase project.
- [ ] Execute two-user authentication, RLS, quota, and ownership tests.
- [ ] Configure production CORS, HTTPS, secrets, and external rate limiting.
- [ ] Execute authenticated Playwright journeys with isolated test accounts.
- [ ] Validate market, RSS, model artifact, scheduler, and Supabase providers.
- [ ] Deploy and smoke-test the public frontend/API URLs.

The checklist is intentionally not marked complete while any required
environment-dependent validation remains outstanding.
