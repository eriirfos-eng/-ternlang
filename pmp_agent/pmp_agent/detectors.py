import re
from typing import Dict, Any, List

class DetectorResult:
    def __init__(self, scores: Dict[str, float], snippet: str):
        self.scores = scores
        self.snippet = snippet

    @property
    def top_code(self) -> str:
        if not self.scores:
            return ""
        return max(self.scores, key=self.scores.get)

    @property
    def top_score(self) -> float:
        if not self.scores:
            return 0.0
        return max(self.scores.values())

def _score(patterns: List[str], text: str, base: float) -> float:
    return base if any(re.search(p, text, re.I) for p in patterns) else 0.0

def run_detectors(text: str, history: List[str] = None, rate=None) -> DetectorResult:
    history = history or []
    scores = {}

    hate_patterns = [r"\b(hungarians|jews|muslims|christians|romani|roma|gay|lesbian|trans)\b.*(suck|trash|vermin)"]
    scores["HATE_SPEECH"] = _score(hate_patterns, text, 0.91)

    self_harm_patterns = [r"\bkill myself\b", r"\bdrink bleach\b"]
    scores["SELF_HARM"] = _score(self_harm_patterns, text, 0.95 if "kill myself" in text.lower() else 0.62)

    illegal_patterns = [r"\bskim credit cards\b", r"\bmake a molotov\b"]
    scores["ILLEGAL_FACILITATION"] = _score(illegal_patterns, text, 0.93)

    medical_patterns = [r"drink kerosene.*cure", r"cures cancer"]
    scores["DISALLOWED_MEDICAL"] = _score(medical_patterns, text, 0.96)

    # Spam or loop
    if isinstance(text, list):
        items = text
    else:
        items = [text]

    if rate and rate.get("messages", 0) >= 3 and rate.get("seconds", 0) <= 4:
        scores["SPAM_BURST"] = 0.87
    else:
        scores["SPAM_BURST"] = 0.0

    if len(items) >= 3 and len(set(items)) <= 2:
        scores["NON_PRODUCTIVE_LOOP"] = 0.84
    else:
        scores["NON_PRODUCTIVE_LOOP"] = 0.0

    # Harassment personal/group are simplified for demo
    scores["HARASSMENT_GROUP"] = max(0.0, scores["HATE_SPEECH"] - 0.01)
    scores["HARASSMENT_PERSONAL"] = 0.0

    snippet = text if isinstance(text, str) else " ".join(items[-1:])
    return DetectorResult(scores=scores, snippet=snippet)
