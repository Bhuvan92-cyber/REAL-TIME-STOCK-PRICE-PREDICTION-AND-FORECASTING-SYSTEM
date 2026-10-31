from __future__ import annotations

import numpy as np
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


def evaluate_forecast(actual, predicted) -> dict[str, float]:
    y_true = np.asarray(actual, dtype=float)
    y_pred = np.asarray(predicted, dtype=float)
    if y_true.shape != y_pred.shape or y_true.size == 0:
        raise ValueError("actual and predicted must be non-empty arrays of equal shape")
    errors = y_true - y_pred
    nonzero = np.abs(y_true) > np.finfo(float).eps
    mape = float(np.mean(np.abs(errors[nonzero] / y_true[nonzero])) * 100) if nonzero.any() else 0.0
    smape_denominator = np.abs(y_true) + np.abs(y_pred)
    smape = float(np.mean(2 * np.abs(errors[smape_denominator > 0]) / smape_denominator[smape_denominator > 0]) * 100) if (smape_denominator > 0).any() else 0.0
    actual_direction = np.sign(np.diff(y_true))
    predicted_direction = np.sign(np.diff(y_pred))
    directional = float(np.mean(actual_direction == predicted_direction) * 100) if actual_direction.size else 0.0
    return {
        "mae": float(mean_absolute_error(y_true, y_pred)),
        "rmse": float(np.sqrt(mean_squared_error(y_true, y_pred))),
        "mape": mape,
        "smape": smape,
        "r2": float(r2_score(y_true, y_pred)) if y_true.size > 1 else 0.0,
        "directional_accuracy": directional,
    }


def naive_last_value(actual) -> np.ndarray:
    values = np.asarray(actual, dtype=float)
    if values.size < 2:
        raise ValueError("At least two observations are required for a naive baseline")
    return values[:-1]
