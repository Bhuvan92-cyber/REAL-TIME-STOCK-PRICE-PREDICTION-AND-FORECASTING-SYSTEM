# Portfolio transactions

Transactions are virtual buy/sell records owned by the authenticated user.
They include symbol, side, quantity, execution price, optional fee, and
timestamp. Average-cost accounting rejects sells larger than current holdings;
current value remains unavailable when a provider quote is unavailable.

On Windows 11 PowerShell:

```powershell
$env:PYTHONPATH = "."
python -m pytest -q tests/test_phase5_1.py
```

The REST endpoints are `GET/POST/PATCH/DELETE
/api/v1/portfolios/{portfolio_id}/transactions`.
