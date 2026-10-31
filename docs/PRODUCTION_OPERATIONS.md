# Production operations

Monitor `/health`, API error rates, provider latency, rate-limit responses,
Supabase usage, and scheduler failures. Keep `BILLING_ENABLED=false` until a
real payment provider, webhook replay protection, reconciliation, and
incident process are approved.

Rotate Supabase service-role, scheduler, JWT, and webhook secrets through the
hosting provider's secret manager. Never place them in frontend variables,
logs, screenshots, or issue reports.

Before a migration, back up the Supabase project and apply migrations in
numeric order. Roll back application code first; treat database rollback as a
planned migration because destructive rollback can lose user data.
