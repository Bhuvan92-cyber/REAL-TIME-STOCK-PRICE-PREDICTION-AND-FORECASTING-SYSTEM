from __future__ import annotations

import joblib

try:
    from lightgbm import LGBMRegressor
except ImportError as exc:  # Optional dependency; registry reports availability.
    LGBMRegressor = None
    _IMPORT_ERROR = exc


class LightGBMModel:
    name = "lightgbm"

    def __init__(self):
        if LGBMRegressor is None:
            raise RuntimeError(f"LightGBM is unavailable: {_IMPORT_ERROR}")
        self.model = LGBMRegressor(n_estimators=200, learning_rate=0.05, random_state=42, verbosity=-1)

    def train(self, X, y):
        self.model.fit(X, y)

    def predict(self, X):
        return self.model.predict(X)

    def save(self, path):
        joblib.dump(self.model, path)

    def load(self, path):
        self.model = joblib.load(path)
