import json
from pathlib import Path


def load_config(config_path="config/main_config.json"):
    path = Path(config_path)
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)
