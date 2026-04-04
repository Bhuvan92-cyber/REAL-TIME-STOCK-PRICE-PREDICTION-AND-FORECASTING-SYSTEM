import os
import json
from datetime import datetime


class ExperimentLogger:
    """
    Logs ML experiment metadata such as parameters and metrics.
    """

    def __init__(self, log_dir="logs/experiments"):
        self.log_dir = log_dir
        os.makedirs(self.log_dir, exist_ok=True)

    def log_experiment(self, model_name, parameters, metrics):

        experiment = {
            "model_name": model_name,
            "parameters": parameters,
            "metrics": metrics,
            "timestamp": datetime.utcnow().isoformat()
        }

        filename = f"{model_name}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = os.path.join(self.log_dir, filename)

        with open(filepath, "w") as f:
            json.dump(experiment, f, indent=4)

        return filepath