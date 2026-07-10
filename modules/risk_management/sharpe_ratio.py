import numpy as np
from modules.utils.logger import get_logger

logger = get_logger(__name__)

def calculate_sharpe_ratio(
    returns,
    risk_free_rate: float = 0.0
):
    """
    Calculates Sharpe Ratio.
    """

    logger.info("Calculating Sharpe Ratio")

    try:
        returns = np.array(returns, dtype=float)
    except Exception:
        logger.warning("Invalid returns provided to calculate_sharpe_ratio; returning 0.0")
        return 0.0

    if returns.size == 0:
        return 0.0

    excess_returns = returns - risk_free_rate

    std_dev = np.std(excess_returns)

    if std_dev == 0 or np.isnan(std_dev):
        return 0.0

    sharpe = np.mean(excess_returns) / std_dev
    if not np.isfinite(sharpe):
        return 0.0
    return float(sharpe)
