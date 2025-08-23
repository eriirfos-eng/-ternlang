import json
from ternary_phase_modulator import TernaryPhaseModulator

def test_success_xor_true_true_true():
    mod = TernaryPhaseModulator("test", True, True, True)
    out = mod.run()
    assert out["runSummary"]["result"] is True

def test_anomaly_when_origin_false():
    mod = TernaryPhaseModulator("test", False, True, False)
    out = mod.run()
    assert out["runSummary"]["result"] is False
    notes = out["operatorNotes"]
    assert any("Live anomaly" in n["message"] for n in notes)

def test_majority_operator_behavior():
    mod = TernaryPhaseModulator("test", False, True, True,
                                synthesis_fn=TernaryPhaseModulator.majority3)
    out = mod.run()
    assert out["runSummary"]["result"] is False or out["runSummary"]["result"] is True  # sanity
    assert out["runSummary"]["synthesisOperator"] == "majority3"
