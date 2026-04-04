import time
import pandas as pd
import joblib
import torch
import sys

from modules.ingestion.realtime_stream import RealTimeStreamer
from modules.prediction.signal_generator import generate_signal
from modules.utils.helpers import save_dataframe
from modules.utils.logger import get_logger

from modules.models.deep_learning.cnn_lstm_model import CNNLSTMModel


logger = get_logger(__name__)

# Supported stocks
SUPPORTED_STOCKS = ["AAPL", "TCS", "NIFTY50"]
DEFAULT_STOCK = "AAPL"
LOOKBACK = 60  # must match training

def run_predictions(symbol="AAPL"):
    """
    Run real-time predictions for a specific stock.
    """
    logger.info(f"Starting real-time prediction engine for {symbol}")
    
    # -------------------------
    # MODEL PATHS
    # -------------------------
    RF_MODEL_PATH = f"models_saved/{symbol}_random_forest.pkl"
    CNN_LSTM_MODEL_PATH = f"models_saved/{symbol}_cnn_lstm_model.pt"
    LSTM_SCALER_PATH = f"models_saved/{symbol}_lstm_scaler.pkl"
    DATA_PATH = f"data/processed/{symbol}_feature_engineered.csv"
    LIVE_DATA_PATH = f"data/raw/realtime/{symbol}_live_stream.csv"
    LATEST_PRED_PATH = f"data/processed/{symbol}_latest_predictions.csv"
    
    # -------------------------
    # CHECK IF MODELS EXIST
    # -------------------------
    import os
    if not os.path.exists(RF_MODEL_PATH):
        logger.error(f"Random Forest model not found: {RF_MODEL_PATH}")
        logger.error("Please run: python scripts/train_model.py")
        return
    
    if not os.path.exists(CNN_LSTM_MODEL_PATH):
        logger.error(f"CNN-LSTM model not found: {CNN_LSTM_MODEL_PATH}")
        logger.error("Please run: python scripts/train_model.py")
        return
    
    # -------------------------
    # LOAD MODELS
    # -------------------------
    try:
        rf_model = joblib.load(RF_MODEL_PATH)
        logger.info(f"✅ Loaded Random Forest model for {symbol}")
    except Exception as e:
        logger.error(f"Failed to load Random Forest model: {e}")
        return
    
    try:
        cnn_lstm = CNNLSTMModel()
        cnn_lstm.load_state_dict(
            torch.load(CNN_LSTM_MODEL_PATH, map_location="cpu")
        )
        cnn_lstm.eval()
        logger.info(f"✅ Loaded CNN-LSTM model for {symbol}")
    except Exception as e:
        logger.error(f"Failed to load CNN-LSTM model: {e}")
        return
    
    try:
        lstm_scaler = joblib.load(LSTM_SCALER_PATH)
        logger.info(f"✅ Loaded LSTM scaler for {symbol}")
    except Exception as e:
        logger.error(f"Failed to load LSTM scaler: {e}")
        return
    
    # -------------------------
    # LOAD HISTORICAL DATA
    # -------------------------
    try:
        df = pd.read_csv(DATA_PATH)
        logger.info(f"✅ Loaded feature-engineered data: {df.shape}")
    except Exception as e:
        logger.error(f"Failed to load data: {e}")
        return
    
    # -------------------------
    # START REAL-TIME INFERENCE
    # -------------------------
    logger.info(f"Starting real-time inference for {symbol}...\n")
    
    try:
        iteration = 0
        while True:
            iteration += 1
            
            logger.info(f"--- Iteration {iteration} ---")
            
            # =============================
            # 1️⃣ RANDOM FOREST PREDICTION
            # =============================
            try:
                latest_row = df.drop(columns=["close"], errors="ignore").iloc[-1:]
                latest_row = latest_row.select_dtypes(include=["int64", "float64"])
                current_price = df["close"].iloc[-1]
                rf_pred = rf_model.predict(latest_row.values.reshape(1, -1))[0]
                logger.info(f"Random Forest prediction: {rf_pred:.4f}")
            except Exception as e:
                logger.error(f"Random Forest prediction failed: {e}")
                rf_pred = current_price
            
            # =============================
            # 2️⃣ CNN-LSTM PREDICTION
            # =============================
            try:
                if len(df["close"]) >= LOOKBACK:
                    last_prices = df["close"].values[-LOOKBACK:].reshape(-1, 1)
                    scaled = lstm_scaler.transform(last_prices)
                    X_lstm = torch.tensor(
                        scaled.reshape(1, LOOKBACK, 1),
                        dtype=torch.float32
                    )
                    with torch.no_grad():
                        cnn_pred_scaled = cnn_lstm(X_lstm).item()
                    cnn_pred = lstm_scaler.inverse_transform(
                        [[cnn_pred_scaled]]
                    )[0][0]
                    logger.info(f"CNN-LSTM prediction: {cnn_pred:.4f}")
                else:
                    cnn_pred = current_price
                    logger.warning("Insufficient data for CNN-LSTM")
            except Exception as e:
                logger.error(f"CNN-LSTM prediction failed: {e}")
                cnn_pred = current_price
            
            # =============================
            # 3️⃣ ENSEMBLE PREDICTION
            # =============================
            final_prediction = (rf_pred + cnn_pred) / 2
            
            # =============================
            # 4️⃣ GENERATE SIGNAL
            # =============================
            signal = generate_signal(
                current_price=current_price,
                predicted_price=final_prediction
            )
            
            logger.info(f"📊 SIGNAL: {signal['signal']} | Confidence: {signal['confidence (%)']:.2f}%")
            logger.info(f"Current: {current_price:.2f} → Predicted: {final_prediction:.2f}\n")
            
            # =============================
            # 5️⃣ SAVE PREDICTIONS
            # =============================
            try:
                live_df = pd.DataFrame([signal])
                save_dataframe(live_df, LIVE_DATA_PATH)
            except Exception as e:
                logger.warning(f"Failed to save live data: {e}")
            
            # Wait before next prediction
            time.sleep(30)
    
    except KeyboardInterrupt:
        logger.info(f"✋ Real-time engine stopped for {symbol}")


def main():
    """
    Main entry point.
    """
    # Check if specific stock provided
    stock = DEFAULT_STOCK
    if len(sys.argv) > 1:
        stock = sys.argv[1].upper()
        if stock not in SUPPORTED_STOCKS:
            logger.error(f"Unsupported stock: {stock}")
            logger.info(f"Supported stocks: {', '.join(SUPPORTED_STOCKS)}")
            return
    
    logger.info(f"Supported stocks: {', '.join(SUPPORTED_STOCKS)}")
    logger.info(f"Running real-time predictions for: {stock}")
    logger.info("="*60)
    
    run_predictions(stock)


if __name__ == "__main__":
    main()
