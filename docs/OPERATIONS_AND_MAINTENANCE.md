# Operations and maintenance

Monitor `/health`, provider latency/errors, 429 responses, Render cold starts,
Supabase quotas, migration history, and scheduled alert failures. Free Render
services have ephemeral filesystems and can sleep; all user records must
remain in Supabase.

Before schema changes, verify the target project, back up as appropriate, and
apply migrations in order. Keep billing disabled until payment-provider
security, reconciliation, and webhook replay controls are approved.

For an incident, disable the affected provider or scheduler secret, preserve
logs without secrets, roll back application code, and do not delete user
data. Re-test authentication, ownership, and health before reopening traffic.
