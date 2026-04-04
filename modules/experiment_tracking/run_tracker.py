import os
import json
import uuid
from datetime import datetime


class RunTracker:
    """
    Tracks ML training runs.
    """

    def __init__(self, log_file="logs/runs/run_history.json"):

        self.log_file = log_file
        os.makedirs(os.path.dirname(self.log_file), exist_ok=True)

        if not os.path.exists(self.log_file):
            with open(self.log_file, "w") as f:
                json.dump([], f)

    def start_run(self, model_name, dataset):

        run_id = str(uuid.uuid4())

        run_data = {
            "run_id": run_id,
            "model_name": model_name,
            "dataset": dataset,
            "start_time": datetime.utcnow().isoformat(),
            "end_time": None,
            "status": "RUNNING"
        }

        self._append_run(run_data)

        return run_id

    def end_run(self, run_id, status="COMPLETED"):

        with open(self.log_file, "r") as f:
            runs = json.load(f)

        for run in runs:
            if run["run_id"] == run_id:
                run["end_time"] = datetime.utcnow().isoformat()
                run["status"] = status

        with open(self.log_file, "w") as f:
            json.dump(runs, f, indent=4)

    def _append_run(self, run_data):

        with open(self.log_file, "r") as f:
            runs = json.load(f)

        runs.append(run_data)

        with open(self.log_file, "w") as f:
            json.dump(runs, f, indent=4)