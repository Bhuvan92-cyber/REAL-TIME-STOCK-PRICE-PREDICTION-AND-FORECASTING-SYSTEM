import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import GridSearchCV
from modules.utils.logger import get_logger

logger = get_logger(__name__)

def tune_random_forest(
    X: pd.DataFrame,
    y: pd.Series
):
    """
    Hyperparameter tuning for Random Forest Regressor.
    """
    logger.info("Starting Random Forest hyperparameter tuning")

    param_grid = {
        "n_estimators": [100, 200],
        "max_depth": [None, 10, 20],
        "min_samples_split": [2, 5]
    }

    rf = RandomForestRegressor(random_state=42)

    grid_search = GridSearchCV(
        rf,
        param_grid,
        cv=3,
        scoring="neg_mean_squared_error",
        n_jobs=-1
    )

    grid_search.fit(X, y)

    logger.info(f"Best RF Params: {grid_search.best_params_}")
    return grid_search.best_estimator_
