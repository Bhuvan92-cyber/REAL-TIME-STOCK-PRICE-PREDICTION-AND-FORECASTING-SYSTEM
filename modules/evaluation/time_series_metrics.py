import numpy as np
from sklearn.metrics import mean_squared_error, mean_absolute_error
from modules.utils.logger import get_logger

logger = get_logger(__name__)

def time_series_evaluation(actual, forecast):
    """
    Evaluates time-series predictions.
    """

    logger.info("Evaluating time-series model performance")

    actual = np.array(actual)
    forecast = np.array(forecast)

    mse = mean_squared_error(actual, forecast)
    rmse = np.sqrt(mse)
    mae = mean_absolute_error(actual, forecast)
    mape = np.mean(np.abs((actual - forecast) / actual)) * 100

    results = {
        "MSE": mse,
        "RMSE": rmse,
        "MAE": mae,
        "MAPE (%)": mape
    }

    logger.info(f"Time-Series Metrics: {results}")
    return results
