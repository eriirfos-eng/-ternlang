# config_io.py
import json
import os
from glob import glob

class ConfigError(Exception):
    pass

try:
    from jsonschema import validate
    from jsonschema.exceptions import ValidationError
    _HAS_JSONSCHEMA = True
except Exception:
    _HAS_JSONSCHEMA = False
    ValidationError = Exception  # fallback type alias


def _load_json(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def _validate(stage_key: str, doc: dict, schema_root: dict):
    if not _HAS_JSONSCHEMA:
        # soft warning: validator not installed, skip strict check
        return
    try:
        stage_schema = schema_root["stages"][stage_key]
    except KeyError:
        raise ConfigError(f"schema missing for {stage_key}")
    try:
        validate(instance=doc, schema=stage_schema)
    except ValidationError as e:
        loc = " → ".join(str(p) for p in e.path) if getattr(e, "path", None) else ""
        msg = f"{stage_key} invalid: {e.message}"
        if loc:
            msg += f" at {loc}"
        raise ConfigError(msg) from e

def load_master_docs(config_dir: str) -> dict:
    """
    loads stage_01.json ... stage_13.json and validates each against schema.json.
    returns a dict keyed by 'stage_XX'.
    """
    if not os.path.isdir(config_dir):
        raise ConfigError(f"config dir not found: {config_dir}")

    # schema path
    schema_path = os.path.join(config_dir, "schema.json")
    if not os.path.isfile(schema_path):
        raise ConfigError(f"schema.json not found in {config_dir}")
    schema_root = _load_json(schema_path)

    docs = {}
    for i in range(1, 14):
        stage_key = f"stage_{i:02d}"
        fname = f"{stage_key}.json"
        path = os.path.join(config_dir, fname)
        if not os.path.isfile(path):
            raise ConfigError(f"missing config: {path}")
        doc = _load_json(path)

        # quick top-level sanity
        if "name" not in doc:
            raise ConfigError(f"'name' missing in {fname}")

        # jsonschema validation
        _validate(stage_key, doc, schema_root)

        docs[stage_key] = doc

    return docs
