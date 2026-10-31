# Alert reliability

Only active rules with available provider prices are evaluated. Price alerts
honor cooldowns and persist the observed price, evaluation timestamp, and a
unique time-bucketed event key before creating a notification. Provider
failures are counted by scheduled evaluation and do not create synthetic
events. Technical-indicator and forecast-specific rules remain future work.
