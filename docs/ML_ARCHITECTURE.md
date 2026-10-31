# ML architecture

Forecasting is split into model adapters, evaluation, services, and API
routes. `modules/models/registry.py` is the extension point: optional
XGBoost and LightGBM adapters are reported as unavailable when their packages
are not installed rather than breaking application startup.

Online requests load existing registered artifacts and never train inside the
forecast route. Model comparison and backtesting currently train on the
selected historical dataset as authenticated, rate-limited analysis operations;
production deployments should move those jobs to a scheduled worker.
