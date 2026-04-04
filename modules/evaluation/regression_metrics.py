import numpy as np
from sklearn.metrics import (
    mean_squared_error,
    mean_absolute_error,
    r2_score
)
from modules.utils.logger import get_logger

logger = get_logger(__name__)

def regression_evaluation(y_true, y_pred):
    """
    Enhanced evaluation metrics for stock prediction
    """

    y_true = np.array(y_true)
    y_pred = np.array(y_pred)

    # Basic regression metrics
    mae = mean_absolute_error(y_true, y_pred)
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    r2 = r2_score(y_true, y_pred)

    # Directional accuracy
    actual_direction = np.sign(np.diff(y_true))
    predicted_direction = np.sign(np.diff(y_pred))

    directional_accuracy = np.mean(
        actual_direction == predicted_direction
    )

    return {
        "MAE": round(mae, 4),
        "RMSE": round(rmse, 4),
        "R2 Score": round(r2, 4),
        "Directional Accuracy": round(directional_accuracy * 100, 2)
    }