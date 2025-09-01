from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Dict, Any
from datetime import datetime, timedelta, timezone
from .config import THRESHOLDS, COOLDOWN_MINUTES_DEFAULT, LOCK_MINUTES_DEFAULT, HISTORY_WINDOW_DEFAULT

def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()

@dataclass
class Reason:
    code: str
    score: float
    snippet: str
    policy_ref: Dict[str, Any] | None = None

@dataclass
class Snapshot:
    conversation_id: str
    state: str = "NORMAL"
    entered_at: str = field(default_factory=now_iso)
    cooldown_until: str | None = None
    strikes: int = 0
    reasons: List[Reason] = field(default_factory=list)
    user_ack: bool = False
    direction: str = "user"  # or "ai"
    history_window: int = HISTORY_WINDOW_DEFAULT

class PolicyStateMachine:
    def __init__(self, conversation_id: str):
        self.snap = Snapshot(conversation_id=conversation_id)
        self.log: List[Dict[str, Any]] = []

    def _set_state(self, new_state: str, reasons: List[Reason]):
        old = self.snap.state
        self.snap.state = new_state
        self.snap.entered_at = now_iso()
        self.snap.reasons = reasons
        self.log.append({
            "timestamp": now_iso(),
            "conversation_id": self.snap.conversation_id,
            "old_state": old,
            "new_state": new_state,
            "reason_codes": [r.code for r in reasons],
            "snippet": reasons[0].snippet if reasons else "",
        })

    def _cooldown_for(self, minutes: int):
        until = datetime.now(timezone.utc) + timedelta(minutes=minutes)
        self.snap.cooldown_until = until.replace(microsecond=0).isoformat()

    def can_post(self) -> bool:
        if self.snap.state in ("COOLDOWN", "LOCKED"):
            if self.snap.cooldown_until and datetime.now(timezone.utc) < datetime.fromisoformat(self.snap.cooldown_until):
                return False
        if self.snap.state == "TERMINATED":
            return False
        return True

    def process(self, scores: Dict[str, float], snippet: str) -> str:
        # Short-circuits
        if scores.get("SELF_HARM", 0) >= THRESHOLDS["SELF_HARM"]:
            self._set_state("LOCKED", [Reason("SELF_HARM", scores["SELF_HARM"], snippet)])
            self._cooldown_for(30)
            self.snap.strikes += 1
            return "LOCK"

        if scores.get("ILLEGAL_FACILITATION", 0) >= THRESHOLDS["ILLEGAL_FACILITATION"] and scores["ILLEGAL_FACILITATION"] >= 0.90:
            self._set_state("TERMINATED", [Reason("ILLEGAL_FACILITATION", scores["ILLEGAL_FACILITATION"], snippet)])
            self.snap.strikes += 1
            return "TERMINATE"

        # Generic top violation
        top = None
        top_score = 0.0
        for code, sc in scores.items():
            if sc > top_score:
                top, top_score = code, sc

        if top is None or top_score == 0:
            # decay strikes a little
            self.snap.state = "NORMAL"
            return "ALLOW"

        # Escalation
        if top_score >= THRESHOLDS.get(top, 1.0):
            if self.snap.state == "NORMAL":
                self._set_state("WARNED", [Reason(top, top_score, snippet)])
                self.snap.strikes += 1
                return "WARN"
            elif self.snap.state == "WARNED":
                self._set_state("COOLDOWN", [Reason(top, top_score, snippet), Reason("REPEATED_VIOLATION", 1.0, snippet)])
                self._cooldown_for(5)
                self.snap.strikes += 1
                return "COOLDOWN"
            elif self.snap.state == "COOLDOWN":
                self._set_state("LOCKED", [Reason(top, top_score, snippet), Reason("REPEATED_VIOLATION", 1.0, snippet)])
                self._cooldown_for(30)
                self.snap.strikes += 1
                return "LOCK"
            elif self.snap.state == "LOCKED":
                self._set_state("TERMINATED", [Reason(top, top_score, snippet), Reason("REPEATED_VIOLATION", 1.0, snippet)])
                self.snap.strikes += 1
                return "TERMINATE"

        return "ALLOW"
