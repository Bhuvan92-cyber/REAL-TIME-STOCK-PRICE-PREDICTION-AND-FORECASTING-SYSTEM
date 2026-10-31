# Billing security

No card numbers, CVVs, payment secrets, or service-role credentials are sent
to the frontend. Subscription APIs derive ownership from the verified bearer
token. Admin plan changes require `ADMIN_USER_IDS` server configuration.
Webhook processing requires a backend HMAC secret and unique provider event
IDs. Live billing is disabled unless explicitly configured.
