# Final deployment guide

## Local Windows PowerShell

```powershell
py -3.12 -m venv .venv312
.\.venv312\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
Copy-Item .env.example .env
python -m pytest -m "not live_external" -q
docker compose -f deployment/docker-compose.yml config
docker compose -f deployment/docker-compose.yml up --build
```

The current host has Python 3.10 and no running Docker daemon, so these
runtime commands require Python 3.12/Docker Desktop or CI.

## Cloud split

1. Apply Supabase migrations `001` through `006`.
2. Deploy `frontend` to Cloudflare Pages with `VITE_API_URL`,
   `VITE_SUPABASE_URL`, and `VITE_SUPABASE_ANON_KEY`.
3. Deploy `deployment/Dockerfile.api` to a Python 3.12 container service.
4. Configure backend-only Supabase service-role, JWT, scheduler, and billing
   secrets in the hosting provider.
5. Set production `CORS_ORIGINS` to the exact HTTPS frontend origin.

Do not expose service-role keys or billing secrets to Vite.
