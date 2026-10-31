# Supabase production setup

1. Create or select the intended Supabase project.
2. Enable email/password Auth and configure the production site URL and
   redirect URLs.
3. In the SQL editor or Supabase CLI, apply migrations in numeric order:
   `001` through `006`.
4. Configure the API with `SUPABASE_URL` and the server-only
   `SUPABASE_SERVICE_ROLE_KEY`.
5. Configure the browser only with `VITE_SUPABASE_URL` and
   `VITE_SUPABASE_ANON_KEY`.
6. Keep `BILLING_ENABLED=false`.
7. Test two isolated accounts against profiles, watchlists, portfolios,
   transactions, predictions, alerts, notifications, and subscriptions.

Never paste service-role keys into frontend settings, GitHub logs, tickets, or
the repository. Live RLS validation remains pending until a disposable
project and two test accounts are available.
