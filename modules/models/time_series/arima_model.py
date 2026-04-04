import joblib
import pandas as pd
from statsmodels.tsa.arima.model import ARIMA
from modules.utils.logger import get_logger

logger = get_logger(__name__)

class ARIMAModel:
    def __init__(self, order=(5, 1, 0)):
        """
        order = (p, d, q)
        p = autoregressive terms
        d = differencing
        q = moving average terms
        """
        self.order = order
        self.model_fit = None

    def train(self, series: pd.Series):
        logger.info(f"Training ARIMA model with order={self.order}")
        model = ARIMA(series, order=self.order)
        self.model_fit = model.fit()

    def forecast(self, steps: int = 1):
        if self.model_fit is None:
            raise RuntimeError("ARIMA model is not trained")
        return self.model_fit.forecast(steps=steps)

    def save(self, path: str = "models_saved/arima_model.pkl"):
        joblib.dump(self.model_fit, path)
        logger.info(f"ARIMA model saved at {path}")

    def load(self, path: str = "models_saved/arima_model.pkl"):
        self.model_fit = joblib.load(path)
        logger.info("ARIMA model loaded")
