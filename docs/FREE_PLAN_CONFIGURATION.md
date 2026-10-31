# Free-plan configuration

The application works with billing disabled and no payment credentials. Set
`BILLING_ENABLED=false` (the default), leave provider secrets unset, and apply
Supabase migrations `001` through `005`. Configure only `SUPABASE_URL`,
`SUPABASE_SERVICE_ROLE_KEY`, and the existing authentication variables for
local persistence.

On Windows 11 PowerShell:

```powershell
$env:BILLING_ENABLED = "false"
$env:PYTHONPATH = "."
uvicorn api.main:app --reload
```
