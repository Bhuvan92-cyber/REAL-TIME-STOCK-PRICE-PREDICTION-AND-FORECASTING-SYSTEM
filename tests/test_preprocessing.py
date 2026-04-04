import pandas as pd
import numpy as np
from modules.preprocessing.data_cleaner import clean_data
from modules.preprocessing.missing_value_handler import handle_missing_values
from modules.preprocessing.normalizer import normalize_data

def test_preprocessing_pipeline():
    df = pd.DataFrame({
        "date": pd.date_range(start="2023-01-01", periods=5),
        "close": [100, np.nan, 102, 103, np.nan],
        "volume": [1000, 1100, 1050, np.nan, 1200]
    })

    df = clean_data(df)
    df = handle_missing_values(df)
    df = normalize_data(df, save_scaler=False)

    assert df.isnull().sum().sum() == 0
    assert df["close"].max() <= 1.0
    assert df["close"].min() >= 0.0
