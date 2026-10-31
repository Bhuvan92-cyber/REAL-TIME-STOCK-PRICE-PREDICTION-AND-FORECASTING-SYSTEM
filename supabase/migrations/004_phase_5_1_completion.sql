alter table public.alert_events add column if not exists event_key text;
alter table public.alert_events add column if not exists evaluated_at timestamptz not null default now();
create unique index if not exists alert_events_event_key_idx on public.alert_events(event_key) where event_key is not null;
create table if not exists public.backtest_history (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  symbol text not null,
  model text not null,
  parameters jsonb not null default '{}'::jsonb,
  report jsonb not null,
  evaluation_start date,
  evaluation_end date,
  data_source text not null,
  created_at timestamptz not null default now()
);
create index if not exists backtest_history_user_created_idx on public.backtest_history(user_id, created_at desc);
alter table public.backtest_history enable row level security;
create policy "backtests are user-owned" on public.backtest_history for all using (auth.uid() = user_id) with check (auth.uid() = user_id);
create table if not exists public.alert_execution_logs (
  id uuid primary key default gen_random_uuid(),
  execution_key text unique not null,
  evaluated_at timestamptz not null default now(),
  evaluated_count integer not null default 0,
  triggered_count integer not null default 0,
  failure_count integer not null default 0,
  error text,
  created_at timestamptz not null default now()
);
alter table public.alert_execution_logs enable row level security;
create policy "service role manages alert execution logs" on public.alert_execution_logs for all using (auth.role() = 'service_role') with check (auth.role() = 'service_role');
