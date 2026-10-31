alter table public.plans add column if not exists features jsonb not null default '[]'::jsonb;
alter table public.plans add column if not exists updated_at timestamptz not null default now();
alter table public.usage_records add column if not exists created_at timestamptz not null default now();
alter table public.usage_records add column if not exists reset_at timestamptz;

update public.plans
set features = case id
  when 'free' then '["market_overview","basic_technical_analysis","basic_forecasting","basic_backtesting"]'::jsonb
  when 'pro' then '["advanced_technical_analysis","advanced_portfolio_analytics","advanced_backtesting","exports"]'::jsonb
  when 'premium' then '["ensemble_forecasting","advanced_model_intelligence","advanced_portfolio_analytics","advanced_backtesting","exports","api_access"]'::jsonb
  else features
end;

insert into public.plans (id, name, limits, features)
values
  ('free', 'Free', '{"forecast_requests":{"period":"day","value":20},"advanced_model_usage":{"period":"day","value":0},"backtest_executions":{"period":"day","value":5},"portfolios":{"period":"total","value":1},"watchlists":{"period":"total","value":2},"stock_alerts":{"period":"total","value":3},"prediction_history":{"period":"total","value":50},"data_exports":{"period":"month","value":0},"api_access":{"period":"month","value":0}}', '["market_overview","basic_technical_analysis","basic_forecasting","basic_backtesting"]'),
  ('pro', 'Pro', '{"forecast_requests":{"period":"day","value":200},"advanced_model_usage":{"period":"day","value":50},"backtest_executions":{"period":"day","value":50},"portfolios":{"period":"total","value":5},"watchlists":{"period":"total","value":10},"stock_alerts":{"period":"total","value":25},"prediction_history":{"period":"total","value":500},"data_exports":{"period":"month","value":20},"api_access":{"period":"month","value":0}}', '["advanced_technical_analysis","advanced_portfolio_analytics","advanced_backtesting","exports"]'),
  ('premium', 'Premium', '{"forecast_requests":{"period":"day","value":1000},"advanced_model_usage":{"period":"day","value":500},"backtest_executions":{"period":"day","value":250},"portfolios":{"period":"total","value":25},"watchlists":{"period":"total","value":50},"stock_alerts":{"period":"total","value":100},"prediction_history":{"period":"total","value":5000},"data_exports":{"period":"month","value":100},"api_access":{"period":"month","value":1000}}', '["ensemble_forecasting","advanced_model_intelligence","advanced_portfolio_analytics","advanced_backtesting","exports","api_access"]')
on conflict (id) do update set limits = excluded.limits, features = excluded.features, updated_at = now();

create table if not exists public.plan_features (
  plan_id text not null references public.plans(id) on delete cascade,
  feature_key text not null,
  enabled boolean not null default true,
  primary key (plan_id, feature_key)
);
create table if not exists public.subscriptions (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null unique references auth.users(id) on delete cascade,
  plan_id text not null references public.plans(id),
  status text not null check (status in ('FREE','TRIALING','ACTIVE','PAST_DUE','CANCELLED','EXPIRED','SUSPENDED')),
  starts_at timestamptz not null default now(),
  ends_at timestamptz,
  billing_interval text check (billing_interval in ('month','year')),
  trial_ends_at timestamptz,
  cancelled_at timestamptz,
  renews_at timestamptz,
  provider text,
  provider_subscription_id text unique,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);
create table if not exists public.subscription_events (
  id uuid primary key default gen_random_uuid(),
  user_id uuid references auth.users(id) on delete set null,
  provider text,
  provider_event_id text not null unique,
  event_type text not null,
  payload jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now()
);
create table if not exists public.billing_customers (
  user_id uuid primary key references auth.users(id) on delete cascade,
  provider text not null,
  provider_customer_id text not null unique,
  created_at timestamptz not null default now()
);
create table if not exists public.payment_transactions (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  provider text,
  provider_payment_id text unique,
  status text not null check (status in ('initiated','succeeded','failed','refunded')),
  amount numeric check (amount is null or amount >= 0),
  currency text,
  created_at timestamptz not null default now()
);

alter table public.plan_features enable row level security;
alter table public.subscriptions enable row level security;
alter table public.subscription_events enable row level security;
alter table public.billing_customers enable row level security;
alter table public.payment_transactions enable row level security;
create policy "plan features are readable" on public.plan_features for select using (true);
create policy "subscriptions are user-owned" on public.subscriptions for select using (auth.uid() = user_id);
create policy "subscription events are user-owned" on public.subscription_events for select using (auth.uid() = user_id);
create policy "billing customers are user-owned" on public.billing_customers for select using (auth.uid() = user_id);
create policy "payments are user-owned" on public.payment_transactions for select using (auth.uid() = user_id);

create or replace function public.consume_usage(
  p_user_id uuid,
  p_metric text,
  p_period_start date,
  p_limit integer
) returns table (allowed boolean, usage_count integer)
language plpgsql security definer set search_path = public as $$
declare
  new_count integer;
begin
  insert into public.usage_records(user_id, metric, period_start, usage_count)
  values (p_user_id, p_metric, p_period_start, 1)
  on conflict (user_id, metric, period_start) do update
  set usage_count = public.usage_records.usage_count + 1
  where public.usage_records.usage_count < p_limit
  returning public.usage_records.usage_count into new_count;
  if new_count is null then
    select u.usage_count into usage_count
    from public.usage_records u
    where u.user_id = p_user_id and u.metric = p_metric and u.period_start = p_period_start;
    allowed := false;
  else
    usage_count := new_count;
    allowed := true;
  end if;
  return next;
end;
$$;
revoke all on function public.consume_usage(uuid, text, date, integer) from public;
grant execute on function public.consume_usage(uuid, text, date, integer) to service_role;

insert into public.subscriptions(user_id, plan_id, status)
select ue.user_id, ue.plan_id, 'FREE' from public.user_entitlements ue
on conflict (user_id) do nothing;

create or replace function public.handle_new_user()
returns trigger language plpgsql security definer set search_path = public as $$
begin
  insert into public.profiles (id, display_name) values (new.id, coalesce(new.raw_user_meta_data->>'display_name', new.email));
  insert into public.user_entitlements (user_id, plan_id) values (new.id, 'free') on conflict (user_id) do nothing;
  insert into public.subscriptions (user_id, plan_id, status) values (new.id, 'free', 'FREE') on conflict (user_id) do nothing;
  insert into public.user_preferences (user_id) values (new.id) on conflict (user_id) do nothing;
  return new;
end;
$$;
