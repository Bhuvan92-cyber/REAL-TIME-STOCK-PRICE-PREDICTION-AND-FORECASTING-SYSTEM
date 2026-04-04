import pandas as pd


class SchemaValidator:
    """
    Validates dataset schema before pipeline execution.
    """

    def __init__(self, required_columns=None):

        if required_columns is None:
            required_columns = [
                "date",
                "open",
                "high",
                "low",
                "close",
                "volume"
            ]

        self.required_columns = required_columns

    def validate_columns(self, df: pd.DataFrame):

        missing_columns = [
            col for col in self.required_columns if col not in df.columns
        ]

        if missing_columns:
            raise ValueError(
                f"Missing required columns: {missing_columns}"
            )

        return True

    def validate_types(self, df: pd.DataFrame):

        numeric_columns = ["open", "high", "low", "close", "volume"]

        for col in numeric_columns:
            if not pd.api.types.is_numeric_dtype(df[col]):
                raise TypeError(
                    f"Column {col} must be numeric"
                )

        return True

    def validate_datetime(self, df: pd.DataFrame):

        try:
            pd.to_datetime(df["date"])
        except Exception:
            raise ValueError("Invalid datetime format in 'date' column")

        return True

    def validate(self, df: pd.DataFrame):

        self.validate_columns(df)
        self.validate_types(df)
        self.validate_datetime(df)

        return True