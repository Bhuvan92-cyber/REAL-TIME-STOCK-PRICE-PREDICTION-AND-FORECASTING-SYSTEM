from __future__ import annotations

import numpy as np


def calculate_risk_metrics(returns, confidence: float = 0.95) -> dict[str, float]:
    values = np.asarray(returns, dtype=float)
    values = values[np.isfinite(values)]
    if values.size < 2:
        raise ValueError("At least two returns are required")
    downside = values[values < 0]
    var = float(np.quantile(values, 1 - confidence))
    cvar_values = values[values <= var]
    return {
        "sortino_ratio": float(np.mean(values) / np.std(downside, ddof=1) * np.sqrt(252)) if downside.size > 1 and np.std(downside, ddof=1) > 0 else 0.0,
        "value_at_risk": abs(var),
        "conditional_value_at_risk": abs(float(np.mean(cvar_values))) if cvar_values.size else abs(var),
        "confidence": confidence,
        "annualization_factor": 252.0,
    }
