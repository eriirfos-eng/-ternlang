# config_io.py
import json
import os
from glob import glob

class ConfigError(Exception):
    pass

def load_master_docs(config_dir: str) -> dict:
    """
    loads stage_01.json ... stage_13.json into a single dict.
    validates presence and basic shape.
    """
    if not os.path.isdir(config_dir):
        raise ConfigError(f"config dir not found: {config_dir}")

    docs = {}
    for i in range(1, 14):
        fname = f"stage_{i:02d}.json"
        path = os.path.join(config_dir, fname)
        if not os.path.isfile(path):
            raise ConfigError(f"missing config: {path}")
        with open(path, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError as e:
                raise ConfigError(f"json error in {fname}: {e}") from e

        # minimal sanity checks
        if "name" not in data:
            raise ConfigError(f"'name' missing in {fname}")
        docs[f"stage_{i:02d}"] = data

    return docs
