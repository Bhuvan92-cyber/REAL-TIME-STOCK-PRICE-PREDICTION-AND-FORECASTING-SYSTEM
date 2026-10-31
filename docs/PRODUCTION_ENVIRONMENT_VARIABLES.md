# Production environment variables

## Backend-only

| Variable | Required | Notes |
|---|---|---|
| `APP_ENV` | Yes | Set to `production` |
| `SUPABASE_URL` | Yes | Project URL |
| `SUPABASE_SERVICE_ROLE_KEY` | Yes | Secret; never expose to Vite |
| `CORS_ORIGINS` | Yes | Exact HTTPS frontend origin(s) |
| `BILLING_ENABLED` | Yes | Keep `false` |
| `SUPABASE_JWT_SECRET` | No | Legacy HS256 only |
| `ALERT_SCHEDULER_SECRET` | No | Required for scheduler endpoint |
| `NEWS_RSS_URL` | No | RSS provider URL |
| `BILLING_WEBHOOK_SECRET` | No | Only for a real provider |

## Frontend-public

| Variable | Required | Notes |
|---|---|---|
| `VITE_API_URL` | Yes | HTTPS API origin |
| `VITE_SUPABASE_URL` | Yes | Public project URL |
| `VITE_SUPABASE_ANON_KEY` | Yes | Public anon key only |

Missing optional provider keys must not prevent startup. Rotate secrets through
the hosting provider and never print them in diagnostics.
