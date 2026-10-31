# Testing strategy

The default backend command is network-free:

```powershell
python -m pytest -m "not live_external" -q
```

Tests use `unit`, `integration`, and `live_external` markers. Market-data unit
tests use `DeterministicMarketDataProvider` and cover successful, empty, and
provider-failure responses. Yahoo Finance tests are explicitly marked
`live_external` and are never part of the default suite.

Frontend validation runs TypeScript compilation and the Vite production build.
Vitest/React Testing Library infrastructure is tracked separately from live
provider and Supabase tests; browser journeys require a configured Playwright
runtime and are not represented as successful until executed.
