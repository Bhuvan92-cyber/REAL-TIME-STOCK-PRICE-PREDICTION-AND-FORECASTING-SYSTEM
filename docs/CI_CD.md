# CI/CD

`.github/workflows/ci.yml` runs Python compilation/tests, frontend TypeScript
builds, and npm production dependency auditing on pushes and pull requests.
`.github/workflows/dependency-audit.yml` runs scheduled `pip-audit` on Python
3.12; its
result must be reviewed before releases.

Cloud deployment is intentionally not automated in this repository because
provider credentials and deployment ownership are not available.
