create table if not exists public.watchlist_items (
  id bigint generated always as identity primary key,
  watchlist_id bigint not null references public.watchlists(id) on delete cascade,
  user_id uuid not null references auth.users(id) on delete cascade,
  symbol text not null,
  created_at timestamptz not null default now(),
  unique (watchlist_id, symbol)
);

alter table public.watchlists add column if not exists name text;
insert into public.watchlist_items (watchlist_id, user_id, symbol)
select id, user_id, symbol from public.watchlists
where symbol is not null
on conflict (watchlist_id, symbol) do nothing;
update public.watchlists set name = coalesce(name, 'Default watchlist');
alter table public.watchlists alter column name set not null;
alter table public.watchlists drop constraint if exists watchlists_user_id_symbol_key;
alter table public.watchlists drop column if exists symbol;

alter table public.prediction_history add column if not exists horizon integer not null default 1;
alter table public.prediction_history add column if not exists model_version text not null default 'unknown';
alter table public.prediction_history add column if not exists evaluation_metadata jsonb not null default '{}'::jsonb;

create table if not exists public.portfolios (
  id bigint generated always as identity primary key,
  user_id uuid not null references auth.users(id) on delete cascade,
  name text not null,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists public.portfolio_assets (
  id bigint generated always as identity primary key,
  portfolio_id bigint not null references public.portfolios(id) on delete cascade,
  user_id uuid not null references auth.users(id) on delete cascade,
  symbol text not null,
  quantity numeric not null check (quantity > 0),
  purchase_price numeric not null check (purchase_price > 0),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique (portfolio_id, symbol)
);

create table if not exists public.user_preferences (
  user_id uuid primary key references auth.users(id) on delete cascade,
  theme text not null default 'dark',
  currency text not null default 'USD',
  updated_at timestamptz not null default now()
);

create table if not exists public.plans (
  id text primary key,
  name text not null,
  limits jsonb not null
);

insert into public.plans (id, name, limits) values
  ('free', 'Free', '{"watchlists": 2, "portfolios": 1, "forecast_requests": 20, "prediction_history": 50, "advanced_analytics": false}')
on conflict (id) do nothing;

create table if not exists public.user_entitlements (
  user_id uuid primary key references auth.users(id) on delete cascade,
  plan_id text not null references public.plans(id) default 'free',
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists public.usage_records (
  id bigint generated always as identity primary key,
  user_id uuid not null references auth.users(id) on delete cascade,
  metric text not null,
  period_start date not null default current_date,
  usage_count integer not null default 0 check (usage_count >= 0),
  unique (user_id, metric, period_start)
);

create index if not exists watchlists_user_id_idx on public.watchlists(user_id);
create index if not exists watchlist_items_user_id_idx on public.watchlist_items(user_id);
create index if not exists portfolios_user_id_idx on public.portfolios(user_id);
create index if not exists portfolio_assets_user_id_idx on public.portfolio_assets(user_id);
create index if not exists prediction_history_user_created_idx on public.prediction_history(user_id, created_at desc);

alter table public.watchlist_items enable row level security;
alter table public.portfolios enable row level security;
alter table public.portfolio_assets enable row level security;
alter table public.user_preferences enable row level security;
alter table public.plans enable row level security;
alter table public.user_entitlements enable row level security;
alter table public.usage_records enable row level security;

create policy "watchlist items are user-owned" on public.watchlist_items for all using (auth.uid() = user_id) with check (auth.uid() = user_id);
create policy "portfolios are user-owned" on public.portfolios for all using (auth.uid() = user_id) with check (auth.uid() = user_id);
create policy "portfolio assets are user-owned" on public.portfolio_assets for all using (auth.uid() = user_id) with check (auth.uid() = user_id);
create policy "preferences are user-owned" on public.user_preferences for all using (auth.uid() = user_id) with check (auth.uid() = user_id);
create policy "plans are readable" on public.plans for select using (true);
create policy "entitlements are user-owned" on public.user_entitlements for select using (auth.uid() = user_id);
create policy "usage is user-owned" on public.usage_records for all using (auth.uid() = user_id) with check (auth.uid() = user_id);

create or replace function public.handle_new_user()
returns trigger language plpgsql security definer set search_path = public as $$
begin
  insert into public.profiles (id, display_name) values (new.id, coalesce(new.raw_user_meta_data->>'display_name', new.email));
  insert into public.user_entitlements (user_id, plan_id) values (new.id, 'free');
  insert into public.user_preferences (user_id) values (new.id);
  return new;
end;
$$;

drop trigger if exists on_auth_user_created on auth.users;
create trigger on_auth_user_created after insert on auth.users
for each row execute procedure public.handle_new_user();
