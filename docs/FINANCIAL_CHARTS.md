# Financial charts

Market charts use backend OHLCV rows and backend-calculated SMA, EMA,
Bollinger, RSI, and MACD fields. Volume is rendered separately. Values are
formatted from the returned currency context; missing provider values remain
missing rather than zero. Chart data is cached by symbol through TanStack
Query.
