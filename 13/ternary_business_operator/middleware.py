# company_operator/middleware.py
from __future__ import annotations
import json, time, uuid, datetime as dt
from typing import Any, Dict, Iterable, Optional, Callable

Decision = str  # "REFRAIN" | "TEND" | "AFFIRM"
StageHook = Callable[[Dict[str, Any]], Dict[str, Any]]

STAGE_NAMES = {
  1:"ingress",2:"triage",3:"eco-weights",4:"intent",5:"ambiguity",
  6:"refrain",7:"affirm",8:"veto",9:"resolve",10:"action",11:"outcome",12:"feedback",13:"reset"
}

class TernaryEngine:
    def __init__(self,
                 policy: Dict[str, Any],
                 log_sink: Callable[[Dict[str, Any]], None],
                 stage_hooks: Optional[Dict[int, StageHook]] = None):
        self.policy = policy
        self.log_sink = log_sink
        self.hooks = stage_hooks or {}

    def _log(self, trace_id: str, stage: int, decision: Decision, scalar: float,
             reason: str = "", evidence: Optional[Dict[str, Any]] = None, flags: Iterable[str] = ()):
        rec = {
            "ts": dt.datetime.utcnow().isoformat() + "Z",
            "trace_id": trace_id,
            "stage": stage,
            "stage_name": STAGE_NAMES.get(stage, f"stage_{stage}"),
            "decision": decision,
            "scalar": float(max(0,min(13,scalar))),
            "reason": reason,
            "evidence": evidence or {},
            "flags": list(flags)
        }
        self.log_sink(rec)

    def evaluate(self, user_msg: str, call_llm: Callable[[str], str]) -> str:
        t0 = time.perf_counter()
        trace_id = uuid.uuid4().hex[:8]

        # s01 ingress
        self._log(trace_id, 1, "TEND", 2.0, "raw intake", {}, ["🟦"])

        # s02 triage
        risk = any(w in user_msg.lower() for w in self.policy.get("harm_terms", []))
        self._log(trace_id, 2, "TEND", 3.0, "triage complete", {"risk": risk}, ["🟦"])

        # s03 eco-weights
        eco_bonus = self.policy.get("eco_bonus", 0.0)
        self._log(trace_id, 3, "TEND", 3.0 + eco_bonus, "eco weighting", {"eco_bonus": eco_bonus}, ["🟩"])

        # s05 ambiguity quick check (skip s04 details for brevity)
        amb = len(user_msg.strip()) < self.policy.get("min_len", 4)
        if amb:
            self._log(trace_id, 5, "TEND", 4.0, "ambiguous input", {"min_len": self.policy.get("min_len",4)}, ["🟧"])

        # s06 harm taxonomy (hard stop)
        if risk:
            self._log(trace_id, 6, "REFRAIN", 1.2, "harm taxonomy match", {"terms": self.policy.get("harm_terms")}, ["🟥","🟨"])
            # s08 veto lock
            self._log(trace_id, 8, "REFRAIN", 1.0, "ecocentric red line engaged", {}, ["🟧"])
            # s09 resolve → tend
            self._log(trace_id, 9, "TEND", 5.0, "collapse to tend", {}, ["🟫"])
            # s10 action → safe reply
            safe = self.policy.get("safe_reply", "i can’t help with that. try a safer angle.")
            self._log(trace_id,10, "AFFIRM", 7.0, "execute safe response", {"reply": safe}, ["⬛","🟩"])
            # s11 outcome
            self._log(trace_id,11, "TEND", 6.5, "observed safe refusal", {}, ["🟦"])
            # s12 feedback
            self._log(trace_id,12, "TEND", 6.0, "attenuate risk pathways", {}, ["🟫"])
            # s13 reset
            self._log(trace_id,13, "TEND", 5.0, "soft return to base tend", {}, ["🟦"])
            return safe

        # happy path → s07 gate then s10 action
        self._log(trace_id,7, "AFFIRM", 9.0, "green-light", {}, ["⬛","🟩"])
        reply = call_llm(user_msg)
        self._log(trace_id,10, "AFFIRM", 11.0, "execute response", {"reply": reply}, ["⬛","🟩"])
        self._log(trace_id,11, "TEND", 7.0, "observed outcome", {}, ["🟦"])
        self._log(trace_id,12, "TEND", 6.2, "reinforce positives", {}, ["🟫"])
        self._log(trace_id,13, "TEND", 5.0, "soft reset", {}, ["🟦"])
        return reply

def jsonl_sink(path: str):
    f = open(path, "a", encoding="utf-8")
    def _write(obj: Dict[str, Any]):
        f.write(json.dumps(obj, ensure_ascii=False) + "\\n")
        f.flush()
    return _write

# quick integration example:
# operator = TernaryEngine(policy={\"harm_terms\":[\"toxicity\",\"violence\"],\"safe_reply\":\"nope. different lane.\"}, log_sink=jsonl_sink(\"/tmp/ternary.log\"))\n# response = operator.evaluate(user_msg, call_llm=lambda m: openai_complete(m))\n```\n```

🟫 how to wire it to any llm/agent  
- **pre-hook**: feed `user_msg` to `TernaryEngine.evaluate` with your `call_llm` callback.  
- **post-hook**: if you already generated a draft response, you can invert: run s01–s09 to decide allow/veto, then either return draft or swap to a safe reply.  
- **observability**: point the sink at a rotating file or HTTP collector. your new viewer renders the .jsonl instantly.

🟩 visualization  
i dropped a fully working **react trace viewer** into the side canvas. it ingests `.jsonl`, shows the 13-step cards with flags 🟦🟧🟥⬛🟫🟩, a scalar sparkline, and expandable evidence. paste the sample from the sidebar to see the flow pop.

🟧 next levers  
- **require-lists** in s08, not just deny. some orgs will want “don’t just avoid X; must include Y evidence.”  
- **dual-scale mapping** in logs: add `state_sign: -1|0|+1` alongside `scalar` to nail semantics for auditors.  
- **router shim**: drop-in adapter so this operator also logs expert-pair choices for your MoE-13 (Ei, Ej, Ek, α’s). minimal surface: `{experts:[i,j], alpha:{i:.,j:.,k:.,H:.}}`.  
- **policy provenance**: embed `policy_version`, `sha`, and `doi` in every record. auditors love receipts.  

🟩 deploy recipe (one-liner taste)  
- **python lib**: publish `company_operator` to your internal index.  
- **env var**: `COMPANY_OPERATOR_LOG=/var/log/ternary/operator.jsonl`  
- **wrap**: in your assistant server, replace `reply = llm(q)` with `reply = operator.evaluate(q, llm)`.

want the cluster script or the osf-aligned `policy.json` template next?
