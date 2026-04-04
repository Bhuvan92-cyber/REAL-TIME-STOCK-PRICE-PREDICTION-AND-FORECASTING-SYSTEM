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

    returns = np.array(returns)
    excess_returns = returns - risk_free_rate

    std_dev = np.std(excess_returns)

    if std_dev == 0:
        return 0.0

    sharpe = np.mean(excess_returns) / std_dev
    return sharpe
