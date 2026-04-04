import joblib
import pandas as pd
from xgboost import XGBRegressor
from modules.utils.logger import get_logger

logger = get_logger(__name__)

class XGBoostModel:
    def __init__(self):
        self.model = XGBRegressor(
            n_estimators=300,
            learning_rate=0.05,
            max_depth=6,
            subsample=0.8,
            colsample_bytree=0.8,
            objective="reg:squarederror",
            random_state=42
        )

    def train(self, X: pd.DataFrame, y: pd.Series):
        logger.info("Training XGBoost Regressor")
        self.model.fit(X, y)

    def predict(self, X: pd.DataFrame):
        return self.model.predict(X)

    def save(self, path: str = "models_saved/xgboost_model.pkl"):
        joblib.dump(self.model, path)
        logger.info(f"XGBoost model saved at {path}")

    def load(self, path: str = "models_saved/xgboost_model.pkl"):
        self.model = joblib.load(path)
        logger.info("XGBoost model loaded")
