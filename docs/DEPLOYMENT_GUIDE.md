# Deployment guide

## Windows 11 local setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
npm install --prefix frontend
Copy-Item .env.example .env
$env:PYTHONPATH = "."
uvicorn api.main:app --reload --port 8000
```

In another PowerShell terminal:

```powershell
npm run dev --prefix frontend
```

## Docker Compose

```powershell
docker compose -f deployment\docker-compose.yml up --build
```

The API is exposed on port 8000, Streamlit on 8501, and the static frontend
on 8080. Docker Desktop must be running. Compose uses non-root API/Streamlit
containers and health checks.

## Cloud

Configure the frontend as a static Cloudflare Pages project with the
`frontend` directory, `npm ci` build dependencies, `npm run build` command,
and `dist` output. Configure the backend as a Render Docker web service using
`deployment/Dockerfile.api` and `/health`. Set secrets in the provider
environment configuration, never in the repository.
