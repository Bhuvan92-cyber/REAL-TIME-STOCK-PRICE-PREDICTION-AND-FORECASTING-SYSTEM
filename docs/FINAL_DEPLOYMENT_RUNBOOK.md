# Final deployment runbook

This runbook deploys the existing React/FastAPI/Supabase application without
adding paid services or requiring payment-card registration. It assumes
Cloudflare Pages for the frontend, Render Free for a demo/testing API, and
Supabase Free for Auth/PostgreSQL. Free-tier availability and signup
requirements must be confirmed in the provider account UI; no account was
created from this repository.

## Step 1: Prepare the repository and final branch

**Dashboard location:** GitHub repository, branch selector and Actions tab.

**Commands (Windows 11 PowerShell):**

```powershell
git fetch --all --prune
git switch <release-branch>
git pull --ff-only
git status --short
git log -1 --oneline
```

Confirm that the intended commit contains the migration files, `frontend/`,
`api/`, deployment files, and CI workflows. Do not commit `.env`, service-role
keys, generated artifacts, or unrelated worktree changes.

**Expected result:** clean release branch and a reproducible commit SHA.

**Common errors/recovery:** If `git pull --ff-only` reports divergence, stop
and resolve it in a separate branch; do not reset or discard work.

## Step 2: Create and configure Supabase

**Dashboard location:** Supabase Dashboard > New project > Project Settings >
API.

Create a Free project only if the account permits card-free signup. Record the
project URL, anon key, and service-role key in the approved secret manager.
Never paste the service-role key into GitHub issues, frontend settings, or logs.

**Expected result:** a reachable project with Auth and PostgreSQL enabled.

**Common errors/recovery:** If signup requests payment information, stop and
retain the local/CI deployment path; do not bypass provider requirements.

## Step 3: Apply database migrations

**Dashboard location:** Supabase Dashboard > SQL Editor, or the Supabase CLI
linked to the confirmed project.

From the repository root, verify order:

```powershell
Get-ChildItem supabase\migrations\*.sql | Sort-Object Name
```

Apply `001` through `006` exactly once and in numeric order. Use the CLI for
repeatable deployment where available:

```powershell
supabase link --project-ref <project-ref>
supabase db push
```

**Expected result:** all six migrations appear in Supabase > Database >
Migrations without errors.

**Common errors/recovery:** Do not rerun partially applied SQL blindly. Inspect
the migration history, back up as appropriate, and resolve the specific failed
statement before continuing.

## Step 4: Configure authentication and RLS

**Dashboard location:** Supabase Dashboard > Authentication > Providers and
URL Configuration; Database > Policies.

Enable Email provider/password authentication. Set the production frontend
site URL and redirect URLs for `/reset-password`. Confirm RLS is enabled for
user-owned tables and that policies use `auth.uid()` plus parent ownership
checks.

Create two disposable test users. Verify User A cannot select, update, or
delete User B's profiles, watchlists, watchlist items, portfolios, assets,
transactions, snapshots, predictions, alerts, or alert events.

**Expected result:** both users can authenticate, but ownership isolation is
preserved.

**Common errors/recovery:** A missing redirect URL requires updating the
allow-list, not weakening frontend or database checks. Revoke disposable test
users after validation.

## Step 5: Deploy the FastAPI backend

**Dashboard location:** Render Dashboard > New > Web Service > Existing Image
or repository deployment settings.

Select the repository, Docker runtime, and
`deployment/Dockerfile.api`. Set the health check path to `/health`. The image
uses Python 3.12 and honors the provider `PORT` variable, defaulting to 8000.

**Expected result:** Render creates a service and reports a healthy instance.

**Common errors/recovery:** A sleeping Free instance is expected after
inactivity. Build failures should be reproduced with
`docker build -f deployment/Dockerfile.api .` in CI or locally when Docker is
available.

## Step 6: Configure backend environment variables

**Dashboard location:** Render service > Environment.

Set these backend variables:

```text
APP_ENV=production
PORT=<provider-assigned-port, if required>
SUPABASE_URL=<project-url>
SUPABASE_SERVICE_ROLE_KEY=<server-only-secret>
SUPABASE_ANON_KEY=<public-anon-key>
CORS_ORIGINS=https://<frontend-host>
BILLING_ENABLED=false
```

Optionally set `SUPABASE_JWT_SECRET` only for legacy HS256 projects,
`ALERT_SCHEDULER_SECRET`, `NEWS_RSS_URL`, `BILLING_WEBHOOK_SECRET`, and
`ADMIN_USER_IDS`. Do not expose backend-only values through `VITE_` variables.

**Expected result:** the service starts and `/health` returns success.

**Common errors/recovery:** A production startup error for missing Supabase
configuration means a required secret is absent. Correct the environment and
redeploy; never downgrade `APP_ENV` to hide the error.

## Step 7: Deploy the React frontend

**Dashboard location:** Cloudflare Dashboard > Workers & Pages > Create
application > Pages > Connect to Git.

Set the project root to `frontend`, build command to `npm ci && npm run build`,
and output directory to `dist`. The repository's
`frontend/public/_redirects` and Vite fallback preserve client-side routes.

**Expected result:** Cloudflare provides an HTTPS Pages hostname and a
successful build.

**Common errors/recovery:** A refresh returning 404 indicates the SPA fallback
is missing or the wrong output directory was selected. Confirm both settings
and redeploy.

## Step 8: Configure frontend environment variables

**Dashboard location:** Cloudflare Pages project > Settings > Environment
variables.

Set only:

```text
VITE_API_URL=https://<api-host>
VITE_SUPABASE_URL=<project-url>
VITE_SUPABASE_ANON_KEY=<public-anon-key>
```

**Expected result:** the deployed bundle points to the HTTPS API and Supabase
project. The anon key is public; the service-role key is absent.

**Common errors/recovery:** Browser CORS failures require correcting the API
`CORS_ORIGINS` value to the exact Pages origin, then restarting the API.

## Step 9: Connect frontend and backend

**Dashboard location:** Render service logs and Cloudflare Pages deployment
logs.

Redeploy the frontend after setting variables. Open the browser developer
network panel and confirm requests use the API host and
`Authorization: Bearer <access_token>` for protected calls.

**Expected result:** public pages load and protected pages redirect to login
when no session exists.

**Common errors/recovery:** A 401 indicates missing/expired authentication;
refresh or sign in again. A 403/CORS error indicates API configuration, not a
reason to make the route public.

## Step 10: Run public API smoke tests

```powershell
$api = "https://<api-host>"
$web = "https://<frontend-host>"
Invoke-WebRequest "$api/health"
Invoke-WebRequest "$api/api/v1/stocks"
Invoke-WebRequest "$web/"
Invoke-WebRequest "$web/pricing"
```

**Expected result:** HTTPS responses succeed; market responses identify their
provider and unavailable data explicitly.

**Common errors/recovery:** A 5xx or timeout may be a Render cold start or
provider failure. Retry once, inspect logs, then distinguish API failure from
external market-data unavailability.

## Step 11: Run authentication and user-isolation tests

Using the two disposable accounts, verify registration, login, logout,
password recovery/reset, session expiry, protected-route redirects, and
ownership isolation for every private resource.

**Expected result:** only the owning account can access private records.

**Common errors/recovery:** Reset links must use the configured production
redirect. Delete test data and accounts after evidence is captured without
recording credentials or tokens.

## Step 12: Validate forecasting, portfolios, watchlists, and alerts

From the deployed UI, verify:

- Watchlist create/rename/delete, stock search, add/remove, and quote refresh.
- Portfolio create/rename/delete, holdings, allocation, valuation, and
  unavailable-price states.
- Forecast request limits, registered model availability, history save/delete,
  and export.
- Alert creation, cooldown/duplicate behavior, notification retrieval, and
  scheduled evaluation when configured.

**Expected result:** persisted operations survive refresh and no unavailable
market price is displayed as zero.

**Common errors/recovery:** External Yahoo/RSS/model outages must appear as
explicit unavailable/provider errors. Do not fabricate values or bypass limits.

## Step 13: Verify production logs and health checks

**Dashboard location:** Render service > Logs and Metrics; Cloudflare Pages >
Deployments; Supabase > Logs.

Check startup, `/health`, authentication failures, rate limits, database
errors, provider latency, scheduler responses, and quota usage. Confirm no
access tokens, service-role keys, webhook secrets, or passwords appear.

**Expected result:** healthy service with actionable, secret-free logs.

**Common errors/recovery:** For an incident, disable the affected scheduler or
provider, preserve redacted logs, roll back application code, and re-test
health/authentication/ownership before reopening traffic.

## Step 14: Record final public URLs

Record the deployment commit SHA, frontend URL, API URL, Supabase project
reference (not secrets), deployment timestamps, smoke-test results, and known
free-tier limitations in the release record.

**Expected result:** URLs are recorded only after actual public requests and
authenticated tests succeed.

**Common errors/recovery:** If any step remains account-dependent or unverified,
label it pending rather than claiming public deployment.

## Environment variable audit

| Variable | Component | Required | Secret/public | Example | Configure in |
|---|---|---:|---|---|---|
| `APP_ENV` | Backend | Yes in production | Non-secret | `production` | Render |
| `PORT` | Backend | Provider-dependent | Non-secret | `8000` | Render |
| `SUPABASE_URL` | Backend/frontend | Yes | Public URL | `https://project.supabase.co` | Render/Cloudflare |
| `SUPABASE_ANON_KEY` | Backend | Optional | Public | `<anon-key>` | Render |
| `SUPABASE_SERVICE_ROLE_KEY` | Backend | Yes | Secret | `<service-role-key>` | Render |
| `SUPABASE_JWT_SECRET` | Backend | Legacy only | Secret | `<jwt-secret>` | Render |
| `CORS_ORIGINS` | Backend | Yes | Non-secret | `https://frontend.example` | Render |
| `NEWS_RSS_URL` | Backend | Optional | Non-secret | `<rss-url>` | Render |
| `ALERT_SCHEDULER_SECRET` | Backend | Optional | Secret | `<scheduler-secret>` | Render/GitHub |
| `BILLING_ENABLED` | Backend | Yes | Non-secret | `false` | Render |
| `BILLING_WEBHOOK_SECRET` | Backend | Optional | Secret | `<webhook-secret>` | Render |
| `ADMIN_USER_IDS` | Backend | Optional | Sensitive identifiers | `<user-id>` | Render |
| `VITE_API_URL` | Frontend | Yes | Public | `https://api.example` | Cloudflare |
| `VITE_SUPABASE_URL` | Frontend | Yes | Public URL | `https://project.supabase.co` | Cloudflare |
| `VITE_SUPABASE_ANON_KEY` | Frontend | Yes | Public | `<anon-key>` | Cloudflare |

`BILLING_ENABLED` remains `false`. No payment gateway or paid service is
activated by this runbook.
