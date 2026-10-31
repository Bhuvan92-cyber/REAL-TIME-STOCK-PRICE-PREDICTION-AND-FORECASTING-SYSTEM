# Live deployment guide

This repository is deployment-ready but has not been connected to a cloud
account. No paid service, payment method, domain, or production secret was
created during this phase.

Recommended free architecture:

1. Cloudflare Pages for `frontend` (build command `npm run build`, output
   directory `dist`).
2. Render Free or another approved Python 3.12 service for
   `deployment/Dockerfile.api`. Render Free services sleep after 15 minutes
   and are explicitly not recommended for production.
3. Supabase Free for Auth and PostgreSQL.

Use the provider dashboards to configure secrets; never commit them. Apply
Supabase migrations `001` through `006` only after confirming the target
project and taking an appropriate backup.

Windows PowerShell smoke checks:

```powershell
curl.exe https://<api-host>/health
curl.exe https://<api-host>/api/v1/stocks
Invoke-WebRequest https://<frontend-host>/pricing
```

Do not record a deployment as successful until these URLs and authenticated
flows have been tested.
