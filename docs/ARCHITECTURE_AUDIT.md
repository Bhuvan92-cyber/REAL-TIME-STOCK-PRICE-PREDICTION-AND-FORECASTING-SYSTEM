# Architecture audit

## Scope

The audit covers the repository at the start of the platform upgrade. Existing
Streamlit pages and `modules/` code were inspected without deleting model
artifacts or historical datasets.

## Findings

### Strengths

- The project already has reusable ingestion, preprocessing, feature
  engineering, model, evaluation, prediction, and risk-management modules.
- Yahoo Finance ingestion and CSV datasets provide a no-card development path.
- Existing Random Forest and CNN-LSTM artifacts can be retained.
- Streamlit pages cover live market, technical analysis, predictions, risk, and
  model-performance workflows.

### Defects and risks

1. There was no API boundary, typed request/response contract, or separation
   between UI code and business logic.
2. `setup.py` and `requirements.txt` had conflicting NumPy and FastAPI-related
   dependency constraints. Optional ML dependencies were not represented
   clearly.
3. `config.yaml` used placeholder API-key fields. Secrets must come from the
   environment and must never be required for the free Yahoo Finance path.
4. The Streamlit entry point configured the page after creating sidebar
   widgets, which can fail in Streamlit.
5. The existing model pages assume pre-trained artifacts and exact feature
   counts, but do not expose a documented API error contract.
6. Yahoo Finance data is delayed/limited by provider policy; it must not be
   labelled as an exchange-grade real-time feed.
7. There is no user identity, watchlist, portfolio, prediction-history storage,
   or row-level authorization layer.
8. The original deployment only starts Streamlit and does not provide a
   health-checked backend/frontend topology.
9. Several tests depend on live network access, making deterministic CI
   difficult.

## Upgrade decisions

- Preserve the existing Streamlit application and `modules/` package.
- Add a FastAPI application under `api/` with explicit validation and provider
  metadata.
- Use local historical CSVs when available and Yahoo Finance as the configured
  fallback; responses state the data source and freshness limitations.
- Add a React/Vite frontend shell that consumes the API rather than duplicating
  forecasting logic.
- Keep Supabase integration opt-in through environment variables and provide
  SQL migrations with RLS policies; local development remains usable without
  credentials.
- Keep model providers optional. A missing optional provider returns an explicit
  error rather than a fabricated forecast.

## Remaining work

Portfolio writes, Supabase auth wiring, and production model training remain
separate implementation phases. They are intentionally not represented as
successful functionality until the required service configuration and tests are
available.
