# Usage limits

Daily and monthly operation quotas use the `usage_records` table. The
`consume_usage` PostgreSQL function performs an atomic conditional increment,
so concurrent requests cannot consume beyond the configured limit. Total
resource limits are checked against user-owned rows. Failed operations should
only call consumption after the operation is authorized and prepared.
