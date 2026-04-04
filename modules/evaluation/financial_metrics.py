import numpy as np
from modules.utils.logger import get_logger

logger = get_logger(__name__)

def sharpe_ratio(returns, risk_free_rate=0.0):
    excess_returns = returns - risk_free_rate
    return np.mean(excess_returns) / np.std(excess_returns)

def max_drawdown(cumulative_returns):
    peak = np.maximum.accumulate(cumulative_returns)
    drawdown = (cumulative_returns - peak) / peak
    return drawdown.min()

def financial_evaluation(returns):
    """
    Evaluates financial performance of predictions.
    """

    logger.info("Evaluating financial performance metrics")

    returns = np.array(returns)
    cumulative_returns = np.cumsum(returns)

    metrics = {
        "Sharpe_Ratio": sharpe_ratio(returns),
        "Maximum_Drawdown": max_drawdown(cumulative_returns),
        "Total_Return": cumulative_returns[-1]
    }

    logger.info(f"Financial Metrics: {metrics}")
    return metrics
