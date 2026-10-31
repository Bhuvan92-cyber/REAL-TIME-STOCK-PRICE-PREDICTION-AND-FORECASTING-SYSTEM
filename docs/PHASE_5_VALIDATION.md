# Phase 5.1 validation

Run these commands from the repository root in Windows 11 PowerShell:

```powershell
$env:PYTHONPATH = "."
pytest -q tests/test_phase5_1.py tests/test_ml_foundations.py tests/test_api_auth.py
python -m compileall -q api modules
npm run build --prefix frontend
```

The deterministic suite uses mocked/local values. Live Supabase RLS,
Yahoo Finance, RSS providers, and GitHub Actions execution require configured
external services and are not claimed by local tests.
