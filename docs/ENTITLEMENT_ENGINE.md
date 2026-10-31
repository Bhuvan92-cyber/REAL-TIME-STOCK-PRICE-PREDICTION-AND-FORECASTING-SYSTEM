# Entitlement engine

`EntitlementService` resolves effective plan, feature access, resource limits,
and period usage. Expired, cancelled, and suspended subscriptions resolve to
Free. Existing `enforce_limit` and `record_usage` callers delegate to this
service for compatibility.
