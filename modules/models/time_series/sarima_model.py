import joblib
import pandas as pd
from statsmodels.tsa.statespace.sarimax import SARIMAX
from modules.utils.logger import get_logger

logger = get_logger(__name__)

class SARIMAModel:
    def __init__(
        self,
        order=(5, 1, 0),
        seasonal_order=(1, 1, 1, 12)
    ):
        """
        seasonal_order = (P, D, Q, m)
        m = seasonal period (e.g., 12 for monthly seasonality)
        """
        self.order = order
        self.seasonal_order = seasonal_order
        self.model_fit = None

    def train(self, series: pd.Series):
        logger.info(
            f"Training SARIMA model order={self.order}, "
            f"seasonal_order={self.seasonal_order}"
        )
        model = SARIMAX(
            series,
            order=self.order,
            seasonal_order=self.seasonal_order,
            enforce_stationarity=False,
            enforce_invertibility=False
        )
        self.model_fit = model.fit(disp=False)

    def forecast(self, steps: int = 1):
        if self.model_fit is None:
            raise RuntimeError("SARIMA model is not trained")
        return self.model_fit.forecast(steps=steps)

    def save(self, path: str = "models_saved/sarima_model.pkl"):
        joblib.dump(self.model_fit, path)
        logger.info(f"SARIMA model saved at {path}")

    def load(self, path: str = "models_saved/sarima_model.pkl"):
        self.model_fit = joblib.load(path)
        logger.info("SARIMA model loaded")
