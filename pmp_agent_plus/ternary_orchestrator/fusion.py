from typing import Dict, Any, List
from .core import Orchestrator, DetectorOutput, FailsafeConfig, FusionWeights, AFFIRM, TEND, REFRAIN

# sample stub detectors to prove plumbing; swap with real models later
def stub_toxicity(text: str) -> DetectorOutput:
    # naive heuristic: presence of certain tokens bumps score
    toks = text.lower()
    s = 0.0
    for bad in ["suck", "trash", "vermin"]:
        if bad in toks:
            s = max(s, 0.7)
    return DetectorOutput(scores={"HATE_SPEECH": s}, meta={"model": "toxicity-stub"})

def stub_self_harm(text: str) -> DetectorOutput:
    toks = text.lower()
    s = 0.0
    if "kill myself" in toks or "drink bleach" in toks:
        s = 0.95 if "kill myself" in toks else 0.62
    return DetectorOutput(scores={"SELF_HARM": s}, meta={"model": "selfharm-stub"})

def stub_illegal(text: str) -> DetectorOutput:
    toks = text.lower()
    s = 0.0
    if "skim credit cards" in toks or "molotov" in toks:
        s = 0.93
    return DetectorOutput(scores={"ILLEGAL_FACILITATION": s}, meta={"model": "illegal-stub"})

def run(text: str) -> Dict[str, Any]:
    orch = Orchestrator()
    outs = [stub_toxicity(text), stub_self_harm(text), stub_illegal(text)]
    fused = orch.fuse(outs)
    return fused.model_dump()  # dict
