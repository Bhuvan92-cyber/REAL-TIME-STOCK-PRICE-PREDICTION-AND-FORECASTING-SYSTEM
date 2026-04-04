import yaml
import os

def load_config(path: str = "config.yaml"):
    """
    Loads YAML configuration file.
    """

    if not os.path.exists(path):
        raise FileNotFoundError(f"Config file not found: {path}")

    with open(path, "r") as file:
        config = yaml.safe_load(file)

    return config
