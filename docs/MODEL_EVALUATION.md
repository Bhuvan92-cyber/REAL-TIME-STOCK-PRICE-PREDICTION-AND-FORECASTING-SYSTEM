# Model evaluation

`modules/evaluation/forecast_metrics.py` contains deterministic metric
calculation and `walk_forward.py` contains chronological split helpers.
Metrics must be generated from actual out-of-sample arrays; no accuracy values
are hardcoded. A naive last-observed-price baseline is available through the
same metric functions.
