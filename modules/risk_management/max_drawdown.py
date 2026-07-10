import numpy as np
from modules.utils.logger import get_logger

logger = get_logger(__name__)

def calculate_max_drawdown(cumulative_returns):
    """
    Calculates Maximum Drawdown.
    """

    logger.info("Calculating Maximum Drawdown")

    try:
        cumulative_returns = np.array(cumulative_returns, dtype=float)
    except Exception:
        logger.warning("Invalid cumulative_returns provided to calculate_max_drawdown; returning 0.0")
        return 0.0

    if cumulative_returns.size == 0:
        return 0.0

    # Avoid division by zero in case peak contains zeros
    peak = np.maximum.accumulate(cumulative_returns)
    # If all zeros or NaN
    if np.all(peak == 0) or np.isnan(peak).all():
        return 0.0

    with np.errstate(divide='ignore', invalid='ignore'):
        drawdown = (cumulative_returns - peak) / peak
        drawdown = np.nan_to_num(drawdown, neginf=0.0, posinf=0.0)

    return float(np.min(drawdown))
