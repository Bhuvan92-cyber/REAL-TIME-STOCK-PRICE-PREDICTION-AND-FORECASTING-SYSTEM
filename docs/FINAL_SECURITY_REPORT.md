# Final security report

## Verified

- Backend derives ownership from validated JWT subjects.
- Frontend sends access tokens through `Authorization: Bearer`.
- Service-role authorization is backend-only.
- Migration 006 checks parent ownership for child records.
- Billing is disabled by default.
- Webhook handling and scheduler routes require configured secrets.
- Production frontend audit reports zero production vulnerabilities.

## Not yet verified

- Live Supabase JWT/JWKS behavior and RLS with two real users.
- External TLS, gateway rate limiting, secret rotation, and cloud IAM.
- Python 3.12 `pip-audit` execution.

The release must not be described as a clean security audit until those
environment-dependent checks are completed.
