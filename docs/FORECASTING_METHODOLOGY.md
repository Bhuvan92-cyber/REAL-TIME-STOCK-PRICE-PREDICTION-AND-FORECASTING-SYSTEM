# Forecasting methodology

Historical rows are kept in chronological order. Evaluation uses an
out-of-sample tail split and reports MAE, RMSE, MAPE, sMAPE, R², and directional
accuracy. MAPE excludes zero actual values. The walk-forward helper refits on
the observations available at each decision point.

Recursive multi-horizon forecasts are limited by the model adapter and are not
guarantees of future prices. Yahoo Finance data can be delayed and the system
does not claim exchange-grade real-time access.
