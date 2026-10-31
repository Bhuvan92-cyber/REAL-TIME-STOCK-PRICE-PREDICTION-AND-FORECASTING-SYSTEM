import { FormEvent, useState } from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { getAlertEvents, getAlerts, getBacktests, getNews, getNotifications, apiRequest } from "./api";

export function Sentiment() {
  const [symbol, setSymbol] = useState("AAPL");
  const news = useQuery({ queryKey: ["news", symbol], queryFn: () => getNews(symbol) });
  return <section><div className="section-heading"><div><p className="eyebrow">MARKET SENTIMENT</p><h2>Provider news feed</h2></div><input value={symbol} onChange={(e) => setSymbol(e.target.value.toUpperCase())} placeholder="AAPL" /></div>{news.isLoading && <p>Loading permitted RSS feed…</p>}{news.error && <p className="error">{(news.error as Error).message}</p>}<div className="grid">{(news.data ?? []).map((item) => <article className="card" key={item.url}><span className={`pill ${item.label === "positive" ? "available" : ""}`}>{item.label}</span><h3><a href={item.url} target="_blank" rel="noreferrer">{item.title}</a></h3><p>{item.source} · {item.published_at ? new Date(item.published_at).toLocaleString() : "Publication time unavailable"}</p></article>)}</div><p className="notice">Headline sentiment is an educational signal and is not a measure of market performance.</p></section>;
}

export function Alerts() {
  const client = useQueryClient();
  const alerts = useQuery({ queryKey: ["alerts"], queryFn: getAlerts });
  const [form, setForm] = useState({ symbol: "AAPL", condition: "above", threshold: "" });
  async function create(event: FormEvent) { event.preventDefault(); await apiRequest("/api/v1/alerts", { method: "POST", body: JSON.stringify({ ...form, threshold: Number(form.threshold) }) }); setForm({ ...form, threshold: "" }); await client.invalidateQueries({ queryKey: ["alerts"] }); }
  const events = useQuery({ queryKey: ["alert-events"], queryFn: getAlertEvents });
  return <section><div className="section-heading"><div><p className="eyebrow">ALERT CENTRE</p><h2>Price alerts</h2></div><button onClick={async () => { await apiRequest("/api/v1/alerts/evaluate", { method: "POST" }); await client.invalidateQueries({ queryKey: ["alerts", "alert-events"] }); }}>Evaluate now</button></div><form className="card form-row" onSubmit={create}><input required value={form.symbol} onChange={(e) => setForm({ ...form, symbol: e.target.value.toUpperCase() })} placeholder="AAPL" /><select value={form.condition} onChange={(e) => setForm({ ...form, condition: e.target.value })}><option value="above">Rises above</option><option value="below">Falls below</option></select><input required type="number" min="0" step="any" value={form.threshold} onChange={(e) => setForm({ ...form, threshold: e.target.value })} placeholder="Threshold" /><button>Create alert</button></form>{alerts.isLoading && <p>Loading alerts…</p>}<div className="grid">{(alerts.data ?? []).map((alert) => <article className="card" key={alert.id}><h3>{alert.symbol}</h3><p>Price {alert.condition} {alert.threshold}</p><button className="secondary" onClick={async () => { await apiRequest(`/api/v1/alerts/${alert.id}`, { method: "PATCH", body: JSON.stringify({ active: !alert.active }) }); await client.invalidateQueries({ queryKey: ["alerts"] }); }}>{alert.active ? "Disable" : "Enable"}</button><button className="text-button" onClick={async () => { await apiRequest(`/api/v1/alerts/${alert.id}`, { method: "DELETE" }); await client.invalidateQueries({ queryKey: ["alerts"] }); }}>Delete</button></article>)}</div><h3>Trigger history</h3>{events.isLoading && <p>Loading events…</p>}{(events.data ?? []).map((event) => <article className="card history-row" key={event.id}><strong>{event.observed_price}</strong><time>{new Date(event.evaluated_at).toLocaleString()}</time></article>)}</section>;
}

export function Notifications() {
  const client = useQueryClient();
  const notifications = useQuery({ queryKey: ["notifications"], queryFn: getNotifications });
  return <section><p className="eyebrow">NOTIFICATIONS</p><h2>Activity centre</h2>{notifications.isLoading && <p>Loading notifications…</p>}{(notifications.data ?? []).map((item) => <article className={`card history-row ${item.read_at ? "" : "unread"}`} key={item.id}><strong>{item.title}</strong><span>{item.body}</span><time>{new Date(item.created_at).toLocaleString()}</time>{!item.read_at && <button onClick={async () => { await apiRequest(`/api/v1/notifications/${item.id}`, { method: "PATCH", body: JSON.stringify({ read: true }) }); await client.invalidateQueries({ queryKey: ["notifications"] }); }}>Mark read</button>}</article>)}</section>;
}

export function Backtesting() {
  const [symbol, setSymbol] = useState("AAPL");
  const [model, setModel] = useState("random_forest");
  const [message, setMessage] = useState("");
  const history = useQuery({ queryKey: ["backtests"], queryFn: getBacktests });
  async function run(event: FormEvent) { event.preventDefault(); setMessage("Running out-of-sample backtest…"); try { await apiRequest(`/api/v1/stocks/${symbol}/backtest`, { method: "POST", body: JSON.stringify({ model, initial_capital: 100000, position_size: 1, transaction_cost: 0.001, slippage: 0.0005 }) }); setMessage("Backtest saved."); await history.refetch(); } catch (error) { setMessage((error as Error).message); } }
  return <section><p className="eyebrow">BACKTESTING</p><h2>Reproducible strategy reports</h2><form className="card form-row" onSubmit={run}><input value={symbol} onChange={(e) => setSymbol(e.target.value.toUpperCase())} required /><select value={model} onChange={(e) => setModel(e.target.value)}><option value="random_forest">Random forest</option><option value="linear_regression">Linear regression</option></select><button>Run backtest</button></form>{message && <p className="notice">{message}</p>}{history.isLoading && <p>Loading reports…</p>}{(history.data ?? []).map((item) => { const result = item.report.strategy?.long_only; return <article className="card history-row" key={item.id}><strong>{item.symbol} · {item.model}</strong><span>Return: {result ? `${(result.cumulative_return * 100).toFixed(2)}%` : "Unavailable"} · Drawdown: {result ? `${(result.max_drawdown * 100).toFixed(2)}%` : "Unavailable"}</span><time>{new Date(item.created_at).toLocaleString()}</time></article>; })}</section>;
}
