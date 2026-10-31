# Final architecture audit

## Scope

The audit covered the FastAPI API, React/Vite application, Supabase
migrations, authentication, entitlement service, market-data and RSS
providers, portfolio/backtesting/alert modules, Docker files, CI workflows,
environment templates, and tests.

## Findings and disposition

| Severity | Finding | Disposition |
|---|---|---|
| High | Child-table RLS checked only `user_id`, not ownership of the referenced parent resource. | Fixed in migration `006_ownership_hardening.sql` with parent `EXISTS` checks. |
| Medium | API container and legacy Streamlit container shared an image whose default command and file set were inconsistent. | Fixed with dedicated API and Streamlit images plus Compose health dependencies. |
| Medium | No CI workflow ran backend/frontend tests and builds together. | Added `.github/workflows/ci.yml`. |
| Medium | No baseline API security headers or request throttling existed. | Added security headers and a bounded in-memory per-client rate limiter. |
| Low | Production frontend bundle exceeds Vite’s 500 kB warning threshold. | Documented; code splitting remains a future optimization. |
| Low | Live provider, Supabase, payment, and cloud deployment behavior cannot be validated without credentials. | Explicitly documented; no live-success claim is made. |

The security review found no additional concrete authentication, JWT,
webhook-signature, scheduler-token, or frontend-secret exposure defects.
Production CORS, deployed RLS, TLS termination, and provider configuration
remain deployment-time verification items.
