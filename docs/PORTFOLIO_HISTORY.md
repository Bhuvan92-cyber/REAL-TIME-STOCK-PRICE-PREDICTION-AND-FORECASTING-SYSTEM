# Portfolio history

`GET /api/v1/portfolios/{portfolio_id}/history` returns persisted daily
snapshots. Snapshots must be produced from transaction history and historical
prices, not reconstructed from current holdings. Missing historical prices are
represented as unavailable. Currency is not converted automatically; do not
combine USD and INR portfolios without an explicit exchange-rate policy.
