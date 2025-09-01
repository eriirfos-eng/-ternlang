import json, pathlib
from jsonschema import validate

BASE = pathlib.Path(__file__).resolve().parents[1]

def _load(p):
    return json.loads((BASE / p).read_text(encoding="utf-8"))

def test_decision_log_schema_ok():
    schema = _load("pmp_agent/schemas/decision_log.schema.json")
    example = _load("examples/decision_log_example.json")
    validate(example, schema)

def test_state_snapshot_schema_ok():
    schema = _load("pmp_agent/schemas/state_snapshot.schema.json")
    example = _load("examples/state_snapshot_example.json")
    validate(example, schema)

def test_matrix_schema_ok():
    schema = _load("pmp_agent/schemas/test_matrix.schema.json")
    example = _load("examples/matrix.json")
    validate(example, schema)
