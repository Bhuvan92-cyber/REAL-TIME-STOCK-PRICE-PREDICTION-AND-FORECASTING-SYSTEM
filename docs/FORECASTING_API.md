# Forecasting API

- `GET /api/v1/models` lists model availability.
- `POST /api/v1/stocks/{symbol}/forecast` generates an authenticated forecast
  for 1–30 requested steps.
- `GET /api/v1/stocks/{symbol}/model-metrics` evaluates available regression
  models on a chronological holdout.
- `POST /api/v1/stocks/{symbol}/backtest` runs an authenticated directional
  backtest with explicit costs and slippage.

Responses include data source, training cutoff where applicable, and explicit
interval availability. Unsupported or unavailable models return an error.
