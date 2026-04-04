import pandas as pd
from sklearn.preprocessing import MinMaxScaler
import joblib
from modules.utils.logger import get_logger

logger = get_logger(__name__)

def normalize_data(
    df: pd.DataFrame,
    save_scaler: bool = True,
    scaler_path: str = "models_saved/scaler.pkl"
) -> pd.DataFrame:
    """
    Normalizes numerical columns using MinMaxScaler.
    """

    logger.info("Starting data normalization")

    df = df.copy()
    scaler = MinMaxScaler()

    numeric_cols = df.select_dtypes(include=["float64", "int64"]).columns

    df[numeric_cols] = scaler.fit_transform(df[numeric_cols])

    if save_scaler:
        joblib.dump(scaler, scaler_path)
        logger.info(f"Scaler saved at {scaler_path}")

    logger.info("Data normalization completed")
    return df
