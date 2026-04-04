import numpy as np
import pandas as pd


class DataDriftDetector:
    """
    Detects data drift using Population Stability Index (PSI).
    """

    def __init__(self, bins=10):
        self.bins = bins

    def calculate_psi(self, expected, actual):

        breakpoints = np.linspace(0, 100, self.bins + 1)

        expected_perc = np.percentile(expected, breakpoints)
        actual_perc = np.percentile(actual, breakpoints)

        psi_value = 0

        for i in range(len(expected_perc) - 1):

            expected_count = ((expected >= expected_perc[i]) &
                              (expected < expected_perc[i + 1])).sum()

            actual_count = ((actual >= actual_perc[i]) &
                            (actual < actual_perc[i + 1])).sum()

            expected_ratio = expected_count / len(expected)
            actual_ratio = actual_count / len(actual)

            if actual_ratio == 0:
                actual_ratio = 0.0001

            psi_value += (
                (expected_ratio - actual_ratio)
                * np.log(expected_ratio / actual_ratio)
            )

        return psi_value

    def detect_drift(self, train_df: pd.DataFrame, new_df: pd.DataFrame):

        drift_report = {}

        common_columns = train_df.columns.intersection(new_df.columns)

        for col in common_columns:

            if pd.api.types.is_numeric_dtype(train_df[col]):

                psi = self.calculate_psi(
                    train_df[col].dropna(),
                    new_df[col].dropna()
                )

                drift_report[col] = psi

        return drift_report