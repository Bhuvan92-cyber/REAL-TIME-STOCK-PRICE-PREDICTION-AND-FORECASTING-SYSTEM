import { lazy, Suspense, useState, type ReactNode } from "react";
import { Link, Navigate, Route, Routes, useLocation } from "react-router-dom";
import { useAuth } from "./auth";
import { ForgotPassword, Login, Register, ResetPassword } from "./authPages";
const Portfolios = lazy(() => import("./privatePages").then((module) => ({ default: module.Portfolios })));
const PredictionHistory = lazy(() => import("./privatePages").then((module) => ({ default: module.PredictionHistory })));
const Profile = lazy(() => import("./privatePages").then((module) => ({ default: module.Profile })));
const Watchlists = lazy(() => import("./privatePages").then((module) => ({ default: module.Watchlists })));
const ModelIntelligence = lazy(() => import("./modelIntelligence").then((module) => ({ default: module.ModelIntelligence })));
const Forecasting = lazy(() => import("./marketPages").then((module) => ({ default: module.Forecasting })));
const MarketOverview = lazy(() => import("./marketPages").then((module) => ({ default: module.MarketOverview })));
const RiskAnalytics = lazy(() => import("./marketPages").then((module) => ({ default: module.RiskAnalytics })));
const Alerts = lazy(() => import("./intelligencePages").then((module) => ({ default: module.Alerts })));
const Backtesting = lazy(() => import("./intelligencePages").then((module) => ({ default: module.Backtesting })));
const Notifications = lazy(() => import("./intelligencePages").then((module) => ({ default: module.Notifications })));
const Sentiment = lazy(() => import("./intelligencePages").then((module) => ({ default: module.Sentiment })));
const Pricing = lazy(() => import("./subscriptionPages").then((module) => ({ default: module.Pricing })));
const SubscriptionSettings = lazy(() => import("./subscriptionPages").then((module) => ({ default: module.SubscriptionSettings })));
import { useQuery } from "@tanstack/react-query";
import { getMarket, getStocks, getSubscription } from "./api";

function Protected({ children }: { children: ReactNode }) {
  const { user, loading } = useAuth();
  const location = useLocation();
  if (loading) return <p className="state">Restoring session…</p>;
  if (!user) return <Navigate to={`/login?next=${encodeURIComponent(location.pathname)}`} replace />;
  return <>{children}</>;
}

function PublicOnly({ children }: { children: React.ReactNode }) {
  const { user, loading } = useAuth();
  if (loading) return <p className="state">Loading…</p>;
  return user ? <Navigate to="/" replace /> : <>{children}</>;
}

function Dashboard() {
  const { user, signOut } = useAuth();
  const [symbol, setSymbol] = useState("AAPL");
  const stocks = useQuery({ queryKey: ["stocks"], queryFn: getStocks });
  const subscription = useQuery({ queryKey: ["subscription"], queryFn: getSubscription });
  const market = useQuery({ queryKey: ["market", symbol], queryFn: () => getMarket(symbol), refetchInterval: 60_000 });
  const candles = market.data?.candles ?? [];
  const latest = candles.length ? candles[candles.length - 1] : undefined;
  return <main className="shell">
    <header className="topbar"><div><p className="eyebrow">MARKET INTELLIGENCE</p><h1>Stock Analytics</h1></div><div className="user-actions"><span>{user?.email}</span><button className="secondary" onClick={signOut}>Log out</button></div></header>
    <nav className="nav"><Link to="/">Dashboard</Link><Link to="/market">Market</Link><Link to="/technical">Technical</Link><Link to="/forecasting">Forecasting</Link><Link to="/models">Models</Link><Link to="/watchlists">Watchlists</Link><Link to="/portfolios">Portfolio</Link><Link to="/risk">Risk</Link><Link to="/predictions">History</Link><Link to="/profile">Profile</Link></nav>
    <section className="notice"><strong>Data status:</strong> {market.data?.delayed ? "Delayed provider data" : "Loading provider status"}. Forecasts are estimates and are not financial advice.</section>
    <div className="toolbar"><select value={symbol} onChange={(event) => setSymbol(event.target.value)}>{(stocks.data ?? [{ symbol: "AAPL", name: "Apple Inc." }]).map((stock) => <option key={stock.symbol} value={stock.symbol}>{stock.symbol} · {stock.name}</option>)}</select></div>
    {market.isLoading && <p className="state">Loading market data…</p>}{market.error && <p className="error">{(market.error as Error).message}</p>}
    {latest && <section className="grid"><article className="card primary"><p className="eyebrow">LATEST CLOSE</p><div className="price">{latest.close.toFixed(2)}</div><p>{symbol} · {market.data?.source === "cache" ? "Local cache" : "Yahoo Finance"}</p></article><article className="card"><p className="eyebrow">OBSERVATIONS</p><div className="metric">{candles.length}</div><p>Daily candles available</p></article><article className="card"><p className="eyebrow">ACCOUNT</p><div className="metric">{subscription.data?.plan.name ?? "Free"}</div><p><Link to="/subscription">View plan and usage</Link></p></article></section>}
  </main>;
}

export default function App() {
  return <Suspense fallback={<p className="state">Loading page…</p>}><Routes>
    <Route path="/login" element={<PublicOnly><Login /></PublicOnly>} />
    <Route path="/register" element={<PublicOnly><Register /></PublicOnly>} />
    <Route path="/forgot-password" element={<PublicOnly><ForgotPassword /></PublicOnly>} />
    <Route path="/reset-password" element={<ResetPassword />} />
    <Route path="/pricing" element={<Pricing />} />
    <Route path="/*" element={<Protected><Routes><Route path="/" element={<Dashboard />} /><Route path="/market" element={<Page><MarketOverview /></Page>} /><Route path="/technical" element={<Page><MarketOverview technical /></Page>} /><Route path="/forecasting" element={<Page><Forecasting /></Page>} /><Route path="/models" element={<Page><ModelIntelligence /></Page>} /><Route path="/watchlists" element={<Page><Watchlists /></Page>} /><Route path="/portfolios" element={<Page><Portfolios /></Page>} /><Route path="/risk" element={<Page><RiskAnalytics /></Page>} /><Route path="/sentiment" element={<Page><Sentiment /></Page>} /><Route path="/alerts" element={<Page><Alerts /></Page>} /><Route path="/notifications" element={<Page><Notifications /></Page>} /><Route path="/backtesting" element={<Page><Backtesting /></Page>} /><Route path="/subscription" element={<Page><SubscriptionSettings /></Page>} /><Route path="/predictions" element={<Page><PredictionHistory /></Page>} /><Route path="/profile" element={<Page><Profile /></Page>} /></Routes></Protected>} />
  </Routes></Suspense>;
}

function Page({ children }: { children: ReactNode }) {
  return <main className="shell"><nav className="nav"><Link to="/">Dashboard</Link><Link to="/market">Market</Link><Link to="/technical">Technical</Link><Link to="/forecasting">Forecasting</Link><Link to="/models">Models</Link><Link to="/watchlists">Watchlists</Link><Link to="/portfolios">Portfolio</Link><Link to="/risk">Risk</Link><Link to="/sentiment">Sentiment</Link><Link to="/alerts">Alerts</Link><Link to="/notifications">Notifications</Link><Link to="/backtesting">Backtests</Link><Link to="/subscription">Subscription</Link><Link to="/predictions">History</Link><Link to="/profile">Profile</Link></nav>{children}</main>;
}
