from dataclasses import dataclass


@dataclass(frozen=True)
class Stock:
    symbol: str
    name: str
    exchange: str
    ticker: str
    currency: str


STOCKS: dict[str, Stock] = {
    "AAPL": Stock("AAPL", "Apple Inc.", "NASDAQ", "AAPL", "USD"),
    "MSFT": Stock("MSFT", "Microsoft Corporation", "NASDAQ", "MSFT", "USD"),
    "GOOGL": Stock("GOOGL", "Alphabet Inc.", "NASDAQ", "GOOGL", "USD"),
    "TCS": Stock("TCS", "Tata Consultancy Services", "NSE", "TCS.NS", "INR"),
    "NIFTY50": Stock("NIFTY50", "NIFTY 50 Index", "NSE", "^NSEI", "INR"),
}


def get_stock(symbol: str) -> Stock:
    key = symbol.upper()
    try:
        return STOCKS[key]
    except KeyError as exc:
        raise ValueError(f"Unsupported stock symbol: {symbol}") from exc
