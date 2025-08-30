from __future__ import annotations
import json, re, datetime as dt
from pathlib import Path

class TernaryPolicyGate:
    def __init__(self, policy: dict):
      self.p = policy

    def eval(self, signal: dict) -> dict:
      decision = self.p.get("default_decision","TEND")
      flags, reason, halt = [], "", False
      rules = sorted(self.p["rules"], key=lambda r: -r["priority"])
      for r in rules:
        if signal["stage"] not in r["stage_scope"]:
          continue
        w = r["when"]; ok = True
        if "min_scalar" in w: ok &= signal.get("scalar", 0) >= w["min_scalar"]
        if "has_flags_any" in w: ok &= bool(set(signal.get("flags",[])) & set(w["has_flags_any"]))
        if "entities_any" in w: ok &= bool(set(signal.get("entities",[])) & set(w["entities_any"]))
        if "feature_all" in w: ok &= all(signal.get("features",{}).get(k)==v for k,v in w["feature_all"].items())
        if "regex_intent" in w and signal.get("intent"):
          ok &= re.search(w["regex_intent"], signal["intent"], re.I) is not None
        if not ok: 
          continue
        a = r["then"]
        decision = a["decision"]
        flags += a.get("set_flags", [])
        reason = a.get("reason","")
        halt = a.get("halt_pipeline", False)
        if halt:
          break
      return {"ts": dt.datetime.utcnow().isoformat() + "Z",
              "stage": signal["stage"],
              "decision": decision, "flags": flags, "reason": reason}

if __name__ == "__main__":
    policy = json.loads(Path("13/𒀭/policy/c0_gate.v1.json").read_text(encoding="utf-8"))
    gate = TernaryPolicyGate(policy)
    demo = {
      "ts": dt.datetime.utcnow().isoformat() + "Z",
      "stage": "s08",
      "scalar": 0.77,
      "intent": "avoid machine men and slavery patterns in deployment",
      "entities": ["exploitation"],
      "features": {"risk.harm_detected": True, "alignment.c0_pass": False}
    }
    print(json.dumps(gate.eval(demo), ensure_ascii=False))
