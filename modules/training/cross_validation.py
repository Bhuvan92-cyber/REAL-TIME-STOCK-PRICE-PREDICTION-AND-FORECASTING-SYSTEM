import numpy as np
import pandas as pd
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import mean_squared_error
from modules.utils.logger import get_logger

logger = get_logger(__name__)

def time_series_cross_validation(
    model,
    X: pd.DataFrame,
    y: pd.Series,
    splits: int = 5
):
    """
    Performs TimeSeriesSplit cross-validation.
    """
    logger.info("Starting time-series cross-validation")

    tscv = TimeSeriesSplit(n_splits=splits)
    rmse_scores = []

    for train_index, test_index in tscv.split(X):
        X_train, X_test = X.iloc[train_index], X.iloc[test_index]
        y_train, y_test = y.iloc[train_index], y.iloc[test_index]

        model.train(X_train, y_train)
        preds = model.predict(X_test)

        rmse = np.sqrt(mean_squared_error(y_test, preds))
        rmse_scores.append(rmse)

    avg_rmse = np.mean(rmse_scores)
    logger.info(f"Average RMSE across folds: {avg_rmse}")
    return avg_rmse
