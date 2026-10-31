# Dependency security report

Audit command: `pip-audit -r requirements.txt --format json`  
Audit date: 2026-10-31  
Audit interpreter: Python 3.10.0 (the workstation does not currently have
Python 3.12 installed)

The audit found **50 vulnerability records across three packages**. The
reported database does not provide CVSS severity in this output; therefore
severity is recorded as **unscored** rather than guessed. Duplicate records
reported by the advisory database are retained in the count but consolidated
below by identifier.

| Package | Version | Direct/transitive | Advisory identifiers | Fixed version reported |
|---|---:|---|---|---|
| tornado | 6.5.10 | Direct | CVE-2026-116577, CVE-2026-115927, CVE-2026-116578 | 6.6 |
| starlette | 1.0.1 | Direct | PYSEC-2026-2281, PYSEC-2026-2280, PYSEC-2026-249, PYSEC-2026-248 | 1.1.0, 1.3.1, 1.3.0 |
| pillow | 12.3.0 | Transitive via Streamlit | PYSEC-2026-4327, PYSEC-2026-4328, PYSEC-2026-4326, PYSEC-2026-4339, PYSEC-2026-4340, PYSEC-2026-4343, PYSEC-2026-4334, PYSEC-2026-4337, PYSEC-2026-4341, PYSEC-2026-4330, PYSEC-2026-4338, PYSEC-2026-4335, PYSEC-2026-4336, PYSEC-2026-4331, PYSEC-2026-4332, PYSEC-2026-4329, PYSEC-2026-4333, PYSEC-2026-4342, CVE-2026-112895, CVE-2026-112400, CVE-2026-112897, CVE-2026-112395, CVE-2026-112404, CVE-2026-112899, CVE-2026-112900, CVE-2026-112893, CVE-2026-112891, CVE-2026-112390, CVE-2026-112401, CVE-2026-112391, CVE-2026-112894, CVE-2026-112406, CVE-2026-112399, CVE-2026-112892, CVE-2026-112393, CVE-2026-96638, CVE-2026-96640, CVE-2026-96778, GHSA-78g4-xqwv-q3g8 | 13.0.0 |

## Remediation

- FastAPI `0.162.0` and Starlette `1.3.1` are pinned as a compatible pair.
- Tornado `6.6` requires Python 3.11 or newer according to the package index.
  Python 3.12 is now the preferred runtime, so the clean Python 3.12 CI/Docker
  audit is the required follow-up verification.
- The current Python 3.10 workstation cannot install those fixed versions
  without violating the supported runtime constraint. The target Python 3.12
  requirements now select those fixed versions; the remaining risk must be
  re-audited on Python 3.12.
- Streamlit `1.54.0` currently constrains Pillow to `<13`; Pillow `13.0.0`
  cannot be forced without breaking dependency resolution. The Pillow
  advisories remain a documented transitive risk until Streamlit lifts that
  constraint or the legacy Streamlit surface is removed.
- A Python 3.12-targeted pip resolution completed successfully with the
  selected requirements. It selected Tornado `6.6`, Starlette `1.3.1`, and
  Pillow `12.3.0`; this is a compatibility check, not a replacement for
  running `pip-audit` under an actual Python 3.12 interpreter.
- Optional deep-learning dependencies were removed from the base install and
  placed in the pinned `ml_cpu` extra to reduce the default attack surface and
  installation cost.

This report must be regenerated in Python 3.12 before release. Do not approve
production deployment based solely on the Python 3.10 audit.

## Frontend audit

On 2026-10-31, `npm audit` and
`npm audit --omit=dev --audit-level=high` both reported **0 vulnerabilities**.
The prior eight development-only findings were resolved by upgrading Vitest
to `5.0.5` and `@playwright/test` to `1.55.1`; the lockfile was regenerated
with `npm install`, not `npm audit fix --force`. The existing TypeScript,
Vitest, Vite, React Testing Library, and Playwright checks pass after the
upgrade.
