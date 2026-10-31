import { useQuery } from "@tanstack/react-query";
import { getPlans, getSubscription, type Plan } from "./api";
import type { ReactNode } from "react";

const label = (value: string) => value.replace(/_/g, " ");

export function PlanBadge({ plan }: { plan?: string }) {
  return <span className="pill">{(plan ?? "free").toUpperCase()}</span>;
}

export function UsageLimitIndicator({ metric, used, limit }: { metric: string; used: number; limit?: { period: string; value: number } }) {
  const maximum = limit?.value ?? 0;
  const percentage = maximum ? Math.min(100, used / maximum * 100) : 0;
  return <div className="usage-item"><div><strong>{label(metric)}</strong><span>{used} / {maximum || "not available"} {limit?.period}</span></div><progress max="100" value={percentage} /></div>;
}

export function Pricing() {
  const plans = useQuery({ queryKey: ["plans"], queryFn: getPlans });
  return <section><p className="eyebrow">PLANS</p><h2>Choose your analytics workspace</h2><p className="notice">Billing is currently disabled. Plans and entitlements are ready for future provider integration; no payment is requested or simulated.</p><div className="grid">{(plans.data ?? []).map((plan) => <PlanCard key={plan.id} plan={plan} />)}</div></section>;
}

function PlanCard({ plan }: { plan: Plan }) {
  return <article className="card"><div className="section-heading"><h3>{plan.name}</h3><PlanBadge plan={plan.id} /></div><ul>{plan.features.map((feature) => <li key={feature}>{label(feature)}</li>)}</ul>{Object.entries(plan.limits).map(([metric, limit]) => <p key={metric}>{label(metric)}: {limit.value} / {limit.period}</p>)}<button disabled>Billing unavailable</button></article>;
}

export function SubscriptionSettings() {
  const subscription = useQuery({ queryKey: ["subscription"], queryFn: getSubscription });
  if (subscription.isLoading) return <p className="state">Loading subscription…</p>;
  if (subscription.error) return <p className="error">{(subscription.error as Error).message}</p>;
  const account = subscription.data;
  const usage = new Map(account?.usage.map((row) => [row.metric, row.usage_count]));
  return <section><div className="section-heading"><div><p className="eyebrow">SUBSCRIPTION</p><h2>Account plan</h2></div><PlanBadge plan={account?.plan.id} /></div><p className="notice">Status: {account?.subscription.status}. Billing is disabled, so upgrades, downgrades and cancellations are unavailable.</p><div className="card"><h3>{account?.plan.name} plan</h3>{Object.entries(account?.plan.limits ?? {}).map(([metric, limit]) => <UsageLimitIndicator key={metric} metric={metric} used={usage.get(metric) ?? 0} limit={limit} />)}</div><p><a href="/pricing">Compare plans</a></p></section>;
}

export function FeatureGate({ allowed, feature, children }: { allowed: boolean; feature: string; children: ReactNode }) {
  if (allowed) return <>{children}</>;
  return <div className="notice">The {label(feature)} feature requires a higher plan. <a href="/pricing">Compare plans</a>.</div>;
}
