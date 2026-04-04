import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np

from modules.utils.logger import get_logger

logger = get_logger(__name__)


class LSTMModel(nn.Module):
    """
    PyTorch-based LSTM model for time-series prediction.
    Compatible with Python 3.10+
    """

    def __init__(
        self,
        input_size: int = 1,
        hidden_size: int = 64,
        num_layers: int = 2,
        dropout: float = 0.2
    ):
        super(LSTMModel, self).__init__()

        self.hidden_size = hidden_size
        self.num_layers = num_layers

        self.lstm = nn.LSTM(
            input_size=input_size,
            hidden_size=hidden_size,
            num_layers=num_layers,
            batch_first=True,
            dropout=dropout
        )

        self.fc = nn.Linear(hidden_size, 1)

    def forward(self, x):
        """
        Forward pass
        x shape: (batch_size, seq_length, input_size)
        """
        lstm_out, _ = self.lstm(x)
        out = self.fc(lstm_out[:, -1, :])
        return out

    def train_model(
        self,
        X: np.ndarray,
        y: np.ndarray,
        epochs: int = 10,
        lr: float = 0.001
    ):
        """
        Train LSTM model
        """
        device = torch.device("cpu")
        self.to(device)

        X_tensor = torch.tensor(X, dtype=torch.float32).to(device)
        y_tensor = torch.tensor(y, dtype=torch.float32).to(device)

        criterion = nn.MSELoss()
        optimizer = optim.Adam(self.parameters(), lr=lr)

        logger.info("Starting PyTorch LSTM training")

        for epoch in range(epochs):
            self.train()
            optimizer.zero_grad()

            outputs = self(X_tensor).squeeze()
            loss = criterion(outputs, y_tensor)

            loss.backward()
            optimizer.step()

            logger.info(
                f"LSTM Epoch [{epoch + 1}/{epochs}] - Loss: {loss.item():.6f}"
            )

    def predict(self, X: np.ndarray) -> float:
        """
        Predict next value
        """
        self.eval()
        with torch.no_grad():
            X_tensor = torch.tensor(X, dtype=torch.float32)
            prediction = self(X_tensor).item()
        return prediction

    def save(self, path: str = "models_saved/lstm_model.pt"):
        """
        Save PyTorch model
        """
        torch.save(self.state_dict(), path)
        logger.info(f"LSTM model saved at {path}")

    def load(self, path: str = "models_saved/lstm_model.pt"):
        """
        Load PyTorch model
        """
        self.load_state_dict(
            torch.load(path, map_location="cpu")
        )
        self.eval()
        logger.info(f"LSTM model loaded from {path}")
