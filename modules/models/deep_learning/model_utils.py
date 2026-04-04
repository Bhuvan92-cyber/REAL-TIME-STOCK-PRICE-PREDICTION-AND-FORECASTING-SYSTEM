import numpy as np
from sklearn.preprocessing import MinMaxScaler

def prepare_lstm_data(df, target_col="close", lookback=60):
    """
    Convert dataframe into LSTM-ready sequences
    """
    scaler = MinMaxScaler()
    scaled_data = scaler.fit_transform(df[[target_col]])

    X, y = [], []
    for i in range(lookback, len(scaled_data)):
        X.append(scaled_data[i - lookback:i, 0])
        y.append(scaled_data[i, 0])

    X = np.array(X)
    y = np.array(y)

    X = X.reshape((X.shape[0], X.shape[1], 1))
    return X, y, scaler
