drop policy if exists "watchlist items are user-owned" on public.watchlist_items;
create policy "watchlist items are user-owned" on public.watchlist_items
for all using (
  auth.uid() = user_id
  and exists (
    select 1 from public.watchlists w
    where w.id = watchlist_items.watchlist_id
      and w.user_id = auth.uid()
  )
) with check (
  auth.uid() = user_id
  and exists (
    select 1 from public.watchlists w
    where w.id = watchlist_items.watchlist_id
      and w.user_id = auth.uid()
  )
);

drop policy if exists "portfolio assets are user-owned" on public.portfolio_assets;
create policy "portfolio assets are user-owned" on public.portfolio_assets
for all using (
  auth.uid() = user_id
  and exists (
    select 1 from public.portfolios p
    where p.id = portfolio_assets.portfolio_id
      and p.user_id = auth.uid()
  )
) with check (
  auth.uid() = user_id
  and exists (
    select 1 from public.portfolios p
    where p.id = portfolio_assets.portfolio_id
      and p.user_id = auth.uid()
  )
);

drop policy if exists "portfolio transactions are user-owned" on public.portfolio_transactions;
create policy "portfolio transactions are user-owned" on public.portfolio_transactions
for all using (
  auth.uid() = user_id
  and exists (
    select 1 from public.portfolios p
    where p.id = portfolio_transactions.portfolio_id
      and p.user_id = auth.uid()
  )
) with check (
  auth.uid() = user_id
  and exists (
    select 1 from public.portfolios p
    where p.id = portfolio_transactions.portfolio_id
      and p.user_id = auth.uid()
  )
);

drop policy if exists "portfolio snapshots are user-owned" on public.portfolio_snapshots;
create policy "portfolio snapshots are user-owned" on public.portfolio_snapshots
for all using (
  auth.uid() = user_id
  and exists (
    select 1 from public.portfolios p
    where p.id = portfolio_snapshots.portfolio_id
      and p.user_id = auth.uid()
  )
) with check (
  auth.uid() = user_id
  and exists (
    select 1 from public.portfolios p
    where p.id = portfolio_snapshots.portfolio_id
      and p.user_id = auth.uid()
  )
);

drop policy if exists "alert events are user-owned" on public.alert_events;
create policy "alert events are user-owned" on public.alert_events
for all using (
  auth.uid() = user_id
  and exists (
    select 1 from public.alert_rules a
    where a.id = alert_events.alert_id
      and a.user_id = auth.uid()
  )
) with check (
  auth.uid() = user_id
  and exists (
    select 1 from public.alert_rules a
    where a.id = alert_events.alert_id
      and a.user_id = auth.uid()
  )
);
