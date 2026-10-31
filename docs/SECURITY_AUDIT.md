# Security audit

## Controls verified

- Supabase JWT signatures, audience, issuer, expiration, and authenticated
  role are validated by the backend.
- Protected API routes derive ownership from the verified token subject.
- User-specific tables use RLS; migration `006_ownership_hardening.sql`
  additionally verifies child-to-parent ownership.
- Service-role credentials are backend-only and absent from Vite variables.
- Billing webhooks require an HMAC signature and unique provider event ID.
- Scheduler execution requires a backend-only secret.
- Plan administration requires configured administrator IDs.
- API responses add browser security headers and a basic request rate limit.

## Remaining risks

The in-memory rate limiter is process-local and is not a distributed abuse
control. Production deployments with multiple instances should place a
provider or gateway rate limiter in front of the API. Live Supabase policy
behavior, TLS, secret rotation, and provider webhook delivery require
deployment verification.

The Python 3.10 dependency audit currently reports 50 upstream advisories:
three Tornado advisories whose fixes require Tornado 6.6, and transitive
Pillow 12.3.0 advisories whose listed fix is Pillow 13.0.0. Those releases
require Python 3.11, so this repository does not silently raise its Python
floor. FastAPI 0.162.0 and Starlette 1.0.1 are pinned to the latest tested
pair that is installable on the current runtime. Revisit the runtime support
policy before adopting the remaining fixes.
