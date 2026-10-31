# Billing testing

Local tests cover deterministic plan resolution, feature restrictions, quota
periods, HMAC verification, malformed events, and duplicate-event handling.
They do not claim live payment-provider or Supabase integration. Run from
Windows PowerShell:

```powershell
$env:PYTHONPATH = "."
pytest -q tests/test_subscriptions.py
npm run build --prefix frontend
```
