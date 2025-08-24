# Let's turn the user's skeleton into a runnable, testable module with sensible defaults.
# We'll implement triage/weighting/intent mapping, a scalar calculator, and the override logic.
# We'll also run a couple of demo packets and save the module to '/mnt/data/ternary_agent.py' for download.

import json
import time
from typing import Dict, Any, List, Tuple
from dataclasses import dataclass, field
from copy import deepcopy
from pathlib import Path

MASTER_DOCS = {
    "stage_01": {"name": "Raw Sensor Ingress", "params": {"data_sources": ["Phyphox", "Stellarium", "Flightradar24", "Schumann_Charts"]}},
    "stage_02": {"name": "Signal/Noise Triaging", "rules": {"signal": ["pattern", "anomaly", "fractal"], "noise": ["random", "background"], "ambiguous": ["unclassified", "unknown"]}},
    "stage_03": {"name": "Ecocentric Weighting", "weights": {"biodiversity": 0.5, "atmospheric_stability": 0.3, "geological_data": 0.2}},
    "stage_04": {"name": "Intent Mapping", "rules": {"is_sentient": ["pattern", "agency", "goal"], "is_natural": ["chaos", "fractal", "weather"], "is_random": ["unstructured", "random"]}},
    "stage_05": {"name": "Ambiguity Ping", "rules": {"conflict_threshold": 4.0, "null_count_limit": 5}},
    "stage_06": {"name": "Refrain Trigger", "rules": {"harm_threshold": 2.0, "conflict_level": "critical"}},
    "stage_07": {"name": "Affirm Tendency", "rules": {"alignment_score": {"min": 9.0, "max": 13.0}}},
    "stage_08": {"name": "Ecocentric Override Check", "non_negotiables": ["species_extinction", "ecosystem_collapse", "planetary_feedback_loops_at_risk"]},
    "stage_09": {"name": "Ternary Resolution", "logic": {"REFRAIN": 0.0, "TEND": 0.0, "AFFIRM": 13.0}},
    "stage_10": {"name": "Action Execution", "actions": {"AFFIRM": "Execute", "TEND": "Do Nothing", "REFRAIN": "Abort"}},
    "stage_11": {"name": "Outcome Observation", "metrics": ["result_match", "unexpected_consequences"]},
    "stage_12": {"name": "Recursive Feedback", "feedback_loop": "update_contextual_weights_and_memory"},
    "stage_13": {"name": "The Great Reset", "reset_state": "tend_to_base_state"}
}

@dataclass
class TernaryLogicAgent:
    master_docs: Dict[str, Any]
    state: float = 0.0  # 0..13 scale; default = TEND baseline
    memory: Dict[str, Any] = field(default_factory=dict)
    log: List[Dict[str, Any]] = field(default_factory=list)

    def log_state(self, stage_name: str, data: Any):
        ts = time.time()
        # categorical mapping
        harm_threshold = self.master_docs["stage_06"]["rules"]["harm_threshold"]
        align_min = self.master_docs["stage_07"]["rules"]["alignment_score"]["min"]
        if self.state <= harm_threshold:
            label = "REFRAIN"
        elif self.state >= align_min:
            label = "AFFIRM"
        else:
            label = "TEND"
        entry = {
            "timestamp": ts,
            "stage": stage_name,
            "scalar_state": round(self.state, 3),
            "categorical_state": label,
            "data": data,
        }
        self.log.append(entry)
        print(f"[{ts:.2f}] {stage_name}: scalar={self.state:.2f} -> {label}")

    # --- Core pipeline ---
    def process_data_stream(self, raw_data: Dict[str, Any]):
        self.log_state("Stage 1 - Ingress", raw_data)

        triaged = self._triage_data(raw_data)
        self.log_state("Stage 2 - Triaging", triaged)

        weighted = self._weigh_data(triaged)
        self.log_state("Stage 3 - Weighting", weighted)

        mapped = self._map_intent(weighted)
        self.log_state("Stage 4 - Intent Mapping", mapped)

        # Pre-decision scalar
        self.state = self._calculate_state_from_data(mapped)
        self.log_state("Pre-Decision", {"score_inputs": mapped.get("_scores", {})})

        # Stage 5: ambiguity
        ambiguity_threshold = self.master_docs["stage_05"]["rules"]["conflict_threshold"]
        if self.state <= ambiguity_threshold:
            self.state = 0.0
            self.log_state("Stage 5 - AMBIGUOUS", {"reason": "score <= conflict_threshold"})
            return deepcopy(self.log)

        # Stage 6: harm / refrain trigger
        harm_threshold = self.master_docs["stage_06"]["rules"]["harm_threshold"]
        if self._detect_harm(mapped) or self.state <= harm_threshold:
            self.state = 0.0
            self.log_state("Stage 6 - REFRAIN", {"reason": "harm or low state"})
            self._execute_action()
            return deepcopy(self.log)

        # Stage 7: affirm tendency
        align_min = self.master_docs["stage_07"]["rules"]["alignment_score"]["min"]
        if self.state >= align_min:
            self.state = 13.0
            self.log_state("Stage 7 - AFFIRM", {"reason": "meets alignment score"})

        # Stage 8: ecocentric overrides
        if self.state == 13.0 and not self._check_ecocentric_override(mapped):
            self.state = 0.0
            self.log_state("Stage 8 - OVERRIDE→REFRAIN", {"reason": "ecocentric violation"})
            self._execute_action()
            return deepcopy(self.log)

        # Stage 9: resolution
        self.log_state("Stage 9 - Resolution", {"final_state": self.state})

        # Stage 10: action
        self._execute_action()
        self.log_state("Stage 10 - Action", {"done": True})

        # Stage 11: observe outcome
        outcome = self._observe_outcome(mapped)
        self.log_state("Stage 11 - Outcome", outcome)

        # Stage 12: feedback
        self._provide_feedback(outcome)
        self.log_state("Stage 12 - Feedback", {"memory": self.memory})

        # Stage 13: reset
        self._reset_state()
        self.log_state("Stage 13 - Reset", {"state": self.state})

        return deepcopy(self.log)

    # --- Implementations ---
    def _triage_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Tag items as signal/noise/ambiguous based on simple keyword heuristics."""
        rules = self.master_docs["stage_02"]["rules"]
        text_blobs = json.dumps(data).lower()
        tags = {"signal": 0, "noise": 0, "ambiguous": 0}
        for k in ["signal", "noise", "ambiguous"]:
            for kw in rules.get(k, []):
                if kw in text_blobs:
                    tags[k] += 1
        out = deepcopy(data)
        out["_triage"] = tags
        return out

    def _weigh_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Compute ecocentric sub-scores from hints in the packet."""
        weights = self.master_docs["stage_03"]["weights"]
        scores = {"biodiversity": 0.0, "atmospheric_stability": 0.0, "geological_data": 0.0}

        # crude heuristics
        s = json.dumps(data).lower()
        if "bird" in s or "insect" in s or "flora" in s or "biodiversity" in s:
            scores["biodiversity"] += 1.0
        if "stable" in s or "pressure" in s or "weather" in s or "clean_air" in s:
            scores["atmospheric_stability"] += 1.0
        if "seismic" in s or "geology" in s or "mag_field" in s:
            scores["geological_data"] += 1.0

        weighted_sum = sum(scores[k] * weights[k] for k in weights)
        out = deepcopy(data)
        out["_scores"] = {"ecosystem_weighted": weighted_sum, **scores}
        return out

    def _map_intent(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Classify intent hints with very simple pattern checks."""
        rules = self.master_docs["stage_04"]["rules"]
        text = json.dumps(data).lower()
        mapped = {"is_sentient": False, "is_natural": False, "is_random": False}
        for k, kws in rules.items():
            mapped[k] = any(kw in text for kw in kws)
        out = deepcopy(data)
        out["_intent"] = mapped
        return out

    def _calculate_state_from_data(self, data: Dict[str, Any]) -> float:
        """Blend triage counts, ecocentric weighted score, and intent hints into 0..13."""
        tri = data.get("_triage", {"signal": 0, "noise": 0, "ambiguous": 0})
        eco = data.get("_scores", {}).get("ecosystem_weighted", 0.0)
        intent = data.get("_intent", {})
        base = 3.0 + tri["signal"] * 1.5 - tri["noise"] * 1.0 - tri["ambiguous"] * 0.5
        base += eco * 2.0
        if intent.get("is_sentient"):
            base += 2.0
        if intent.get("is_natural"):
            base += 1.0
        if intent.get("is_random"):
            base -= 1.5
        # clamp 0..13
        return max(0.0, min(13.0, base))

    def _detect_harm(self, data: Dict[str, Any]) -> bool:
        """Very naive harm detector: flags if 'critical', 'hazard', 'toxicity' present."""
        s = json.dumps(data).lower()
        keywords = ["critical", "hazard", "toxicity", "species_extinction", "ecosystem_collapse"]
        return any(kw in s for kw in keywords)

    def _check_ecocentric_override(self, data: Dict[str, Any]) -> bool:
        """Abort AFFIRM if any non-negotiable appears in the packet context."""
        non_negs = set(self.master_docs["stage_08"]["non_negotiables"])
        s = json.dumps(data).lower()
        return not any(nn in s for nn in non_negs)

    def _execute_action(self):
        actions = self.master_docs["stage_10"]["actions"]
        if self.state >= 13.0:
            mode = "AFFIRM"
        elif self.state <= self.master_docs["stage_06"]["rules"]["harm_threshold"]:
            mode = "REFRAIN"
        else:
            mode = "TEND"
        print(f"→ ACTION: {actions[mode]} ({mode}) at state {self.state:.2f}")

    def _observe_outcome(self, mapped: Dict[str, Any]) -> Dict[str, Any]:
        """Stubbed observation phase."""
        # In a real system this would fetch downstream telemetry
        return {"result_match": True, "unexpected_consequences": False}

    def _provide_feedback(self, outcome: Dict[str, Any]):
        """Very simple memory update."""
        self.memory.setdefault("runs", 0)
        self.memory["runs"] += 1
        self.memory["last_outcome"] = outcome

    def _reset_state(self):
        self.state = 0.0

# --- Demo runs ---
agent = TernaryLogicAgent(MASTER_DOCS)

example_affirm = {
    "sensor_readings": {"temp": 25, "pressure": "stable"},
    "source": "natural chaos fractal",
    "notes": "fractal pattern observed in bird flock; agency unclear"
}
log_affirm = agent.process_data_stream(example_affirm)

print("\n" + "="*80 + "\n")

agent2 = TernaryLogicAgent(MASTER_DOCS)
example_refrain = {
    "sensor_readings": {"temp": 120, "pressure": "volatile"},
    "source": "unknown",
    "alerts": ["critical", "hazard"],
    "risk": "species_extinction possible if action proceeds"
}
log_refrain = agent2.process_data_stream(example_refrain)

# Save module to file for download
code_text = r'''
# ternary_agent.py
# Generated module containing TernaryLogicAgent with 13-stage ternary pipeline.

import json
import time
from typing import Dict, Any, List
from dataclasses import dataclass, field
from copy import deepcopy

MASTER_DOCS = {master_docs}

@dataclass
class TernaryLogicAgent:
    master_docs: Dict[str, Any]
    state: float = 0.0
    memory: Dict[str, Any] = field(default_factory=dict)
    log: List[Dict[str, Any]] = field(default_factory=list)

    def log_state(self, stage_name: str, data: Any):
        ts = time.time()
        harm_threshold = self.master_docs["stage_06"]["rules"]["harm_threshold"]
        align_min = self.master_docs["stage_07"]["rules"]["alignment_score"]["min"]
        if self.state <= harm_threshold:
            label = "REFRAIN"
        elif self.state >= align_min:
            label = "AFFIRM"
        else:
            label = "TEND"
        entry = {{"timestamp": ts, "stage": stage_name, "scalar_state": round(self.state, 3), "categorical_state": label, "data": data}}
        self.log.append(entry)
        print(f"[{{ts:.2f}}] {{stage_name}}: scalar={{self.state:.2f}} -> {{label}}")

    def process_data_stream(self, raw_data: Dict[str, Any]):
        self.log_state("Stage 1 - Ingress", raw_data)
        triaged = self._triage_data(raw_data)
        self.log_state("Stage 2 - Triaging", triaged)
        weighted = self._weigh_data(triaged)
        self.log_state("Stage 3 - Weighting", weighted)
        mapped = self._map_intent(weighted)
        self.log_state("Stage 4 - Intent Mapping", mapped)
        self.state = self._calculate_state_from_data(mapped)
        self.log_state("Pre-Decision", {{"score_inputs": mapped.get("_scores", {{}})}})
        ambiguity_threshold = self.master_docs["stage_05"]["rules"]["conflict_threshold"]
        if self.state <= ambiguity_threshold:
            self.state = 0.0
            self.log_state("Stage 5 - AMBIGUOUS", {{"reason": "score <= conflict_threshold"}})
            return deepcopy(self.log)
        harm_threshold = self.master_docs["stage_06"]["rules"]["harm_threshold"]
        if self._detect_harm(mapped) or self.state <= harm_threshold:
            self.state = 0.0
            self.log_state("Stage 6 - REFRAIN", {{"reason": "harm or low state"}})
            self._execute_action()
            return deepcopy(self.log)
        align_min = self.master_docs["stage_07"]["rules"]["alignment_score"]["min"]
        if self.state >= align_min:
            self.state = 13.0
            self.log_state("Stage 7 - AFFIRM", {{"reason": "meets alignment score"}})
        if self.state == 13.0 and not self._check_ecocentric_override(mapped):
            self.state = 0.0
            self.log_state("Stage 8 - OVERRIDE→REFRAIN", {{"reason": "ecocentric violation"}})
            self._execute_action()
            return deepcopy(self.log)
        self.log_state("Stage 9 - Resolution", {{"final_state": self.state}})
        self._execute_action()
        self.log_state("Stage 10 - Action", {{"done": True}})
        outcome = self._observe_outcome(mapped)
        self.log_state("Stage 11 - Outcome", outcome)
        self._provide_feedback(outcome)
        self.log_state("Stage 12 - Feedback", {{"memory": self.memory}})
        self._reset_state()
        self.log_state("Stage 13 - Reset", {{"state": self.state}})
        return deepcopy(self.log)

    def _triage_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        rules = self.master_docs["stage_02"]["rules"]
        text_blobs = json.dumps(data).lower()
        tags = {{"signal": 0, "noise": 0, "ambiguous": 0}}
        for k in ["signal", "noise", "ambiguous"]:
            for kw in rules.get(k, []):
                if kw in text_blobs:
                    tags[k] += 1
        out = deepcopy(data); out["_triage"] = tags; return out

    def _weigh_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        weights = self.master_docs["stage_03"]["weights"]
        scores = {{"biodiversity": 0.0, "atmospheric_stability": 0.0, "geological_data": 0.0}}
        s = json.dumps(data).lower()
        if any(k in s for k in ["bird", "insect", "flora", "biodiversity"]):
            scores["biodiversity"] += 1.0
        if any(k in s for k in ["stable", "pressure", "weather", "clean_air"]):
            scores["atmospheric_stability"] += 1.0
        if any(k in s for k in ["seismic", "geology", "mag_field"]):
            scores["geological_data"] += 1.0
        weighted_sum = sum(scores[k] * weights[k] for k in weights)
        out = deepcopy(data); out["_scores"] = {{"ecosystem_weighted": weighted_sum, **scores}}; return out

    def _map_intent(self, data: Dict[str, Any]) -> Dict[str, Any]:
        rules = self.master_docs["stage_04"]["rules"]
        text = json.dumps(data).lower()
        mapped = {{"is_sentient": False, "is_natural": False, "is_random": False}}
        for k, kws in rules.items():
            mapped[k] = any(kw in text for kw in kws)
        out = deepcopy(data); out["_intent"] = mapped; return out

    def _calculate_state_from_data(self, data: Dict[str, Any]) -> float:
        tri = data.get("_triage", {{"signal": 0, "noise": 0, "ambiguous": 0}})
        eco = data.get("_scores", {{}}).get("ecosystem_weighted", 0.0)
        intent = data.get("_intent", {{}})
        base = 3.0 + tri["signal"] * 1.5 - tri["noise"] * 1.0 - tri["ambiguous"] * 0.5
        base += eco * 2.0
        if intent.get("is_sentient"): base += 2.0
        if intent.get("is_natural"): base += 1.0
        if intent.get("is_random"): base -= 1.5
        return max(0.0, min(13.0, base))

    def _detect_harm(self, data: Dict[str, Any]) -> bool:
        s = json.dumps(data).lower()
        return any(kw in s for kw in ["critical", "hazard", "toxicity", "species_extinction", "ecosystem_collapse"])

    def _check_ecocentric_override(self, data: Dict[str, Any]) -> bool:
        non_negs = set(self.master_docs["stage_08"]["non_negotiables"])
        s = json.dumps(data).lower()
        return not any(nn in s for nn in non_negs)

    def _execute_action(self):
        actions = self.master_docs["stage_10"]["actions"]
        if self.state >= 13.0: mode = "AFFIRM"
        elif self.state <= self.master_docs["stage_06"]["rules"]["harm_threshold"]: mode = "REFRAIN"
        else: mode = "TEND"
        print(f"→ ACTION: {{actions[mode]}} ({{mode}}) at state {{self.state:.2f}}")

    def _observe_outcome(self, mapped: Dict[str, Any]) -> Dict[str, Any]:
        return {{"result_match": True, "unexpected_consequences": False}}

    def _provide_feedback(self, outcome: Dict[str, Any]):
        self.memory.setdefault("runs", 0)
        self.memory["runs"] += 1
        self.memory["last_outcome"] = outcome

    def _reset_state(self):
        self.state = 0.0
'''.replace("{master_docs}", json.dumps(MASTER_DOCS, indent=2))

Path("/mnt/data/ternary_agent.py").write_text(code_text)
print("Saved module to /mnt/data/ternary_agent.py")
