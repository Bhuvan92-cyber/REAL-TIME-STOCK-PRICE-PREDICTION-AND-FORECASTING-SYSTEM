import joblib
import pandas as pd
from prophet import Prophet
from modules.utils.logger import get_logger

logger = get_logger(__name__)

class ProphetModel:
    def __init__(self):
        self.model = Prophet(
            daily_seasonality=True,
            yearly_seasonality=True,
            weekly_seasonality=True
        )

    def train(self, df: pd.DataFrame):
        """
        Input DataFrame must have:
        ds -> date
        y  -> target (close price)
        """
        logger.info("Training Prophet model")
        self.model.fit(df)

    def forecast(self, periods: int = 1):
        future = self.model.make_future_dataframe(periods=periods)
        forecast = self.model.predict(future)
        return forecast[["ds", "yhat", "yhat_lower", "yhat_upper"]]

    def save(self, path: str = "models_saved/prophet_model.pkl"):
        joblib.dump(self.model, path)
        logger.info(f"Prophet model saved at {path}")

    def load(self, path: str = "models_saved/prophet_model.pkl"):
        self.model = joblib.load(path)
        logger.info("Prophet model loaded")
