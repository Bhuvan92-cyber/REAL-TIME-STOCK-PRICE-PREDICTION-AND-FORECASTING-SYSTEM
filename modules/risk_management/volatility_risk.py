import numpy as np
from modules.utils.logger import get_logger

logger = get_logger(__name__)

def calculate_volatility_risk(
    returns,
    window: int = 20
):
    """
    Calculates rolling volatility risk.
    """

    logger.info("Calculating volatility risk")

    returns = np.array(returns)

    if len(returns) < window:
        return float(np.std(returns))

    rolling_volatility = [
        np.std(returns[i - window:i])
        for i in range(window, len(returns))
    ]

    return float(np.mean(rolling_volatility))
