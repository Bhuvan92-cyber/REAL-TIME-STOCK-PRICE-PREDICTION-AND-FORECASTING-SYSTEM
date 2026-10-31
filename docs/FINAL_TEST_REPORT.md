# Final test report

## Locally executed

- Deterministic backend: **32 passed, 1 live external test deselected**
- Frontend component tests: **2 passed**
- Playwright Chromium public journeys: **2 passed**
- Frontend TypeScript/Vite production build: **passed**
- Python compilation: **passed**
- Migration ordering check: **passed**
- GitHub Actions YAML parsing: **passed**
- Docker Compose config: **passed**
- Frontend `npm audit` including development dependencies: **0 vulnerabilities**
- Frontend production `npm audit --omit=dev --audit-level=high`: **0 vulnerabilities**
- Python 3.12 dependency resolution: **passed as a dry-run only**
- Python 3.12 `pip check`, `pip-audit`, and runtime tests: **CI required; not
  executable on this host because only Python 3.10 is installed**
- Docker image build/runtime: **CI/manual required; Docker daemon unavailable on
  this host**

## Pending

- Actual Python 3.12 installation, `pip check`, and `pip-audit`
- Live Supabase/RLS tests
- Cloud deployment and public URL smoke tests
