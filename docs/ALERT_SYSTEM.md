# Alert system

Price alerts are persisted per user with active state, thresholds, cooldowns,
and trigger events. Manual evaluation is available through the API. A future
scheduled job may call the same evaluator, but free hosting must not be
assumed to provide a continuously running worker.
