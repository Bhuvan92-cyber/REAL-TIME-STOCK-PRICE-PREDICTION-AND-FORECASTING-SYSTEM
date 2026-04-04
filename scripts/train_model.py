import pandas as pd
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
import joblib

from modules.models.regression.random_forest import RandomForestModel
from modules.training.trainer import train_regression_model
from modules.evaluation.regression_metrics import regression_evaluation
from modules.utils.logger import get_logger
from modules.utils.config_loader import load_config

from modules.models.deep_learning.cnn_lstm_model import CNNLSTMModel
from modules.models.deep_learning.model_utils import prepare_lstm_data


logger = get_logger(__name__)


# ---------------------------------------------------------
# CNN-LSTM TRAINING FUNCTION (PyTorch)
# ---------------------------------------------------------
def train_cnn_lstm(X, y, epochs=10, lr=0.001):
    """
    Train CNN-LSTM model using PyTorch
    """
    device = torch.device("cpu")

    X = torch.tensor(X, dtype=torch.float32).to(device)
    y = torch.tensor(y, dtype=torch.float32).to(device)

    model = CNNLSTMModel()
    model.to(device)

    criterion = nn.MSELoss()
    optimizer = optim.Adam(model.parameters(), lr=lr)

    logger.info("Starting CNN-LSTM training")

    for epoch in range(epochs):
        model.train()
        optimizer.zero_grad()

        outputs = model(X).squeeze()
        loss = criterion(outputs, y)

        loss.backward()
        optimizer.step()

        logger.info(
            f"CNN-LSTM Epoch [{epoch + 1}/{epochs}] - Loss: {loss.item():.6f}"
        )

    torch.save(model.state_dict(), "models_saved/cnn_lstm_model.pt")
    logger.info("CNN-LSTM model saved at models_saved/cnn_lstm_model.pt")

    return model


# ---------------------------------------------------------
# MAIN TRAINING PIPELINE
# ---------------------------------------------------------
def main():
    logger.info("Starting model training pipeline")

    # Train models for all 3 stocks
    config = load_config()
    stocks = [stock['symbol'] for stock in config['supported_stocks']]
    
    for symbol in stocks:
        logger.info(f"\n{'='*60}")
        logger.info(f"Training models for {symbol}")
        logger.info(f"{'='*60}\n")
        
        try:
            # -------------------------
            # Load processed dataset
            # -------------------------
            data_path = f"data/processed/{symbol}_feature_engineered.csv"
            df = pd.read_csv(data_path)
            
            logger.info(f"Loaded data shape: {df.shape}")

            # =========================
            # 1️⃣ RANDOM FOREST TRAINING
            # =========================
            rf_model = RandomForestModel()
            preds, y_test = train_regression_model(rf_model, df)
            rf_model.save(path=f"models_saved/{symbol}_random_forest.pkl")

            metrics = regression_evaluation(y_test, preds)
            logger.info(f"Random Forest Metrics for {symbol}: {metrics}")

            # Save evaluation results
            eval_df = pd.DataFrame({
                "y_test": y_test.values,
                "y_pred": preds
            })
            eval_df.to_csv(f"data/processed/{symbol}_train_test_split.csv", index=False)

            logger.info("Random Forest training completed")

            # =========================
            # 2️⃣ CNN-LSTM TRAINING
            # =========================
            # Use ONLY close price for sequence learning
            X_lstm, y_lstm, lstm_scaler = prepare_lstm_data(df[["close"]])

            logger.info(f"LSTM data prepared: X shape {X_lstm.shape}, y shape {y_lstm.shape}")
            
            train_cnn_lstm(X_lstm, y_lstm, epochs=10, lr=0.001)

            # Save model with symbol name
            import torch
            model = CNNLSTMModel()
            model.load_state_dict(torch.load("models_saved/cnn_lstm_model.pt", map_location="cpu"))
            torch.save(model.state_dict(), f"models_saved/{symbol}_cnn_lstm_model.pt")

            # Save scaler for realtime inference
            joblib.dump(lstm_scaler, f"models_saved/{symbol}_lstm_scaler.pkl")
            logger.info(f"LSTM scaler saved at models_saved/{symbol}_lstm_scaler.pkl")
            
            logger.info(f"Model training completed for {symbol}")
            
        except Exception as e:
            logger.error(f"Error training models for {symbol}: {str(e)}")
            continue

    logger.info("\n" + "="*60)
    logger.info("Model training pipeline completed for all stocks")
    logger.info("="*60)


# ---------------------------------------------------------
# ENTRY POINT
# ---------------------------------------------------------
if __name__ == "__main__":
    main()
