# Rollback and recovery

Before applying a Supabase migration, export a database backup and record the
migration version. Apply migrations in order; do not delete user data to make
a migration pass. If a deployment fails, roll back the application image
first, then investigate migration compatibility. Restore Supabase from its
backup procedure only after confirming the required recovery point.

For local Docker recovery, stop Compose, preserve the repository data and
environment files, and restart the last known-good image. Do not commit
secrets or generated credentials.
