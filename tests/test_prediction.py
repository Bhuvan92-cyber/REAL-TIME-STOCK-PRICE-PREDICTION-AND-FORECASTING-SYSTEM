import numpy as np
from modules.prediction.signal_generator import generate_signal
from modules.prediction.predictor import ModelPredictor

class DummyModel:
    def predict(self, X):
        return [110]

def test_signal_generator():
    signal = generate_signal(
        current_price=100,
        predicted_price=110
    )

    assert signal["signal"] in ["BUY", "SELL", "HOLD"]

def test_model_predictor_regression():
    model = DummyModel()
    predictor = ModelPredictor(model, model_type="regression")

    prediction = predictor.predict([[1]])
    assert prediction[0] == 110
