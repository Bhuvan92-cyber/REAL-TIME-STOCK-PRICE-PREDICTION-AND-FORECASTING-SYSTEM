import torch
import torch.nn as nn
import torch.optim as optim


class CNNLSTMModel(nn.Module):
    """
    CNN-LSTM model implemented in PyTorch
    Compatible with Python 3.10+
    """

    def __init__(self, input_channels=1, hidden_size=64):
        super(CNNLSTMModel, self).__init__()

        # CNN feature extractor
        self.conv1 = nn.Conv1d(
            in_channels=input_channels,
            out_channels=64,
            kernel_size=3
        )
        self.pool = nn.MaxPool1d(kernel_size=2)

        # LSTM
        self.lstm = nn.LSTM(
            input_size=64,
            hidden_size=hidden_size,
            batch_first=True
        )

        # Output layer
        self.fc = nn.Linear(hidden_size, 1)

    def forward(self, x):
        # x shape: (batch, seq_len, features)
        x = x.permute(0, 2, 1)  # → (batch, features, seq_len)
        x = torch.relu(self.conv1(x))
        x = self.pool(x)

        x = x.permute(0, 2, 1)  # → (batch, seq_len, features)
        lstm_out, _ = self.lstm(x)

        out = self.fc(lstm_out[:, -1, :])
        return out
