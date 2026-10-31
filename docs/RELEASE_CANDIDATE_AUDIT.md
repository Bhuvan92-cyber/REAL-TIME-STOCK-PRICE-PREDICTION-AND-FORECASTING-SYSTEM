# Release candidate audit

## Status

The release candidate is **not publicly release-ready yet**. Deterministic
backend and frontend checks pass, but Python 3.12 execution, Docker runtime,
live Supabase/RLS, browser execution, and cloud deployment remain
environment-gated.

## Findings

| Severity | Finding | Status |
|---|---|---|
| High | Python 3.12 interpreter is not installed on the current Windows host | CI/Docker verification required |
| High | Docker daemon is unavailable, so image build and runtime health are unverified | Manual/CI action required |
| High | Live Supabase authentication and RLS isolation are unverified | Requires disposable project credentials |
| Medium | `pip-audit` reports transitive Pillow advisories because Streamlit requires Pillow `<13` | Documented residual; reassess Streamlit or Python dependency policy |
| Medium | Authenticated Playwright journeys require isolated Supabase credentials | Pending live test environment |
| Low | Legacy tests emit return-value warnings | Non-blocking cleanup candidate |

The frontend API authorization header and Supabase service-role header were
validated and corrected to use Bearer tokens. No credentials were added to
source files.
