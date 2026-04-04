import pandas as pd
from sklearn.model_selection import train_test_split
from modules.utils.logger import get_logger

logger = get_logger(__name__)

def train_regression_model(
    model,
    df: pd.DataFrame,
    target_col: str = "close",
    test_size: float = 0.2
):
    """
    Trains any regression model (Linear, RF, XGBoost).
    """
    logger.info("Starting regression model training")

    X = df.drop(columns=[target_col])
    X = X.select_dtypes(include=["int64", "float64"])
    y = df[target_col]

    # Time-series safe split (NO shuffle)
    split_index = int(len(df) * (1 - test_size))
    X_train, X_test = X[:split_index], X[split_index:]
    y_train, y_test = y[:split_index], y[split_index:]

    model.train(X_train, y_train)
    predictions = model.predict(X_test)

    logger.info("Regression model training completed")
    return predictions, y_test


def train_time_series_model(
    model,
    series: pd.Series,
    forecast_steps: int = 1
):
    """
    Trains ARIMA / SARIMA models and forecasts future values.
    """
    logger.info("Starting time-series model training")

    model.train(series)
    forecast = model.forecast(steps=forecast_steps)

    logger.info("Time-series model training completed")
    return forecast
