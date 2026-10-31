import { supabase } from "./supabase";

export type Stock = {
  symbol: string;
  name: string;
  exchange: string;
  currency: string;
};

export type MarketResponse = {
  symbol: string;
  source: "cache" | "yahoo_finance";
  delayed: boolean;
  fetched_at: string;
  candles: Array<{ timestamp: string; open: number; high: number; low: number; close: number; volume: number; sma_20?: number | null; ema_20?: number | null; rsi?: number | null; macd?: number | null; macd_signal?: number | null; bb_upper?: number | null; bb_lower?: number | null }>;
};

export type ModelMetric = {
  model: string;
  available: boolean;
  mae?: number;
  rmse?: number;
  mape?: number;
  smape?: number;
  r2?: number;
  directional_accuracy?: number;
  reason?: string;
};

const API_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

export async function apiRequest<T>(path: string, init: RequestInit = {}): Promise<T> {
  const { data } = supabase ? await supabase.auth.getSession() : { data: { session: null } };
  const headers = new Headers(init.headers);
  headers.set("Content-Type", "application/json");
  if (data.session?.access_token) {
    headers.set("Authorization", "Bearer " + data.session.access_token);
  }
  const response = await fetch(`${API_URL}${path}`, { ...init, headers });
  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    throw new Error(body.detail ?? `API request failed (${response.status})`);
  }
  return response.json() as Promise<T>;
}

export const getStocks = () => apiRequest<Stock[]>("/api/v1/stocks");
export const getMarket = (symbol: string) => apiRequest<MarketResponse>(`/api/v1/stocks/${symbol}/market`);
export const getModels = () => apiRequest<Array<{ name: string; family: string; available: boolean; reason?: string }>>("/api/v1/models");
export const getModelMetrics = (symbol: string) => apiRequest<ModelMetric[]>(`/api/v1/stocks/${symbol}/model-metrics`);
export const getRisk = (symbol: string) => apiRequest<Record<string, number | string>>(`/api/v1/stocks/${symbol}/risk`);
export const getForecast = (symbol: string, model: string, horizon: number) =>
  apiRequest<{ symbol: string; model: string; current_price: number; predictions: number[]; data_source: string; warning: string; training_cutoff?: string; interval_available: boolean }>(`/api/v1/stocks/${symbol}/forecast`, { method: "POST", body: JSON.stringify({ model, horizon }) });
export const getNews = (symbol: string) => apiRequest<Array<{ title: string; url: string; source: string; published_at?: string; label: string; score: number }>>(`/api/v1/news?symbol=${encodeURIComponent(symbol)}`);
export const getAlerts = () => apiRequest<Array<{ id: string; symbol: string; condition: string; threshold: number; active: boolean }>>("/api/v1/alerts");
export const getNotifications = () => apiRequest<Array<{ id: string; title: string; body: string; read_at?: string; created_at: string }>>("/api/v1/notifications");
export const getAlertEvents = () => apiRequest<Array<{ id: string; observed_price: number; evaluated_at: string; alert_id: string }>>("/api/v1/alerts/events");
export const getBacktests = () => apiRequest<Array<{ id: string; symbol: string; model: string; report: { strategy?: { long_only?: { cumulative_return: number; max_drawdown: number; } } }; created_at: string }>>("/api/v1/backtests");
export type Plan = { id: string; name: string; limits: Record<string, { period: string; value: number }>; features: string[] };
export const getPlans = () => apiRequest<Plan[]>("/api/v1/plans");
export const getSubscription = () => apiRequest<{ plan: Plan; subscription: { status: string; starts_at?: string; renews_at?: string }; usage: Array<{ metric: string; usage_count: number; period_start: string }> }>("/api/v1/subscriptions/me");
export const getSubscriptionUsage = () => apiRequest<{ plan: Plan; usage: Array<{ metric: string; usage_count: number; period_start: string }> }>("/api/v1/subscriptions/usage");
