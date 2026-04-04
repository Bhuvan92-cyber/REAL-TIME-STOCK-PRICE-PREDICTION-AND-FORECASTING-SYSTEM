import numpy as np
import pandas as pd

from modules.utils.logger import get_logger
from modules.ingestion.live_data_fetcher import fetch_live_stock_data

logger = get_logger(__name__)


class ModelPredictor:
    """
    Generic predictor wrapper for trained models.
    Supports regression, time-series, and deep learning models.
    """

    def __init__(self, model, model_type: str = "regression"):
        """
        model_type: ['regression', 'time_series', 'deep_learning']
        """
        self.model = model
        self.model_type = model_type

        # ticker mapping
        self.ticker_map = {
            "AAPL": "AAPL",
            "TCS": "TCS.NS",
            "NIFTY50": "^NSEI"
        }

    def get_live_data(self, selected_stock):
        """
        Fetch live data for the selected stock.
        """

        if selected_stock not in self.ticker_map:
            raise ValueError(f"Unsupported stock: {selected_stock}")

        ticker_symbol = self.ticker_map[selected_stock]

        logger.info(f"Fetching live data for {ticker_symbol}")

        df = fetch_live_stock_data(ticker_symbol)

        return df

    def predict(self, X):
        """
        Performs prediction based on model type.
        """

        logger.info(f"Running prediction using {self.model_type} model")

        if self.model_type == "regression":

            if isinstance(X, pd.DataFrame):
                return self.model.predict(X)

        elif self.model_type == "time_series":

            # ARIMA / SARIMA
            return self.model.forecast(steps=1)[0]

        elif self.model_type == "deep_learning":

            # LSTM / CNN-LSTM
            X = np.array(X).reshape(1, -1, 1)
            return float(self.model.predict(X)[0][0])

        else:
            raise ValueError("Unsupported model type")