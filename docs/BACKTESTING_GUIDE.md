# Backtesting guide

Backtests use historical out-of-sample observations and explicit transaction
cost, slippage, capital, position sizing, stop-loss, and take-profit inputs.
Signals are observed on the prior bar and executed on the next bar; open
positions are liquidated at the end of the evaluation period. Reports include
benchmark buy-and-hold, equity curve, drawdown, Sharpe, Sortino, profit factor,
win rate, CAGR, and trade history.

`POST /api/v1/stocks/{symbol}/backtest` persists authenticated reports in
`backtest_history`; `GET /api/v1/backtests` returns only the caller's reports.
Results are simulations, not investment promises. Free provider history can
be incomplete and does not eliminate survivorship or execution-model
limitations.
