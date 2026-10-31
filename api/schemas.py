from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class StockResponse(BaseModel):
    symbol: str
    name: str
    exchange: str
    ticker: str
    currency: str


class Candle(BaseModel):
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float = Field(ge=0)
    sma_20: float | None = None
    ema_20: float | None = None
    rsi: float | None = None
    macd: float | None = None
    macd_signal: float | None = None
    bb_upper: float | None = None
    bb_lower: float | None = None


class MarketResponse(BaseModel):
    symbol: str
    source: Literal["cache", "yahoo_finance"]
    delayed: bool
    fetched_at: datetime
    candles: list[Candle]


class ForecastRequest(BaseModel):
    horizon: int = Field(default=1, ge=1, le=30)
    model: Literal["linear_regression", "random_forest", "xgboost", "lightgbm", "arima", "sarima", "ensemble"] = "random_forest"


class ForecastResponse(BaseModel):
    symbol: str
    model: str
    current_price: float
    predictions: list[float]
    data_source: str
    warning: str
    training_cutoff: datetime | None = None
    interval_available: bool = False
    lower_bound: list[float] | None = None
    upper_bound: list[float] | None = None


class ModelInfo(BaseModel):
    name: str
    family: str
    available: bool
    reason: str | None = None


class ModelMetric(BaseModel):
    model: str
    available: bool
    mae: float | None = None
    rmse: float | None = None
    mape: float | None = None
    smape: float | None = None
    r2: float | None = None
    directional_accuracy: float | None = None
    trained_at: datetime | None = None
    evaluation_period: str | None = None
    reason: str | None = None


class BacktestRequest(BaseModel):
    model: Literal["linear_regression", "random_forest", "xgboost", "lightgbm"] = "random_forest"
    transaction_cost: float = Field(default=0.001, ge=0, le=0.1)
    slippage: float = Field(default=0.0005, ge=0, le=0.1)
    initial_capital: float = Field(default=100000, gt=0)
    position_size: float = Field(default=1, gt=0, le=1)
    stop_loss: float | None = Field(default=None, gt=0, lt=1)
    take_profit: float | None = Field(default=None, gt=0)


class AlertCreate(BaseModel):
    symbol: str = Field(min_length=1, max_length=20)
    condition: Literal["above", "below"]
    threshold: float = Field(gt=0)
    cooldown_minutes: int = Field(default=60, ge=0, le=10080)


class NotificationUpdate(BaseModel):
    read: bool = True


class PortfolioTransactionCreate(BaseModel):
    symbol: str = Field(min_length=1, max_length=20)
    side: Literal["buy", "sell"]
    quantity: float = Field(gt=0)
    price: float = Field(gt=0)
    fee: float = Field(default=0, ge=0)
    executed_at: datetime | None = None


class PortfolioTransactionUpdate(PortfolioTransactionCreate):
    pass


class PortfolioSnapshotCreate(BaseModel):
    snapshot_date: datetime
    invested: float = Field(ge=0)
    market_value: float | None = Field(default=None, ge=0)


class RiskResponse(BaseModel):
    symbol: str
    observations: int
    annualized_volatility: float
    sharpe_ratio: float
    max_drawdown: float
    sortino_ratio: float = 0.0
    value_at_risk: float = 0.0
    conditional_value_at_risk: float = 0.0
    evaluation_period: str = "daily returns"
    annualization_factor: float = 252.0
    risk_free_rate: float = 0.0


class ProfileUpdate(BaseModel):
    display_name: str = Field(min_length=1, max_length=80)


class WatchlistCreate(BaseModel):
    name: str = Field(min_length=1, max_length=80)


class WatchlistItemCreate(BaseModel):
    symbol: str = Field(min_length=1, max_length=20)


class PortfolioCreate(BaseModel):
    name: str = Field(min_length=1, max_length=80)


class PortfolioAssetCreate(BaseModel):
    symbol: str = Field(min_length=1, max_length=20)
    quantity: float = Field(gt=0)
    purchase_price: float = Field(gt=0)


class PredictionSave(BaseModel):
    symbol: str = Field(min_length=1, max_length=20)
    model: str = Field(min_length=1, max_length=80)
    horizon: int = Field(ge=1, le=30)
    current_price: float = Field(gt=0)
    predictions: list[float]
    model_version: str = Field(default="unknown", max_length=80)
    evaluation_metadata: dict[str, object] = Field(default_factory=dict)
