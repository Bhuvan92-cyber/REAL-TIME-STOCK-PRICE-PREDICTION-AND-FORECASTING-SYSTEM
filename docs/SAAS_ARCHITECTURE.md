# SaaS architecture

The backend resolves a user's plan from authenticated identity and trusted
Supabase records. The Free plan is assigned by the new-user database trigger.
All feature and quota checks run server-side; frontend gates are explanatory
UX only.

Billing is disabled by default. Future providers implement
`api/subscriptions/payment_provider.py` without changing entitlement callers.
