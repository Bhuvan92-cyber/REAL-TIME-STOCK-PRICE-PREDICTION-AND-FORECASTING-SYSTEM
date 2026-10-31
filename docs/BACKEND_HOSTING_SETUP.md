# Backend hosting setup

Use `deployment/Dockerfile.api` with a Python 3.12 container service.

Required settings:

- `APP_ENV=production`
- `SUPABASE_URL`
- `SUPABASE_SERVICE_ROLE_KEY`
- `CORS_ORIGINS=https://<frontend-host>`
- `BILLING_ENABLED=false`

Optional settings include `SUPABASE_JWT_SECRET` for legacy HS256 projects,
`ALERT_SCHEDULER_SECRET`, `NEWS_RSS_URL`, `BILLING_WEBHOOK_SECRET`, and
`ADMIN_USER_IDS`. The service starts with Uvicorn on the provider's `PORT`
only if the provider maps it; otherwise use port 8000 as configured by the
Docker image and service metadata.

The image honors the provider's `PORT` environment variable and defaults to
8000 locally. The `/health` endpoint is public and is used by provider health
checks.
