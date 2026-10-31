# Public smoke tests

Run only after deployment:

```powershell
$api = "https://<api-host>"
$web = "https://<frontend-host>"
Invoke-WebRequest "$api/health"
Invoke-WebRequest "$api/api/v1/stocks"
Invoke-WebRequest "$web/"
Invoke-WebRequest "$web/pricing"
```

Then manually verify:

- Refreshing `/pricing`, `/login`, and a protected route preserves SPA
  fallback behavior.
- Missing/expired tokens receive an authorization error.
- A real test account can register, sign in, create private data, and sign out.
- A second account cannot read or mutate the first account's records.
- Provider failure states identify unavailable data rather than showing zero.

Record URL, timestamp, HTTP status, provider source, and account/test scope.
Do not record access tokens or secret values.
