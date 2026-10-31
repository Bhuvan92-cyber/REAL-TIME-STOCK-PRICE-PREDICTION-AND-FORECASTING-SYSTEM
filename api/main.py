from __future__ import annotations

from datetime import datetime, timezone
from collections import defaultdict, deque
from threading import Lock
from time import monotonic

from fastapi import Depends, FastAPI, Header, HTTPException, Query, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

from api.catalog import STOCKS, get_stock
from api.auth import CurrentUser
from api.config import settings
from api.database import SupabaseDatabase, database
from api.entitlements import enforce_limit, record_usage
from api.ml_service import backtest_model, compare_models, ensemble_forecast, forecast_with_model
from api.schemas import (
    ForecastRequest,
    ForecastResponse,
    MarketResponse,
    RiskResponse,
    StockResponse,
    PortfolioAssetCreate,
    PortfolioCreate,
    PredictionSave,
    ProfileUpdate,
    WatchlistCreate,
    WatchlistItemCreate,
    BacktestRequest,
    ModelInfo,
    ModelMetric,
    AlertCreate,
    NotificationUpdate,
    PortfolioTransactionCreate,
    PortfolioTransactionUpdate,
    PortfolioSnapshotCreate,
)
from modules.models.registry import list_models
from modules.risk_management.risk_metrics import calculate_risk_metrics
from modules.portfolio.analytics import calculate_portfolio_analytics
from modules.alerts.engine import evaluate_price_alert
from modules.sentiment_analysis.rss_feed import classify_headline, fetch_rss_news
from api.subscriptions.service import EntitlementService
from api.subscriptions.plans import DEFAULT_PLANS
from api.subscriptions.webhooks import parse_event, verify_hmac_signature
from api.services import calculate_risk, forecast, load_market_data, market_response_data

if settings.app_env == "production" and (not settings.supabase_url or not settings.supabase_service_key):
    raise RuntimeError("Production requires SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY")


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("X-Frame-Options", "DENY")
        response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
        response.headers.setdefault("Permissions-Policy", "camera=(), microphone=(), geolocation=()")
        return response


class RequestRateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, limit: int = 120, window_seconds: int = 60):
        super().__init__(app)
        self.limit = limit
        self.window_seconds = window_seconds
        self.requests: dict[str, deque[float]] = defaultdict(deque)
        self.lock = Lock()

    async def dispatch(self, request: Request, call_next):
        if request.url.path == "/health":
            return await call_next(request)
        now = monotonic()
        client = request.client.host if request.client else "unknown"
        with self.lock:
            timestamps = self.requests[client]
            while timestamps and now - timestamps[0] >= self.window_seconds:
                timestamps.popleft()
            if len(timestamps) >= self.limit:
                return JSONResponse({"detail": "Rate limit exceeded"}, status_code=429)
            timestamps.append(now)
        return await call_next(request)


app = FastAPI(title=settings.api_title, version=settings.api_version)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RequestRateLimitMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=list(settings.cors_origins),
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "DELETE"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "stock-analytics-api"}


@app.get("/api/v1/plans")
def list_plans() -> list[dict]:
    try:
        db = database()
        rows = db.request("GET", "plans", params={"order": "id"})
        return rows or [{"id": plan_id, **plan} for plan_id, plan in DEFAULT_PLANS.items()]
    except RuntimeError:
        return [{"id": plan_id, **plan} for plan_id, plan in DEFAULT_PLANS.items()]


@app.get("/api/v1/subscriptions/me")
def subscription_me(user_id: CurrentUser, db: SupabaseDatabase = Depends(database)) -> dict:
    try:
        return EntitlementService(db).account(user_id)
    except RuntimeError as exc:
        raise db_error(exc) from exc


@app.get("/api/v1/subscriptions/usage")
def subscription_usage(user_id: CurrentUser, db: SupabaseDatabase = Depends(database)) -> dict:
    try:
        service = EntitlementService(db)
        plan = service.plan(user_id)
        usage = service.usage(user_id)
        return {"plan": plan, "usage": usage}
    except RuntimeError as exc:
        raise db_error(exc) from exc


def _billing_disabled() -> HTTPException:
    return HTTPException(status_code=503, detail="Billing is disabled; no payment provider is configured")


@app.post("/api/v1/subscriptions/upgrade")
def upgrade_subscription(user_id: CurrentUser) -> dict:
    raise _billing_disabled()


@app.post("/api/v1/subscriptions/downgrade")
def downgrade_subscription(user_id: CurrentUser) -> dict:
    raise _billing_disabled()


@app.post("/api/v1/subscriptions/cancel")
def cancel_subscription(user_id: CurrentUser) -> dict:
    raise _billing_disabled()


@app.get("/api/v1/subscriptions/history")
def subscription_history(user_id: CurrentUser, db: SupabaseDatabase = Depends(database)) -> list[dict]:
    try:
        return db.request("GET", "subscription_events", params={"user_id": f"eq.{user_id}", "order": "created_at.desc"})
    except RuntimeError as exc:
        raise db_error(exc) from exc


@app.post("/api/v1/billing/checkout")
def billing_checkout(user_id: CurrentUser) -> dict:
    raise _billing_disabled()


@app.post("/api/v1/billing/webhooks/{provider}")
async def billing_webhook(provider: str, request: Request, x_signature: str | None = Header(default=None)) -> dict:
    if not settings.billing_enabled or not settings.billing_webhook_secret or not x_signature:
        raise _billing_disabled()
    payload = await request.body()
    if not verify_hmac_signature(payload, x_signature, settings.billing_webhook_secret):
        raise HTTPException(status_code=401, detail="Invalid webhook signature")
    try:
        db = database()
        event = parse_event(payload)
        existing = db.request("GET", "subscription_events", params={"provider_event_id": f"eq.{event['id']}", "limit": "1"})
        if existing:
            return {"status": "already_processed", "event_id": event["id"]}
        db.request("POST", "subscription_events", payload={"provider": provider, "provider_event_id": event["id"], "event_type": event["type"], "payload": event})
        return {"status": "accepted", "event_id": event["id"]}
    except (ValueError, RuntimeError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


def _require_admin(user_id: str) -> None:
    if user_id not in settings.admin_user_ids:
        raise HTTPException(status_code=403, detail="Administrator access required")


@app.get("/api/v1/admin/plans")
def admin_plans(user_id: CurrentUser, db: SupabaseDatabase = Depends(database)) -> list[dict]:
    _require_admin(user_id)
    try:
        return db.request("GET", "plans", params={"order": "id"})
    except RuntimeError as exc:
        raise db_error(exc) from exc


@app.patch("/api/v1/admin/plans/{plan_id}")
def update_admin_plan(plan_id: str, payload: dict, user_id: CurrentUser, db: SupabaseDatabase = Depends(database)) -> dict:
    _require_admin(user_id)
    allowed = {key: payload[key] for key in ("name", "limits", "features") if key in payload}
    if not allowed:
        raise HTTPException(status_code=422, detail="At least one plan field is required")
    try:
        rows = db.request("PATCH", "plans", params={"id": f"eq.{plan_id}"}, payload=allowed)
        if not rows:
            raise HTTPException(status_code=404, detail="Plan not found")
        return rows[0]
    except RuntimeError as exc:
        raise db_error(exc) from exc


@app.get("/api/v1/stocks", response_model=list[StockResponse])
def list_stocks() -> list[StockResponse]:
    return [StockResponse(**stock.__dict__) for stock in STOCKS.values()]


@app.get("/api/v1/stocks/{symbol}/market", response_model=MarketResponse)
def market_data(symbol: str, period: str = Query("1y", pattern=r"^\d+[dwmy]$")) -> MarketResponse:
    try:
        stock = get_stock(symbol)
        frame, source = load_market_data(stock, period)
        return MarketResponse(
            symbol=stock.symbol,
            source=source,
            delayed=True,
            fetched_at=datetime.now(timezone.utc),
            candles=market_response_data(frame),
        )
    except (ValueError, RuntimeError) as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@app.get("/api/v1/portfolios/{portfolio_id}/analytics")
def portfolio_analytics(portfolio_id: int, user_id: CurrentUser, db: SupabaseDatabase = Depends(database)) -> dict:
    try:
        rows = db.request("GET", "portfolios", params={"id": f"eq.{portfolio_id}", "user_id": f"eq.{user_id}", "select": "id,portfolio_assets(*)"})
        if not rows:
            raise HTTPException(status_code=404, detail="Portfolio not found")
        holdings = rows[0].get("portfolio_assets", [])
        prices = {}
        for holding in holdings:
            try:
                frame, _ = load_market_data(get_stock(holding["symbol"]), period="5d")
                prices[holding["symbol"]] = float(frame["close"].dropna().iloc[-1])
            except (ValueError, RuntimeError, IndexError):
                prices[holding["symbol"]] = None
        return calculate_portfolio_analytics(holdings, prices)
    except RuntimeError as exc:
        raise db_error(exc) from exc


def _owned_portfolio(portfolio_id: int, user_id: str, db: SupabaseDatabase) -> None:
    if not db.request("GET", "portfolios", params={"id": f"eq.{portfolio_id}", "user_id": f"eq.{user_id}", "select": "id"}):
        raise HTTPException(status_code=404, detail="Portfolio not found")


@app.get("/api/v1/portfolios/{portfolio_id}/transactions")
def list_transactions(portfolio_id: int, user_id: CurrentUser, db: SupabaseDatabase = Depends(database)) -> list[dict]:
    try:
        _owned_portfolio(portfolio_id, user_id, db)
        return db.request("GET", "portfolio_transactions", params={"portfolio_id": f"eq.{portfolio_id}", "user_id": f"eq.{user_id}", "order": "executed_at.desc"})
    except RuntimeError as exc:
        raise db_error(exc) from exc


@app.post("/api/v1/portfolios/{portfolio_id}/transactions", status_code=201)
def create_transaction(portfolio_id: int, payload: PortfolioTransactionCreate, user_id: CurrentUser, db: SupabaseDatabase = Depends(database)) -> dict:
    try:
        _owned_portfolio(portfolio_id, user_id, db)
        get_stock(payload.symbol)
        data = payload.model_dump(exclude_none=True)
        data.update({"portfolio_id": portfolio_id, "user_id": user_id, "symbol": payload.symbol.upper()})
        return db.request("POST", "portfolio_transactions", payload=data)[0]
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise db_error(exc) from exc


@app.patch("/api/v1/portfolios/{portfolio_id}/transactions/{transaction_id}")
def update_transaction(portfolio_id: int, transaction_id: str, payload: PortfolioTransactionUpdate, user_id: CurrentUser, db: SupabaseDatabase = Depends(database)) -> dict:
    try:
        _owned_portfolio(portfolio_id, user_id, db)
        get_stock(payload.symbol)
        data = payload.model_dump(exclude_none=True)
        data["symbol"] = payload.symbol.upper()
        rows = db.request("PATCH", "portfolio_transactions", params={"id": f"eq.{transaction_id}", "portfolio_id": f"eq.{portfolio_id}", "user_id": f"eq.{user_id}"}, payload=data)
        if not rows:
            raise HTTPException(status_code=404, detail="Transaction not found")
        return rows[0]
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise db_error(exc) from exc


@app.delete("/api/v1/portfolios/{portfolio_id}/transactions/{transaction_id}", status_code=204)
def delete_transaction(portfolio_id: int, transaction_id: str, user_id: CurrentUser, db: SupabaseDatabase = Depends(database)) -> None:
    try:
        _owned_portfolio(portfolio_id, user_id, db)
        db.request("DELETE", "portfolio_transactions", params={"id": f"eq.{transaction_id}", "portfolio_id": f"eq.{portfolio_id}", "user_id": f"eq.{user_id}"}, prefer="return=minimal")
    except RuntimeError as exc:
        raise db_error(exc) from exc


@app.get("/api/v1/portfolios/{portfolio_id}/history")
def portfolio_history(portfolio_id: int, user_id: CurrentUser, db: SupabaseDatabase = Depends(database)) -> list[dict]:
    try:
        _owned_portfolio(portfolio_id, user_id, db)
        rows = db.request("GET", "portfolio_snapshots", params={"portfolio_id": f"eq.{portfolio_id}", "user_id": f"eq.{user_id}", "order": "snapshot_date.asc"})
        previous = None
        for row in rows:
            value = row.get("market_value")
            row["daily_return"] = None if value is None or previous in (None, 0) else float(value) / previous - 1
            row["cumulative_return"] = None if value is None or not row.get("invested") else float(value) / float(row["invested"]) - 1
            if value is not None:
                previous = float(value)
        return rows
    except RuntimeError as exc:
        raise db_error(exc) from exc


@app.post("/api/v1/portfolios/{portfolio_id}/history", status_code=201)
def create_portfolio_snapshot(portfolio_id: int, payload: PortfolioSnapshotCreate, user_id: CurrentUser, db: SupabaseDatabase = Depends(database)) -> dict:
    try:
        _owned_portfolio(portfolio_id, user_id, db)
        data = payload.model_dump()
        data.update({"portfolio_id": portfolio_id, "user_id": user_id, "snapshot_date": payload.snapshot_date.date().isoformat()})
        return db.request("POST", "portfolio_snapshots", payload=data)[0]
    except RuntimeError as exc:
        raise db_error(exc) from exc


@app.get("/api/v1/alerts")
def list_alerts(user_id: CurrentUser, db: SupabaseDatabase = Depends(database)) -> list[dict]:
    try:
        return db.request("GET", "alert_rules", params={"user_id": f"eq.{user_id}", "order": "created_at.desc"})
    except RuntimeError as exc:
        raise db_error(exc) from exc


@app.post("/api/v1/alerts", status_code=201)
def create_alert(payload: AlertCreate, user_id: CurrentUser, db: SupabaseDatabase = Depends(database)) -> dict:
    try:
        EntitlementService(db).resource_limit(user_id, "stock_alerts", "alert_rules")
        get_stock(payload.symbol)
        return db.request("POST", "alert_rules", payload={**payload.model_dump(), "symbol": payload.symbol.upper(), "user_id": user_id})[0]
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise db_error(exc) from exc


@app.patch("/api/v1/alerts/{alert_id}")
def update_alert(alert_id: str, payload: dict, user_id: CurrentUser, db: SupabaseDatabase = Depends(database)) -> dict:
    allowed = {key: value for key, value in payload.items() if key in {"active", "condition", "threshold", "cooldown_minutes"}}
    try:
        rows = db.request("PATCH", "alert_rules", params={"id": f"eq.{alert_id}", "user_id": f"eq.{user_id}"}, payload=allowed)
        if not rows:
            raise HTTPException(status_code=404, detail="Alert not found")
        return rows[0]
    except RuntimeError as exc:
        raise db_error(exc) from exc


@app.delete("/api/v1/alerts/{alert_id}", status_code=204)
def delete_alert(alert_id: str, user_id: CurrentUser, db: SupabaseDatabase = Depends(database)) -> None:
    try:
        db.request("DELETE", "alert_rules", params={"id": f"eq.{alert_id}", "user_id": f"eq.{user_id}"}, prefer="return=minimal")
    except RuntimeError as exc:
        raise db_error(exc) from exc


@app.post("/api/v1/alerts/evaluate")
def evaluate_alerts(user_id: CurrentUser, db: SupabaseDatabase = Depends(database)) -> dict:
    try:
        rules = db.request("GET", "alert_rules", params={"user_id": f"eq.{user_id}", "active": "eq.true"})
        triggered = 0
        for rule in rules:
            frame, _ = load_market_data(get_stock(rule["symbol"]), period="5d")
            price = float(frame["close"].dropna().iloc[-1]) if not frame.empty else None
            if evaluate_price_alert(rule, price):
                evaluated_at = datetime.now(timezone.utc)
                event_key = f"{rule['id']}:{evaluated_at.strftime('%Y-%m-%dT%H:%M')}"
                if db.request("GET", "alert_events", params={"event_key": f"eq.{event_key}", "limit": "1"}):
                    continue
                db.request("POST", "alert_events", payload={"alert_id": rule["id"], "user_id": user_id, "observed_price": price, "evaluated_at": evaluated_at.isoformat(), "event_key": event_key})
                db.request("POST", "notifications", payload={"user_id": user_id, "category": "alert", "title": f"{rule['symbol']} alert triggered", "body": f"Price condition {rule['condition']} {rule['threshold']} was met at {price}."})
                db.request("PATCH", "alert_rules", params={"id": f"eq.{rule['id']}", "user_id": f"eq.{user_id}"}, payload={"last_triggered_at": datetime.now(timezone.utc).isoformat()})
                triggered += 1
        return {"evaluated": len(rules), "triggered": triggered}
    except (ValueError, RuntimeError) as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


def _evaluate_scheduled_alerts(db: SupabaseDatabase, evaluated_at: datetime) -> dict:
    rules = db.request("GET", "alert_rules", params={"active": "eq.true"})
    triggered = 0
    failures = 0
    for rule in rules:
        try:
            frame, _ = load_market_data(get_stock(rule["symbol"]), period="5d")
            closes = frame["close"].dropna()
            price = float(closes.iloc[-1]) if not closes.empty else None
            if not evaluate_price_alert(rule, price, evaluated_at):
                continue
            event_key = f"{rule['id']}:{evaluated_at.strftime('%Y-%m-%dT%H:%M')}"
            if db.request("GET", "alert_events", params={"event_key": f"eq.{event_key}", "limit": "1"}):
                continue
            db.request("POST", "alert_events", payload={"alert_id": rule["id"], "user_id": rule["user_id"], "observed_price": price, "evaluated_at": evaluated_at.isoformat(), "event_key": event_key})
            db.request("POST", "notifications", payload={"user_id": rule["user_id"], "category": "alert", "title": f"{rule['symbol']} alert triggered", "body": f"Price condition {rule['condition']} {rule['threshold']} was met at {price}."})
            db.request("PATCH", "alert_rules", params={"id": f"eq.{rule['id']}"}, payload={"last_triggered_at": evaluated_at.isoformat()})
            triggered += 1
        except (ValueError, RuntimeError):
            failures += 1
    return {"evaluated": len(rules), "triggered": triggered, "failures": failures, "evaluated_at": evaluated_at.isoformat()}


@app.post("/api/v1/internal/alerts/evaluate")
def scheduled_alerts(x_scheduler_token: str | None = Header(default=None)) -> dict:
    if not settings.scheduler_secret or x_scheduler_token != settings.scheduler_secret:
        raise HTTPException(status_code=401, detail="Invalid scheduler token")
    try:
        db = database()
        return _evaluate_scheduled_alerts(db, datetime.now(timezone.utc))
    except RuntimeError as exc:
        raise db_error(exc) from exc


@app.get("/api/v1/alerts/events")
def alert_events(user_id: CurrentUser, db: SupabaseDatabase = Depends(database)) -> list[dict]:
    try:
        return db.request("GET", "alert_events", params={"user_id": f"eq.{user_id}", "order": "evaluated_at.desc", "limit": "100"})
    except RuntimeError as exc:
        raise db_error(exc) from exc


@app.get("/api/v1/notifications")
def list_notifications(user_id: CurrentUser, db: SupabaseDatabase = Depends(database)) -> list[dict]:
    try:
        return db.request("GET", "notifications", params={"user_id": f"eq.{user_id}", "order": "created_at.desc", "limit": "100"})
    except RuntimeError as exc:
        raise db_error(exc) from exc


@app.patch("/api/v1/notifications/{notification_id}")
def update_notification(notification_id: str, payload: NotificationUpdate, user_id: CurrentUser, db: SupabaseDatabase = Depends(database)) -> dict:
    try:
        rows = db.request("PATCH", "notifications", params={"id": f"eq.{notification_id}", "user_id": f"eq.{user_id}"}, payload={"read_at": datetime.now(timezone.utc).isoformat() if payload.read else None})
        if not rows:
            raise HTTPException(status_code=404, detail="Notification not found")
        return rows[0]
    except RuntimeError as exc:
        raise db_error(exc) from exc


@app.get("/api/v1/news")
def news(symbol: str = "AAPL", limit: int = Query(20, ge=1, le=50)) -> list[dict]:
    try:
        articles = fetch_rss_news(settings.news_rss_url, symbol, limit)
        return [{**article, **classify_headline(article["title"])} for article in articles]
    except (OSError, ValueError, RuntimeError) as exc:
        raise HTTPException(status_code=503, detail=f"News provider unavailable: {exc}") from exc


@app.post("/api/v1/stocks/{symbol}/forecast", response_model=ForecastResponse)
def stock_forecast(symbol: str, request: ForecastRequest, user_id: CurrentUser, db: SupabaseDatabase = Depends(database)) -> ForecastResponse:
    try:
        entitlements = EntitlementService(db)
        if request.model == "ensemble":
            entitlements.check_feature(user_id, "ensemble_forecasting")
        stock = get_stock(symbol)
        frame, source = load_market_data(stock)
        current = float(frame["close"].dropna().iloc[-1])
        details = ensemble_forecast(stock, request.horizon) if request.model == "ensemble" else forecast_with_model(stock, request.model, request.horizon)
        predictions = details["predictions"]
        if request.model in {"xgboost", "lightgbm"}:
            entitlements.consume(user_id, "advanced_model_usage")
        record_usage(db, user_id, "forecast_requests")
        return ForecastResponse(
            symbol=stock.symbol,
            model=request.model,
            current_price=current,
            predictions=predictions,
            data_source=source,
            warning="Forecasts are estimates, not financial advice; Yahoo Finance data may be delayed.",
            training_cutoff=details["training_cutoff"],
            interval_available=details["interval_available"],
        )
    except ValueError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    except FileNotFoundError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise db_error(exc) from exc


@app.get("/api/v1/models", response_model=list[ModelInfo])
def supported_models() -> list[ModelInfo]:
    return [ModelInfo(**item) for item in list_models()]


@app.get("/api/v1/stocks/{symbol}/model-metrics", response_model=list[ModelMetric])
def model_metrics(symbol: str, user_id: CurrentUser) -> list[ModelMetric]:
    try:
        return [ModelMetric(**item) for item in compare_models(get_stock(symbol))]
    except (ValueError, RuntimeError) as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@app.post("/api/v1/stocks/{symbol}/backtest")
def run_backtest(symbol: str, request: BacktestRequest, user_id: CurrentUser, db: SupabaseDatabase = Depends(database)) -> dict:
    try:
        report = backtest_model(
            get_stock(symbol),
            request.model,
            request.transaction_cost,
            request.slippage,
            request.initial_capital,
            request.position_size,
            request.stop_loss,
            request.take_profit,
        )
        record_usage(db, user_id, "backtest_executions")
        db.request("POST", "backtest_history", payload={"user_id": user_id, "symbol": symbol.upper(), "model": request.model, "parameters": request.model_dump(), "report": report, "data_source": report["data_source"]})
        return report
    except ValueError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    except (RuntimeError, FileNotFoundError) as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@app.get("/api/v1/backtests")
def list_backtests(user_id: CurrentUser, db: SupabaseDatabase = Depends(database)) -> list[dict]:
    try:
        return db.request("GET", "backtest_history", params={"user_id": f"eq.{user_id}", "order": "created_at.desc", "limit": "50"})
    except RuntimeError as exc:
        raise db_error(exc) from exc


@app.get("/api/v1/stocks/{symbol}/risk", response_model=RiskResponse)
def stock_risk(symbol: str) -> RiskResponse:
    try:
        stock = get_stock(symbol)
        frame, _ = load_market_data(stock)
        base = calculate_risk(frame)
        close = frame["close"].astype(float).pct_change().dropna()
        return RiskResponse(symbol=stock.symbol, **base, **calculate_risk_metrics(close))
    except (ValueError, RuntimeError) as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


def db_error(exc: Exception) -> HTTPException:
    return HTTPException(status_code=503, detail=str(exc))


@app.get("/api/v1/me")
def profile(user_id: CurrentUser, db: SupabaseDatabase = Depends(database)) -> dict:
    rows = db.request("GET", "profiles", params={"id": f"eq.{user_id}", "limit": "1"})
    return rows[0] if rows else {"id": user_id, "display_name": None}


@app.patch("/api/v1/me")
def update_profile(payload: ProfileUpdate, user_id: CurrentUser, db: SupabaseDatabase = Depends(database)) -> dict:
    try:
        rows = db.request("PATCH", "profiles", params={"id": f"eq.{user_id}"}, payload={"display_name": payload.display_name})
        return rows[0]
    except RuntimeError as exc:
        raise db_error(exc) from exc


@app.get("/api/v1/watchlists")
def list_watchlists(user_id: CurrentUser, db: SupabaseDatabase = Depends(database)) -> list[dict]:
    try:
        return db.request("GET", "watchlists", params={"user_id": f"eq.{user_id}", "select": "*,watchlist_items(*)", "order": "created_at"})
    except RuntimeError as exc:
        raise db_error(exc) from exc


@app.post("/api/v1/watchlists", status_code=201)
def create_watchlist(payload: WatchlistCreate, user_id: CurrentUser, db: SupabaseDatabase = Depends(database)) -> dict:
    try:
        enforce_limit(db, user_id, "watchlists", "watchlists")
        return db.request("POST", "watchlists", payload={"user_id": user_id, "name": payload.name})[0]
    except ValueError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise db_error(exc) from exc


@app.patch("/api/v1/watchlists/{watchlist_id}")
def rename_watchlist(watchlist_id: int, payload: WatchlistCreate, user_id: CurrentUser, db: SupabaseDatabase = Depends(database)) -> dict:
    try:
        rows = db.request("PATCH", "watchlists", params={"id": f"eq.{watchlist_id}", "user_id": f"eq.{user_id}"}, payload={"name": payload.name})
        if not rows:
            raise HTTPException(status_code=404, detail="Watchlist not found")
        return rows[0]
    except RuntimeError as exc:
        raise db_error(exc) from exc


@app.delete("/api/v1/watchlists/{watchlist_id}", status_code=204)
def delete_watchlist(watchlist_id: int, user_id: CurrentUser, db: SupabaseDatabase = Depends(database)) -> None:
    try:
        db.request("DELETE", "watchlists", params={"id": f"eq.{watchlist_id}", "user_id": f"eq.{user_id}"}, prefer="return=minimal")
    except RuntimeError as exc:
        raise db_error(exc) from exc


@app.post("/api/v1/watchlists/{watchlist_id}/items", status_code=201)
def add_watchlist_item(watchlist_id: int, payload: WatchlistItemCreate, user_id: CurrentUser, db: SupabaseDatabase = Depends(database)) -> dict:
    try:
        get_stock(payload.symbol)
        owner = db.request("GET", "watchlists", params={"id": f"eq.{watchlist_id}", "user_id": f"eq.{user_id}", "select": "id"})
        if not owner:
            raise HTTPException(status_code=404, detail="Watchlist not found")
        return db.request("POST", "watchlist_items", payload={"watchlist_id": watchlist_id, "user_id": user_id, "symbol": payload.symbol.upper()})[0]
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise db_error(exc) from exc


@app.delete("/api/v1/watchlists/{watchlist_id}/items/{symbol}", status_code=204)
def delete_watchlist_item(watchlist_id: int, symbol: str, user_id: CurrentUser, db: SupabaseDatabase = Depends(database)) -> None:
    try:
        db.request("DELETE", "watchlist_items", params={"watchlist_id": f"eq.{watchlist_id}", "symbol": f"eq.{symbol.upper()}", "user_id": f"eq.{user_id}"}, prefer="return=minimal")
    except RuntimeError as exc:
        raise db_error(exc) from exc


@app.get("/api/v1/portfolios")
def list_portfolios(user_id: CurrentUser, db: SupabaseDatabase = Depends(database)) -> list[dict]:
    try:
        return db.request("GET", "portfolios", params={"user_id": f"eq.{user_id}", "select": "*,portfolio_assets(*)", "order": "created_at"})
    except RuntimeError as exc:
        raise db_error(exc) from exc


@app.post("/api/v1/portfolios", status_code=201)
def create_portfolio(payload: PortfolioCreate, user_id: CurrentUser, db: SupabaseDatabase = Depends(database)) -> dict:
    try:
        enforce_limit(db, user_id, "portfolios", "portfolios")
        return db.request("POST", "portfolios", payload={"user_id": user_id, "name": payload.name})[0]
    except ValueError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise db_error(exc) from exc


@app.patch("/api/v1/portfolios/{portfolio_id}")
def rename_portfolio(portfolio_id: int, payload: PortfolioCreate, user_id: CurrentUser, db: SupabaseDatabase = Depends(database)) -> dict:
    try:
        rows = db.request("PATCH", "portfolios", params={"id": f"eq.{portfolio_id}", "user_id": f"eq.{user_id}"}, payload={"name": payload.name, "updated_at": datetime.now(timezone.utc).isoformat()})
        if not rows:
            raise HTTPException(status_code=404, detail="Portfolio not found")
        return rows[0]
    except RuntimeError as exc:
        raise db_error(exc) from exc


@app.delete("/api/v1/portfolios/{portfolio_id}", status_code=204)
def delete_portfolio(portfolio_id: int, user_id: CurrentUser, db: SupabaseDatabase = Depends(database)) -> None:
    try:
        db.request("DELETE", "portfolios", params={"id": f"eq.{portfolio_id}", "user_id": f"eq.{user_id}"}, prefer="return=minimal")
    except RuntimeError as exc:
        raise db_error(exc) from exc


@app.post("/api/v1/portfolios/{portfolio_id}/assets", status_code=201)
def add_portfolio_asset(portfolio_id: int, payload: PortfolioAssetCreate, user_id: CurrentUser, db: SupabaseDatabase = Depends(database)) -> dict:
    try:
        get_stock(payload.symbol)
        owner = db.request("GET", "portfolios", params={"id": f"eq.{portfolio_id}", "user_id": f"eq.{user_id}", "select": "id"})
        if not owner:
            raise HTTPException(status_code=404, detail="Portfolio not found")
        return db.request("POST", "portfolio_assets", payload={**payload.model_dump(), "portfolio_id": portfolio_id, "user_id": user_id, "symbol": payload.symbol.upper()})[0]
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise db_error(exc) from exc


@app.patch("/api/v1/portfolios/{portfolio_id}/assets/{asset_id}")
def update_portfolio_asset(
    portfolio_id: int,
    asset_id: int,
    payload: PortfolioAssetCreate,
    user_id: CurrentUser,
    db: SupabaseDatabase = Depends(database),
) -> dict:
    try:
        get_stock(payload.symbol)
        rows = db.request(
            "PATCH",
            "portfolio_assets",
            params={"id": f"eq.{asset_id}", "portfolio_id": f"eq.{portfolio_id}", "user_id": f"eq.{user_id}"},
            payload={**payload.model_dump(), "symbol": payload.symbol.upper(), "updated_at": datetime.now(timezone.utc).isoformat()},
        )
        if not rows:
            raise HTTPException(status_code=404, detail="Portfolio asset not found")
        return rows[0]
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise db_error(exc) from exc


@app.delete("/api/v1/portfolios/{portfolio_id}/assets/{asset_id}", status_code=204)
def delete_portfolio_asset(portfolio_id: int, asset_id: int, user_id: CurrentUser, db: SupabaseDatabase = Depends(database)) -> None:
    try:
        db.request("DELETE", "portfolio_assets", params={"id": f"eq.{asset_id}", "portfolio_id": f"eq.{portfolio_id}", "user_id": f"eq.{user_id}"}, prefer="return=minimal")
    except RuntimeError as exc:
        raise db_error(exc) from exc


@app.get("/api/v1/portfolios/{portfolio_id}/summary")
def portfolio_summary(portfolio_id: int, user_id: CurrentUser, db: SupabaseDatabase = Depends(database)) -> dict:
    try:
        portfolios = db.request(
            "GET",
            "portfolios",
            params={"id": f"eq.{portfolio_id}", "user_id": f"eq.{user_id}", "select": "id,portfolio_assets(*)"},
        )
        if not portfolios:
            raise HTTPException(status_code=404, detail="Portfolio not found")
        assets = []
        total_cost = 0.0
        current_value = 0.0
        for asset in portfolios[0].get("portfolio_assets", []):
            quantity = float(asset["quantity"])
            purchase_price = float(asset["purchase_price"])
            cost = quantity * purchase_price
            total_cost += cost
            market_price = None
            try:
                frame, _ = load_market_data(get_stock(asset["symbol"]))
                market_price = float(frame["close"].dropna().iloc[-1])
                current_value += quantity * market_price
            except (ValueError, RuntimeError, IndexError):
                pass
            assets.append({**asset, "market_price": market_price, "cost_basis": cost, "market_value": None if market_price is None else quantity * market_price})
        return {"portfolio_id": portfolio_id, "cost_basis": total_cost, "current_value": current_value, "assets": assets}
    except RuntimeError as exc:
        raise db_error(exc) from exc


@app.get("/api/v1/predictions")
def list_predictions(user_id: CurrentUser, symbol: str | None = None, db: SupabaseDatabase = Depends(database)) -> list[dict]:
    try:
        params = {"user_id": f"eq.{user_id}", "select": "*", "order": "created_at.desc"}
        if symbol:
            params["symbol"] = f"eq.{symbol.upper()}"
        return db.request("GET", "prediction_history", params=params)
    except RuntimeError as exc:
        raise db_error(exc) from exc


@app.post("/api/v1/predictions", status_code=201)
def save_prediction(payload: PredictionSave, user_id: CurrentUser, db: SupabaseDatabase = Depends(database)) -> dict:
    try:
        enforce_limit(db, user_id, "prediction_history", "prediction_history")
        return db.request("POST", "prediction_history", payload={**payload.model_dump(), "user_id": user_id, "symbol": payload.symbol.upper()})[0]
    except ValueError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise db_error(exc) from exc


@app.delete("/api/v1/predictions/{prediction_id}", status_code=204)
def delete_prediction(prediction_id: int, user_id: CurrentUser, db: SupabaseDatabase = Depends(database)) -> None:
    try:
        db.request("DELETE", "prediction_history", params={"id": f"eq.{prediction_id}", "user_id": f"eq.{user_id}"}, prefer="return=minimal")
    except RuntimeError as exc:
        raise db_error(exc) from exc
