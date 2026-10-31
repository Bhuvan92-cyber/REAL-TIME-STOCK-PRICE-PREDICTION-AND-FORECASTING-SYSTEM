from __future__ import annotations

from dataclasses import dataclass
from importlib.util import find_spec
from typing import Callable


@dataclass(frozen=True)
class ModelSpec:
    name: str
    factory: Callable[[], object]
    family: str
    available: bool
    reason: str | None = None


def _optional_factory(module: str, class_name: str):
    def factory():
        imported = __import__(module, fromlist=[class_name])
        return getattr(imported, class_name)()

    try:
        __import__(module)
        return factory, True, None
    except ImportError as exc:
        return factory, False, str(exc)


_xgb_factory, _xgb_available, _xgb_reason = _optional_factory(
    "modules.models.regression.xgboost_model", "XGBoostModel"
)
_lgb_factory, _lgb_available, _lgb_reason = _optional_factory(
    "modules.models.regression.lightgbm_model", "LightGBMModel"
)
_xgb_available = find_spec("xgboost") is not None
_lgb_available = find_spec("lightgbm") is not None
if not _xgb_available:
    _xgb_reason = "Install the optional xgboost package to enable this model"
if not _lgb_available:
    _lgb_reason = "Install the optional lightgbm package to enable this model"

MODEL_REGISTRY = {
    "linear_regression": ModelSpec("linear_regression", lambda: _load("modules.models.regression.linear_regression", "LinearRegressionModel"), "regression", True),
    "random_forest": ModelSpec("random_forest", lambda: _load("modules.models.regression.random_forest", "RandomForestModel"), "regression", True),
    "xgboost": ModelSpec("xgboost", _xgb_factory, "regression", _xgb_available, _xgb_reason),
    "lightgbm": ModelSpec("lightgbm", _lgb_factory, "regression", _lgb_available, _lgb_reason),
    "arima": ModelSpec("arima", lambda: _load("modules.models.time_series.arima_model", "ARIMAModel"), "time_series", True),
    "sarima": ModelSpec("sarima", lambda: _load("modules.models.time_series.sarima_model", "SARIMAModel"), "time_series", True),
}


def _load(module: str, class_name: str):
    imported = __import__(module, fromlist=[class_name])
    return getattr(imported, class_name)()


def list_models() -> list[dict]:
    return [
        {
            "name": spec.name,
            "family": spec.family,
            "available": spec.available,
            "reason": spec.reason,
        }
        for spec in MODEL_REGISTRY.values()
    ]


def create_model(name: str):
    try:
        spec = MODEL_REGISTRY[name]
    except KeyError as exc:
        raise ValueError(f"Unknown model: {name}") from exc
    if not spec.available:
        raise RuntimeError(f"Model {name} is unavailable: {spec.reason}")
    return spec.factory()
