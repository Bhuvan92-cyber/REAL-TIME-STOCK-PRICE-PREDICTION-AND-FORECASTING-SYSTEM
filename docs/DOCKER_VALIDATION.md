# Docker validation

Compose configuration is validated with:

```powershell
docker compose -f deployment/docker-compose.yml config
```

The API, Streamlit, and frontend images use Python 3.12 where applicable,
non-root users for Python services, health checks, and explicit startup
commands. The frontend remains an Nginx container.

Image build and runtime commands:

```powershell
docker compose -f deployment/docker-compose.yml build
docker compose -f deployment/docker-compose.yml up -d
docker compose -f deployment/docker-compose.yml ps
docker compose -f deployment/docker-compose.yml logs
```

If Docker Desktop is unavailable, only static Compose validation can be
claimed; image and health endpoint execution must remain unverified.
