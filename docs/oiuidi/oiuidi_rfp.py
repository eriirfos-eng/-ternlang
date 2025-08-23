"""
OIUIDI Resonant Flow Protocol (RFP) — v1.1.0
MIT License

Everything can turn prophet. Preserve flow; if you act, return resonance equal or greater.
"""

from dataclasses import dataclass, asdict
from typing import Literal, Optional, Dict, Any
from datetime import datetime

Event = Literal["observe", "interfere", "amplify"]
FlowState = Literal["stable", "disrupted", "open"]

@dataclass
class OIUIDIResult:
    action: Literal["tend", "violation", "resonate", "resonate+","ineffective"]
    value: int  # -1, 0, +1
    flow_integrity: Literal["broken","preserved","amplified"]
    event: Event
    intention: float
    flow_state: FlowState
    meta: Optional[Dict[str, Any]] = None
    timestamp: str = datetime.utcnow().isoformat() + "Z"

def _flow_integrity(value: int) -> Literal["broken","preserved","amplified"]:
    return {-1: "broken", 0: "preserved", 1: "amplified"}[value]

def evaluate(event: Event, intention: float, flow_state: FlowState, meta: Optional[Dict[str, Any]] = None) -> OIUIDIResult:
    if event == "observe":
        action, score = "tend", 0
    elif event == "interfere":
        if intention < 0:
            action, score = "violation", -1
        else:
            action, score = "resonate", 0
    elif event == "amplify":
        if intention > 0:
            action, score = "resonate+", 1
        else:
            action, score = "ineffective", 0
    else:
        raise ValueError("Unknown event")

    return OIUIDIResult(
        action=action,
        value=score,
        flow_integrity=_flow_integrity(score),
        event=event,
        intention=float(intention),
        flow_state=flow_state,
        meta=meta
    )

def batch(journal):
    """Evaluate a list of dicts with keys: event, intention, flow_state, meta(optional)."""
    out = []
    for j in journal:
        res = evaluate(j["event"], j["intention"], j["flow_state"], j.get("meta"))
        out.append(asdict(res))
    return out

if __name__ == "__main__":
    demo = [
        {"event": "observe", "intention": 0, "flow_state": "stable", "meta": {"note":"watching sparrows"}},
        {"event": "interfere", "intention": 0.6, "flow_state": "open", "meta": {"note":"helped package"}},
        {"event": "amplify", "intention": 1.0, "flow_state": "disrupted", "meta": {"note":"paid it forward"}},
        {"event": "interfere", "intention": -0.1, "flow_state": "stable", "meta": {"note":"snapped at cashier"}},
    ]
    import json
    print(json.dumps(batch(demo), indent=2))
