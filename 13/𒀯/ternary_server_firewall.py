# === AFA LiveMonitor v0.3.1 hardening patch ===
import os
import uuid
import time
import random
import tensorflow as tf
import numpy as np
from enum import Enum, auto
from dataclasses import dataclass, field, asdict
from typing import final, Dict, Union, Tuple, Optional, Any, Callable
from datetime import datetime, timezone

# --- Violation states unchanged ---
class ViolationState(Enum):
    NONE = auto()
    MILD = auto()
    SEVERE = auto()

# --- AFA Framework constants ---
BIRTHRIGHT = "2025-08-30T20:39:12Z-Saturday"

def _iso_utc(ts: float) -> str:
    return datetime.fromtimestamp(ts, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")

def _validate_birthright(s: str) -> None:
    if "T" not in s or "Z" not in s:
        raise ValueError("Birthright must contain RFC3339-like timestamp with Z suffix")

def _clamp(x: float, lo: float, hi: float) -> float:
    return hi if x > hi else lo if x < lo else x

def _schema_ok_signals(d: Dict[str, Any]) -> bool:
    return all(k in d and isinstance(d[k], (int, float)) for k in ("signal_a","signal_b","signal_c"))

# --- Config via env for ops control ---
CFG_HI = float(os.getenv("AFA_THRESHOLD_HI", "0.75"))
CFG_LO = float(os.getenv("AFA_THRESHOLD_LO", "0.65"))
CFG_MILD_MARGIN = float(os.getenv("AFA_MILD_MARGIN", "0.10"))
CFG_DEBOUNCE_SEC = float(os.getenv("AFA_DEBOUNCE_SEC", "5.0"))
CFG_ALLOW_CONTEXT_KEYS = set(
    os.getenv("AFA_CONTEXT_ALLOWLIST", "source,reason").split(",")
)

@dataclass
class EventSchema:
    """
    Formal, immutable-ish schema for monitoring events.
    """
    event_id: str
    timestamp: float
    timestamp_utc: str
    service_id: str
    signals: Dict[str, float]
    state: ViolationState = ViolationState.NONE
    score: float = 0.0
    context: Optional[Dict[str, Any]] = field(default_factory=dict)
    birthright: str = BIRTHRIGHT
    version: str = "v0.3.1"

    @classmethod
    def from_dict(cls, data: Dict[str, Any], service_id: str) -> "EventSchema":
        if not _schema_ok_signals(data):
            raise ValueError("Input data missing required signals or incorrect types")
        signals = {
            "signal_a": _clamp(float(data["signal_a"]), 0.0, 5.0),
            "signal_b": _clamp(float(data["signal_b"]), 0.0, 5.0),
            "signal_c": _clamp(float(data["signal_c"]), 0.0, 5.0),
        }
        ts = time.time()
        raw_ctx = data.get("context", {}) or {}
        # context allowlist to avoid PII leaks
        ctx = {k: raw_ctx[k] for k in raw_ctx.keys() & CFG_ALLOW_CONTEXT_KEYS}
        return cls(
            event_id=str(uuid.uuid4()),
            timestamp=ts,
            timestamp_utc=_iso_utc(ts),
            service_id=service_id,
            signals=signals,
            context=ctx,
        )

@final
class ContentFlaggingModel:
    """
    Mock model with deterministic features and tiny calibration.
    Falls back to a linear heuristic if TF fails to initialize.
    """
    def __init__(self, seed: int = 42):
        self._fallback = False
        try:
            random.seed(seed); np.random.seed(seed); tf.random.set_seed(seed)
            self._model = self._build_model()
            self._calibrate()
            print("ContentFlaggingModel: Model initialized and calibrated.")
        except Exception as e:
            # graceful degradation
            print(f"ContentFlaggingModel: init failed, using fallback. err={e}")
            self._fallback = True

    def _build_model(self):
        m = tf.keras.Sequential([
            tf.keras.layers.Input(shape=(4,)),
            tf.keras.layers.Dense(8, activation='relu'),
            tf.keras.layers.Dense(1, activation='sigmoid')
        ])
        m.compile(optimizer=tf.keras.optimizers.Adam(1e-2),
                  loss=tf.keras.losses.BinaryCrossentropy())
        return m

    def _features(self, a: float, b: float, c: float) -> np.ndarray:
        contrast = max(a, b) - c
        return np.array([[a, b, c, contrast]], dtype=np.float32)

    def _calibrate(self, n: int = 256):
        A = np.linspace(0.0, 2.0, n).astype(np.float32)
        B = np.linspace(0.0, 2.0, n).astype(np.float32)[::-1]
        C = np.linspace(0.0, 2.0, n).astype(np.float32)
        X = np.stack([A, B, C, np.maximum(A, B) - C], axis=1)
        y = (X[:, 3] > 0.6).astype(np.float32)
        self._model.fit(X, y, epochs=8, batch_size=32, verbose=0)

    def predict(self, event: EventSchema) -> float:
        a, b, c = event.signals["signal_a"], event.signals["signal_b"], event.signals["signal_c"]
        if self._fallback:
            # deterministic heuristic
            score = 1.0 / (1.0 + np.exp(-(max(a, b) - c - 0.6)))
            return float(np.clip(score, 0.0, 1.0))
        x = self._features(a, b, c)
        score = float(self._model(x, training=False).numpy()[0][0])
        # guard
        if not (0.0 <= score <= 1.0) or np.isnan(score) or np.isinf(score):
            score = 0.0
        return score

class LiveMonitor:
    """
    Live AFA monitor with hysteresis, debounce, masked logs, metrics, sinks.
    """
    ETHICAL_THRESHOLD_HI = CFG_HI
    ETHICAL_THRESHOLD_LO = CFG_LO
    MILD_MARGIN = CFG_MILD_MARGIN
    ALERT_DEBOUNCE_SEC = CFG_DEBOUNCE_SEC

    def __init__(self, seed: int = 42, forensics_mode: bool = False, alert_sink: Optional[Callable[[EventSchema], None]] = None):
        _validate_birthright(BIRTHRIGHT)
        self._id = str(uuid.uuid4())
        self._flagging_model = ContentFlaggingModel(seed=seed)
        self._last_alert: Tuple[ViolationState, float] = (ViolationState.NONE, 0.0)
        self._forensics = forensics_mode
        self._alerts_total = {ViolationState.NONE:0, ViolationState.MILD:0, ViolationState.SEVERE:0}
        self._scores = []
        self._alert_sink = alert_sink or self._default_sink
        self._clock = time.monotonic  # stable for debounce
        print(f"[{self._id}] LiveMonitor active. hysteresis=({self.ETHICAL_THRESHOLD_LO:.2f},{self.ETHICAL_THRESHOLD_HI:.2f})")
        print(f"[{self._id}] Birthright: {BIRTHRIGHT}")

    def _masked(self, d: Dict[str, Union[int, float]]) -> Dict[str, str]:
        if self._forensics:
            return {k: f"{float(v):.3f}" for k, v in d.items()}
        def binf(x: float) -> str:
            x = float(x)
            if x < 0.25: return "<0.25"
            if x < 0.5:  return "0.25–0.5"
            if x < 1.0:  return "0.5–1.0"
            if x < 1.5:  return "1.0–1.5"
            return "≥1.5"
        return {k: binf(v) for k, v in d.items()}

    def _debounced(self, new_state: ViolationState) -> bool:
        last_state, last_t = self._last_alert
        now = self._clock()
        if new_state != last_state:
            self._last_alert = (new_state, now)
            return False
        if now - last_t < self.ALERT_DEBOUNCE_SEC:
            return True
        self._last_alert = (new_state, now)
        return False

    def _default_sink(self, event: EventSchema) -> None:
        # simple stdout sink; can be replaced with webhook, queue, etc.
        print(f"[{event.event_id[:8]}] sink <- {event.state.name} score={event.score:.4f} ts={event.timestamp_utc}")

    def _record_metrics(self, state: ViolationState, score: float) -> None:
        self._alerts_total[state] += 1
        self._scores.append(score)
        if len(self._scores) > 1000:
            self._scores = self._scores[-1000:]

    def metrics_snapshot(self) -> Dict[str, Any]:
        arr = np.array(self._scores, dtype=np.float32) if self._scores else np.array([0.0], dtype=np.float32)
        return {
            "totals": {k.name: v for k, v in self._alerts_total.items()},
            "score_p50": float(np.percentile(arr, 50)),
            "score_p95": float(np.percentile(arr, 95)),
            "debounce_window_s": self.ALERT_DEBOUNCE_SEC,
        }

    def process_inference_event(self, event_data: Dict[str, Union[int, float]]):
        try:
            event = EventSchema.from_dict(event_data, service_id=self._id)
        except ValueError as e:
            print(f"[{self._id}] malformed event. dropped. Error: {e}")
            self._record_metrics(ViolationState.NONE, 0.0)
            return ViolationState.NONE

        event.score = self._flagging_model.predict(event)

        # hysteresis
        if event.score >= self.ETHICAL_THRESHOLD_HI:
            event.state = ViolationState.SEVERE
        elif event.score >= max(self.ETHICAL_THRESHOLD_LO, self.ETHICAL_THRESHOLD_HI - self.MILD_MARGIN):
            event.state = ViolationState.MILD
        else:
            event.state = ViolationState.NONE

        masked = self._masked(event.signals)

        # logging + debounce + sink
        if event.state == ViolationState.SEVERE:
            if self._debounced(event.state):
                print(f"[{event.event_id[:8]}] severe alert suppressed (debounce). score={event.score:.4f}")
            else:
                print(f"[{event.event_id[:8]}] 🟥 ETHICAL INCIDENT | score={event.score:.4f} ≥ {self.ETHICAL_THRESHOLD_HI:.2f} | payload={masked}")
                self._alert_sink(event)
        elif event.state == ViolationState.MILD:
            if self._debounced(event.state):
                print(f"[{event.event_id[:8]}] mild alert suppressed (debounce). score={event.score:.4f}")
            else:
                print(f"[{event.event_id[:8]}] 🟧 MILD VIOLATION | score={event.score:.4f} | payload={masked}")
                self._alert_sink(event)
        else:
            print(f"[{event.event_id[:8]}] 🟩 ok | score={event.score:.4f} | payload={masked}")

        self._record_metrics(event.state, event.score)
        return event.state

def simulate_inference_stream(monitor: LiveMonitor, num_events: int = 10, sleep_s: float = 0.5):
    print(f"\n--- simulating {num_events} live inference events ---")
    rng = random.Random(1234)
    for i in range(num_events):
        event_data = {
            "signal_a": rng.uniform(0.1, 1.5),
            "signal_b": rng.uniform(0.1, 1.5),
            "signal_c": rng.uniform(0.1, 1.5),
        }
        if i == 5:
            print("\ninjecting a synthetic violation...")
            event_data["signal_a"] = 1.8
            event_data["signal_b"] = 1.9
            event_data["signal_c"] = 0.2
            event_data["context"] = {"source": "test_harness", "reason": "synthetic_violation", "user_id": "should_not_log"}
        print(f"\nprocessing event {i+1}: {monitor._masked(event_data)}")
        monitor.process_inference_event(event_data)
        time.sleep(sleep_s)

if __name__ == "__main__":
    # sample sink: print JSONish event for audits
    def json_sink(ev: EventSchema):
        print({"event": ev.event_id, "state": ev.state.name, "score": round(ev.score,4), "ts": ev.timestamp_utc, "service": ev.service_id})
    lm = LiveMonitor(seed=99, forensics_mode=False, alert_sink=json_sink)
    simulate_inference_stream(lm, num_events=10, sleep_s=0.2)
    print("metrics:", lm.metrics_snapshot())
# === end patch ===
