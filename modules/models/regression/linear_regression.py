import joblib
import pandas as pd
from sklearn.linear_model import LinearRegression
from modules.utils.logger import get_logger

logger = get_logger(__name__)

class LinearRegressionModel:
    def __init__(self):
        self.model = LinearRegression()

    def train(self, X: pd.DataFrame, y: pd.Series):
        logger.info("Training Linear Regression model")
        self.model.fit(X, y)

    def predict(self, X: pd.DataFrame):
        return self.model.predict(X)

    def save(self, path: str = "models_saved/linear_regression.pkl"):
        joblib.dump(self.model, path)
        logger.info(f"Linear Regression model saved at {path}")

    def load(self, path: str = "models_saved/linear_regression.pkl"):
        self.model = joblib.load(path)
        logger.info("Linear Regression model loaded")
