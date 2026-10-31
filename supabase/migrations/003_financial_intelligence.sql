create table if not exists public.portfolio_transactions (
  id uuid primary key default gen_random_uuid(),
  portfolio_id bigint not null references public.portfolios(id) on delete cascade,
  user_id uuid not null references auth.users(id) on delete cascade,
  symbol text not null,
  side text not null check (side in ('buy', 'sell')),
  quantity numeric not null check (quantity > 0),
  price numeric not null check (price > 0),
  fee numeric not null default 0 check (fee >= 0),
  executed_at timestamptz not null default now(),
  created_at timestamptz not null default now()
);
create table if not exists public.portfolio_snapshots (
  id uuid primary key default gen_random_uuid(),
  portfolio_id bigint not null references public.portfolios(id) on delete cascade,
  user_id uuid not null references auth.users(id) on delete cascade,
  snapshot_date date not null,
  invested numeric not null,
  market_value numeric,
  created_at timestamptz not null default now(),
  unique (portfolio_id, snapshot_date)
);
create table if not exists public.alert_rules (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  symbol text not null,
  condition text not null check (condition in ('above', 'below')),
  threshold numeric not null check (threshold > 0),
  cooldown_minutes integer not null default 60 check (cooldown_minutes >= 0),
  active boolean not null default true,
  last_triggered_at timestamptz,
  created_at timestamptz not null default now()
);
create table if not exists public.alert_events (
  id uuid primary key default gen_random_uuid(),
  alert_id uuid not null references public.alert_rules(id) on delete cascade,
  user_id uuid not null references auth.users(id) on delete cascade,
  observed_price numeric not null,
  triggered_at timestamptz not null default now()
);
create table if not exists public.notifications (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  category text not null,
  title text not null,
  body text not null,
  read_at timestamptz,
  created_at timestamptz not null default now()
);
create table if not exists public.market_news (
  id uuid primary key default gen_random_uuid(),
  symbol text not null,
  title text not null,
  url text not null unique,
  source text not null,
  published_at timestamptz,
  created_at timestamptz not null default now()
);
create table if not exists public.sentiment_records (
  id uuid primary key default gen_random_uuid(),
  news_id uuid not null references public.market_news(id) on delete cascade,
  label text not null check (label in ('positive', 'neutral', 'negative')),
  score numeric not null,
  created_at timestamptz not null default now(),
  unique (news_id)
);
create index if not exists alert_rules_user_idx on public.alert_rules(user_id);
create index if not exists notifications_user_created_idx on public.notifications(user_id, created_at desc);
create index if not exists market_news_symbol_created_idx on public.market_news(symbol, created_at desc);
alter table public.portfolio_transactions enable row level security;
alter table public.portfolio_snapshots enable row level security;
alter table public.alert_rules enable row level security;
alter table public.alert_events enable row level security;
alter table public.notifications enable row level security;
alter table public.market_news enable row level security;
alter table public.sentiment_records enable row level security;
create policy "portfolio transactions are user-owned" on public.portfolio_transactions for all using (auth.uid() = user_id) with check (auth.uid() = user_id);
create policy "portfolio snapshots are user-owned" on public.portfolio_snapshots for all using (auth.uid() = user_id) with check (auth.uid() = user_id);
create policy "alerts are user-owned" on public.alert_rules for all using (auth.uid() = user_id) with check (auth.uid() = user_id);
create policy "alert events are user-owned" on public.alert_events for all using (auth.uid() = user_id) with check (auth.uid() = user_id);
create policy "notifications are user-owned" on public.notifications for all using (auth.uid() = user_id) with check (auth.uid() = user_id);
create policy "news is public" on public.market_news for select using (true);
create policy "sentiment is public" on public.sentiment_records for select using (true);
