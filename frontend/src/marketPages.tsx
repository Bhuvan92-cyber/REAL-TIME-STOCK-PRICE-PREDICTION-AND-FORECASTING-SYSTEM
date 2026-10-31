import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { getMarket, getRisk, getStocks, getForecast } from "./api";
import { PriceChart, VolumeChart } from "./Chart";

function StockSelect({ value, onChange }: { value: string; onChange: (value: string) => void }) {
  const stocks = useQuery({ queryKey: ["stocks"], queryFn: getStocks });
  return <select value={value} onChange={(e) => onChange(e.target.value)}>{(stocks.data ?? [{ symbol: "AAPL", name: "Apple Inc." }]).map((stock) => <option key={stock.symbol} value={stock.symbol}>{stock.symbol} · {stock.name}</option>)}</select>;
}

export function MarketOverview({ technical = false }: { technical?: boolean }) {
  const [symbol, setSymbol] = useState("AAPL");
  const market = useQuery({ queryKey: ["market", symbol], queryFn: () => getMarket(symbol), refetchInterval: 60_000 });
  return <section><div className="section-heading"><div><p className="eyebrow">{technical ? "TECHNICAL ANALYSIS" : "MARKET OVERVIEW"}</p><h2>{technical ? "Indicators and price action" : "Explore supported instruments"}</h2></div><StockSelect value={symbol} onChange={setSymbol} /></div>{market.isLoading && <p>Loading market data…</p>}{market.error && <p className="error">{(market.error as Error).message}</p>}{market.data && <><div className="card"><PriceChart candles={market.data.candles} indicators={technical} /></div><div className="card"><p className="eyebrow">VOLUME</p><VolumeChart candles={market.data.candles} /></div><p className="notice">Source: {market.data.source}. Updated {new Date(market.data.fetched_at).toLocaleString()}. Provider data may be delayed.</p></>}</section>;
}

export function Forecasting() {
  const [symbol, setSymbol] = useState("AAPL");
  const [model, setModel] = useState("random_forest");
  const [horizon, setHorizon] = useState(1);
  const forecast = useQuery({ queryKey: ["forecast", symbol, model, horizon], queryFn: () => getForecast(symbol, model, horizon), enabled: false });
  const lastPrediction = forecast.data?.predictions.length ? forecast.data.predictions[forecast.data.predictions.length - 1] : undefined;
  return <section><div className="section-heading"><div><p className="eyebrow">AI FORECASTING</p><h2>Generate an artifact-backed forecast</h2></div><StockSelect value={symbol} onChange={setSymbol} /></div><div className="card form-row"><select value={model} onChange={(e) => setModel(e.target.value)}><option value="random_forest">Random Forest</option><option value="linear_regression">Linear Regression</option><option value="arima">ARIMA</option><option value="sarima">SARIMA</option><option value="ensemble">Ensemble</option></select><select value={horizon} onChange={(e) => setHorizon(Number(e.target.value))}><option value={1}>1 trading day</option><option value={5}>5 trading days</option><option value={10}>10 trading days</option><option value={30}>30 trading days</option></select><button onClick={() => forecast.refetch()} disabled={forecast.isFetching}>{forecast.isFetching ? "Generating…" : "Generate forecast"}</button></div>{forecast.error && <p className="error">{(forecast.error as Error).message}</p>}{forecast.data && <div className="grid"><article className="card primary"><p className="eyebrow">FORECAST</p><div className="price">{lastPrediction?.toFixed(2)}</div><p>{forecast.data.model} · {horizon} trading day(s)</p></article><article className="card"><p className="eyebrow">CURRENT PRICE</p><div className="metric">{forecast.data.current_price.toFixed(2)}</div><p>{forecast.data.data_source}</p></article><article className="card"><p className="eyebrow">INTERVAL</p><div className="metric">{forecast.data.interval_available ? "Available" : "Unavailable"}</div><p>Calibration status is explicit.</p></article></div>}</section>;
}

export function RiskAnalytics() {
  const [symbol, setSymbol] = useState("AAPL");
  const risk = useQuery({ queryKey: ["risk", symbol], queryFn: () => getRisk(symbol) });
  return <section><div className="section-heading"><div><p className="eyebrow">RISK ANALYTICS</p><h2>Risk and drawdown measures</h2></div><StockSelect value={symbol} onChange={setSymbol} /></div>{risk.isLoading && <p>Calculating risk…</p>}{risk.error && <p className="error">{(risk.error as Error).message}</p>}{risk.data && <div className="grid">{["annualized_volatility", "sharpe_ratio", "sortino_ratio", "max_drawdown", "value_at_risk", "conditional_value_at_risk"].map((key) => <article className="card" key={key}><p className="eyebrow">{key.split("_").join(" ").toUpperCase()}</p><div className="metric">{Number(risk.data[key]).toFixed(4)}</div><p>Daily returns, annualized factor 252</p></article>)}</div>}<p className="notice">Historical risk statistics are not guarantees. Risk-free rate assumption: 0.</p></section>;
}
