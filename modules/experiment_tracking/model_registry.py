import os
import joblib


class ModelRegistry:
    """
    Stores and versions trained models.
    """

    def __init__(self, registry_dir="models_saved"):
        self.registry_dir = registry_dir
        os.makedirs(self.registry_dir, exist_ok=True)

    def _get_next_version(self, model_name):

        existing = [
            f for f in os.listdir(self.registry_dir)
            if f.startswith(model_name)
        ]

        version = len(existing) + 1
        return version

    def save_model(self, model, model_name):

        version = self._get_next_version(model_name)

        filename = f"{model_name}_v{version}.pkl"
        filepath = os.path.join(self.registry_dir, filename)

        joblib.dump(model, filepath)

        return filepath

    def load_model(self, model_path):

        return joblib.load(model_path)