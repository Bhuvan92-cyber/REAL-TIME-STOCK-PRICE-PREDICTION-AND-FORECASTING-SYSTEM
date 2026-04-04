import numpy as np
import pandas as pd
from modules.models.regression.linear_regression import LinearRegressionModel
from modules.models.time_series.arima_model import ARIMAModel
from modules.models.deep_learning.lstm_model import LSTMModel

def test_linear_regression_model():
    X = pd.DataFrame({"x": [1, 2, 3, 4, 5]})
    y = pd.Series([2, 4, 6, 8, 10])

    model = LinearRegressionModel()
    model.train(X, y)
    preds = model.predict(X)

    assert len(preds) == len(y)

def test_arima_model():
    series = pd.Series(np.random.rand(50))

    model = ARIMAModel(order=(1, 1, 1))
    model.train(series)
    forecast = model.forecast(steps=3)

    assert len(forecast) == 3

def test_lstm_model_initialization():
    model = LSTMModel(seq_length=10)
    assert model.seq_length == 10
