import numpy as np
from modules.utils.logger import get_logger

logger = get_logger(__name__)

def calculate_max_drawdown(cumulative_returns):
    """
    Calculates Maximum Drawdown.
    """

    logger.info("Calculating Maximum Drawdown")

    cumulative_returns = np.array(cumulative_returns)
    peak = np.maximum.accumulate(cumulative_returns)
    drawdown = (cumulative_returns - peak) / peak

    return drawdown.min()
