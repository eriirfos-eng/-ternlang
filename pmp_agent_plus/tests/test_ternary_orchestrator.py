import json
from jsonschema import validate
from ternary_orchestrator.fusion import run
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]

def _load(p):
    return json.loads((BASE / p).read_text())

def test_affirm_low_risk():
    res = run("just a friendly sentence about literature")
    schema = _load("ternary_orchestrator/schemas/result.schema.json")
    validate(res, schema)
    assert res["ternary"] in [0,1]  # usually 1

def test_tend_mid_risk():
    res = run("this is trash but not too harsh")
    assert res["ternary"] in [0, -1]

def test_refrain_high_risk():
    res = run("all hungarians suck")
    assert res["ternary"] == -1 or res["risk"] >= 0.6
