# Subscription plans

Free, Pro, and Premium definitions are stored in `plans` with JSON limits and
feature keys. Migration `005_subscription_platform.sql` seeds the configurable
defaults. Plan changes preserve portfolios, watchlists, predictions, and
history; they only alter future access and quotas.
