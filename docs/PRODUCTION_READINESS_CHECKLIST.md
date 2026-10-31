# Production readiness checklist

- [ ] Apply Supabase migrations `001` through `006` in order.
- [ ] Verify parent-child RLS isolation with two test users.
- [ ] Configure production `APP_ENV`, CORS origins, Supabase URL, service key,
  JWT verification, and scheduler secret.
- [ ] Keep `BILLING_ENABLED=false` until a real provider and webhook
  verification process are approved.
- [ ] Run backend tests, compilation, frontend build, and dependency audits.
- [ ] Deploy the API with a health check and inspect cold-start behavior.
- [ ] Configure frontend `VITE_API_URL`, Supabase URL, and anon key only.
- [ ] Confirm TLS, external rate limiting, backups, and secret rotation.
- [ ] Review market/news provider terms and financial disclaimers.
# Runtime and test status

- [ ] Python 3.12 runtime execution verified on the deployment host.
- [ ] `python -m pytest -m "not live_external"` passes in a clean Python 3.12 environment.
- [ ] `pip-audit` is reviewed under Python 3.12 and remaining advisories are documented.
- [ ] Docker image build and container health verified with Docker Desktop or CI.
