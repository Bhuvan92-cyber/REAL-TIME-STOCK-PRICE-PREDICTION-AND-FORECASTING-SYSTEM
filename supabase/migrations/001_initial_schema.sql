create table if not exists public.profiles (
  id uuid primary key references auth.users(id) on delete cascade,
  display_name text,
  created_at timestamptz not null default now()
);

create table if not exists public.watchlists (
  id bigint generated always as identity primary key,
  user_id uuid not null references auth.users(id) on delete cascade,
  symbol text not null,
  created_at timestamptz not null default now(),
  unique (user_id, symbol)
);

create table if not exists public.prediction_history (
  id bigint generated always as identity primary key,
  user_id uuid not null references auth.users(id) on delete cascade,
  symbol text not null,
  model text not null,
  current_price numeric not null,
  predictions jsonb not null,
  created_at timestamptz not null default now()
);

alter table public.profiles enable row level security;
alter table public.watchlists enable row level security;
alter table public.prediction_history enable row level security;

create policy "profiles are user-owned" on public.profiles for all using (auth.uid() = id) with check (auth.uid() = id);
create policy "watchlists are user-owned" on public.watchlists for all using (auth.uid() = user_id) with check (auth.uid() = user_id);
create policy "predictions are user-owned" on public.prediction_history for all using (auth.uid() = user_id) with check (auth.uid() = user_id);

