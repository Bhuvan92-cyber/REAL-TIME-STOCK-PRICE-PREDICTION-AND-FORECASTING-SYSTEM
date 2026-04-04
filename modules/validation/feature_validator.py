import pandas as pd


class FeatureValidator:
    """
    Validates presence of required ML features.
    """

    def __init__(self, required_features=None):

        if required_features is None:

            required_features = [
                "SMA_20",
                "EMA_20",
                "RSI",
                "MACD",
                "Bollinger_Upper",
                "Bollinger_Lower"
            ]

        self.required_features = required_features

    def validate_features(self, df: pd.DataFrame):

        missing = [
            feature
            for feature in self.required_features
            if feature not in df.columns
        ]

        if missing:
            raise ValueError(
                f"Missing engineered features: {missing}"
            )

        return True