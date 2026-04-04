import pandas as pd
from modules.utils.logger import get_logger

logger = get_logger(__name__)

def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Cleans raw stock market data.
    - Drops duplicates
    - Standardizes column names
    - Converts date column
    - Sorts by date
    """

    logger.info("Starting data cleaning process")

    df = df.copy()

    # Standardize column names
    df.columns = [col.lower().strip() for col in df.columns]

    # Remove duplicate rows
    df.drop_duplicates(inplace=True)

    # Convert date column if present
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"])
        df.sort_values("date", inplace=True)

    logger.info("Data cleaning completed")
    return df.reset_index(drop=True)
