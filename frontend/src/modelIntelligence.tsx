import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { getModelMetrics, getModels, getStocks } from "./api";

export function ModelIntelligence() {
  const [symbol, setSymbol] = useState("AAPL");
  const stocks = useQuery({ queryKey: ["stocks"], queryFn: getStocks });
  const models = useQuery({ queryKey: ["models"], queryFn: getModels });
  const metrics = useQuery({ queryKey: ["model-metrics", symbol], queryFn: () => getModelMetrics(symbol), enabled: Boolean(symbol) });
  return <section>
    <div className="section-heading"><div><p className="eyebrow">MODEL INTELLIGENCE</p><h2>Compare forecasting models</h2></div><select value={symbol} onChange={(event) => setSymbol(event.target.value)}>{(stocks.data ?? [{ symbol: "AAPL", name: "Apple Inc." }]).map((stock) => <option key={stock.symbol} value={stock.symbol}>{stock.symbol}</option>)}</select></div>
    {models.data && <div className="model-list">{models.data.map((model) => <span className={model.available ? "pill available" : "pill"} key={model.name}>{model.name} · {model.available ? "available" : "optional dependency missing"}</span>)}</div>}
    {metrics.isLoading && <p>Evaluating chronological holdout…</p>}{metrics.error && <p className="error">{(metrics.error as Error).message}</p>}
    {metrics.data && <div className="table-wrap"><table><thead><tr><th>Model</th><th>MAE</th><th>RMSE</th><th>MAPE</th><th>sMAPE</th><th>R²</th><th>Direction</th></tr></thead><tbody>{metrics.data.map((metric) => <tr key={metric.model}><td>{metric.model}</td><td>{metric.mae?.toFixed(3) ?? "—"}</td><td>{metric.rmse?.toFixed(3) ?? "—"}</td><td>{metric.mape?.toFixed(2) ?? "—"}%</td><td>{metric.smape?.toFixed(2) ?? "—"}%</td><td>{metric.r2?.toFixed(3) ?? "—"}</td><td>{metric.directional_accuracy?.toFixed(1) ?? "—"}%</td></tr>)}</tbody></table></div>}
    <p className="notice">Metrics are calculated from the historical chronological holdout and do not guarantee future performance.</p>
  </section>;
}
