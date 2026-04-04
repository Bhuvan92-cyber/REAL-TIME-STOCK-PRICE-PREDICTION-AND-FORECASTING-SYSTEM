import joblib
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from modules.utils.logger import get_logger

logger = get_logger(__name__)

class RandomForestModel:
    def __init__(
        self,
        n_estimators: int = 200,
        max_depth: int = None,
        random_state: int = 42
    ):
        self.model = RandomForestRegressor(
            n_estimators=n_estimators,
            max_depth=max_depth,
            random_state=random_state,
            n_jobs=-1
        )

    def train(self, X: pd.DataFrame, y: pd.Series):
        logger.info("Training Random Forest Regressor")
        self.model.fit(X, y)

    def predict(self, X: pd.DataFrame):
        return self.model.predict(X)

    def save(self, path: str = "models_saved/random_forest.pkl"):
        joblib.dump(self.model, path)
        logger.info(f"Random Forest model saved at {path}")

    def load(self, path: str = "models_saved/random_forest.pkl"):
        self.model = joblib.load(path)
        logger.info("Random Forest model loaded")
