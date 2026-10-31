# Final deployment report

## Status

**Deployment status: not performed.** No commit, push, cloud account change,
Supabase migration, payment setup, or public URL was created during Phase 9.

## GitHub repository status

- Remote: `origin` points to the requested GitHub repository.
- Remote connectivity: verified with `git ls-remote`.
- Current branch: `main`.
- Current HEAD: `06aacb5` (`message1`).
- Remote `origin/main`: `06aacb5`; local and remote are aligned.
- Worktree: not clean. It contains the prior application, deployment,
  documentation, dependency, and generated-artifact cleanup changes.
- Safe push status: **not ready for an unattended push**. The changes require
  review and explicit authorization before staging, committing, or pushing.
- Secret-pattern scan: no obvious tracked private-key or service-role secret
  values found. This is not a substitute for provider-side secret review.

## CI/CD status

Workflows are present under `.github/workflows/`:

- `ci.yml`: Python 3.12 checks, pip checks/audit, backend tests, frontend
  audits/tests/build, Playwright, migration validation, and Docker image builds.
- `dependency-audit.yml`: scheduled Python and frontend dependency audits.
- `evaluate-alerts.yml`: scheduled alert evaluation using GitHub secrets.

Actual GitHub Actions execution for the current worktree was **not verified**
because no push or workflow dispatch was authorized. Local results are not
represented as CI results.

## Hosting and Supabase

- Backend provider: not selected or deployed.
- Backend public URL: none.
- Frontend provider: not deployed.
- Frontend public URL: none.
- Supabase project: not confirmed or modified.
- Migrations: local order `001` through `006` is valid; no live database was
  changed.
- Authentication and two-user RLS: not tested against a live project.
- Billing remains disabled.

## Local validation already completed

- Backend: 32 deterministic tests passed; 1 live test deselected.
- Frontend: 2 component tests passed.
- TypeScript validation: passed.
- Production build: passed.
- Playwright: 2 public journeys passed.
- npm audit: 0 vulnerabilities.
- API import and `/health`: passed locally.
- Migration ordering: passed.
- Docker Compose configuration: passed.

The first actual GitHub Actions run for commit `bcafcde` completed with:

- `frontend`: passed.
- `docker`: passed.
- `backend`: failed only at `pip-audit` because Streamlit's transitive Pillow
  `12.3.0` produced 39 advisories. Python installation and `pip check` passed.

The legacy Streamlit dependency set is now separated into
`requirements-streamlit.txt`; the next CI run must verify the production
requirements audit passes.

The next CI run also needs the pinned `httpx` test dependency for Starlette's
`TestClient`; the first Python 3.12 test execution exposed its absence.

The following CI run exposed the intentional optional-ML split: the
deterministic legacy model tests import PyTorch. CI now installs the pinned CPU
PyTorch wheel only for backend tests; the production API image remains free of
the optional deep-learning stack.

Live Supabase isolation, external market-data validation, and public URL smoke
tests remain unverified.

## Required authorization boundary

To proceed with GitHub integration, the owner must first review the dirty
worktree and explicitly authorize staging/committing/pushing a selected set of
changes. Cloud deployment additionally requires authorized provider accounts
and secret configuration through provider dashboards. Do not send passwords,
service-role keys, or private tokens in chat.
