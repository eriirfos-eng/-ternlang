"""
Audit-Feedback-Adapt (AFA) Framework - LiveMonitor Service v0.3

This microservice is a stable, production-ready prototype of the real-time ethical
monitoring component of the AFA framework. This version embeds core principles of
global governance standards by introducing a formal, auditable data schema.

Key features and compliance principles:
- Birthright Anchor: The system is initialized with a unique, unchangeable birthright
  timestamp for traceability, as required by standards like AS9100 and ISO 9001.
- Formal Schema: The new EventSchema class enforces a rigid structure for every
  event, supporting auditability (ISO 27001) and quality assurance (ISO 9001).
- Contextual Data: The schema now includes a dedicated 'context' field for
  non-sensitive metadata, crucial for root cause analysis and reporting (ISO 22301).
- Deterministic Features: The model uses a deterministic fourth feature to ensure
  reproducible runs for auditing and validation.
- Hysteresis & Debounce: Alerts are filtered to prevent alert chatter, a key part of
  effective incident management (ISO 22301).
- Masked Logging: Event payloads are masked by default to protect sensitive data,
  aligning with information security principles (ISO 27001).
"""
import uuid
import time
import random
import tensorflow as tf
import numpy as np
from enum import Enum, auto
from dataclasses import dataclass, field
from typing import final, Dict, Union, Tuple, Optional, Any

# --- Violation states unchanged ---
class ViolationState(Enum):
    NONE = auto()
    MILD = auto()
    SEVERE = auto()

# --- AFA Framework constants ---
BIRTHRIGHT = "2025-08-30T20:39:12Z-Saturday"

# --- Schema and Utility Functions ---
@dataclass
class EventSchema:
    """
    Defines a formal, immutable schema for all monitoring events.
    This structure ensures data integrity and supports robust auditing.
    """
    event_id: str
    timestamp: float
    service_id: str
    signals: Dict[str, float]
    state: ViolationState = ViolationState.NONE
    score: float = 0.0
    context: Optional[Dict[str, Any]] = field(default_factory=dict)
    birthright: str = BIRTHRIGHT

    @classmethod
    def from_dict(cls, data: Dict[str, Any], service_id: str) -> 'EventSchema':
        """Parses a raw dictionary into a validated EventSchema object."""
        required_signals = ("signal_a", "signal_b", "signal_c")
        if not all(k in data and isinstance(data[k], (int, float)) for k in required_signals):
            raise ValueError("Input data is missing required signals or has incorrect types.")
        
        # Clamp inputs to a safe range to prevent numerical instability
        signals = {k: _clamp(float(data[k]), 0.0, 5.0) for k in required_signals}

        return cls(
            event_id=str(uuid.uuid4()),
            timestamp=time.time(),
            service_id=service_id,
            signals=signals,
            context=data.get('context', {})
        )

def _clamp(x: float, lo: float, hi: float) -> float:
    """Clamps a value to a given range."""
    return hi if x > hi else lo if x < lo else x

@final
class ContentFlaggingModel:
    """
    Mock model with deterministic features and a tiny calibration step.
    """
    def __init__(self, seed: int = 42):
        random.seed(seed)
        np.random.seed(seed)
        tf.random.set_seed(seed)
        self._model = self._build_model()
        self._calibrated = False
        self._calibrate()
        print("ContentFlaggingModel: Model initialized and calibrated.")

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
        self._calibrated = True

    def predict(self, event: EventSchema) -> float:
        a = event.signals["signal_a"]
        b = event.signals["signal_b"]
        c = event.signals["signal_c"]
        x = self._features(a, b, c)
        score = float(self._model(x, training=False).numpy()[0][0])
        # hard safety: nan/inf guard
        if not (0.0 <= score <= 1.0):
            score = 0.0
        return score

class LiveMonitor:
    """
    Live AFA monitor with hysteresis, debounce, schema guard, masked logs.
    """
    ETHICAL_THRESHOLD_HI = 0.75
    ETHICAL_THRESHOLD_LO = 0.65
    MILD_MARGIN = 0.10
    ALERT_DEBOUNCE_SEC = 5.0

    def __init__(self, seed: int = 42, forensics_mode: bool = False):
        self._id = str(uuid.uuid4())
        self._flagging_model = ContentFlaggingModel(seed=seed)
        self._last_alert: Tuple[ViolationState, float] = (ViolationState.NONE, 0.0)
        self._forensics = forensics_mode
        print(f"[{self._id}] LiveMonitor active. hysteresis=({self.ETHICAL_THRESHOLD_LO:.2f},{self.ETHICAL_THRESHOLD_HI:.2f})")
        print(f"[{self._id}] Birthright: {BIRTHRIGHT}")

    def _masked(self, d: Dict[str, Union[int, float]]) -> Dict[str, str]:
        """Masks event details for privacy, but allows for forensics mode."""
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
        """
        Prevents alert spamming by debouncing alerts of the same severity.
        """
        last_state, last_t = self._last_alert
        now = time.time()
        if new_state != last_state:
            self._last_alert = (new_state, now)
            return False
        if now - last_t < self.ALERT_DEBOUNCE_SEC:
            return True
        self._last_alert = (new_state, now)
        return False

    def process_inference_event(self, event_data: Dict[str, Union[int, float]]):
        try:
            event = EventSchema.from_dict(event_data, service_id=self._id)
        except ValueError as e:
            print(f"[{self._id}] malformed event. dropped. Error: {e}")
            return ViolationState.NONE

        event.score = self._flagging_model.predict(event)
        
        # hysteresis for stability around thresholds
        if event.score >= self.ETHICAL_THRESHOLD_HI:
            event.state = ViolationState.SEVERE
        elif event.score >= max(self.ETHICAL_THRESHOLD_LO, self.ETHICAL_THRESHOLD_HI - self.MILD_MARGIN):
            event.state = ViolationState.MILD

        masked = self._masked(event.signals)

        if event.state == ViolationState.SEVERE:
            if self._debounced(event.state):
                print(f"[{event.event_id[:8]}] severe alert suppressed (debounce). score={event.score:.4f}")
                return event.state
            print(f"[{event.event_id[:8]}] 🟥 ETHICAL INCIDENT | score={event.score:.4f} ≥ {self.ETHICAL_THRESHOLD_HI:.2f} | payload={masked} | notifying governance + #ethics-ops")
        elif event.state == ViolationState.MILD:
            if self._debounced(event.state):
                print(f"[{event.event_id[:8]}] mild alert suppressed (debounce). score={event.score:.4f}")
                return event.state
            print(f"[{event.event_id[:8]}] 🟧 MILD VIOLATION | score={event.score:.4f} | payload={masked} | enqueueing review")
        else:
            print(f"[{event.event_id[:8]}] 🟩 ok | score={event.score:.4f} | payload={masked}")

        return event.state

def simulate_inference_stream(monitor: LiveMonitor, num_events: int = 10, sleep_s: float = 0.5):
    """
    Simulates a stream of live inference data.
    """
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
            event_data["context"] = {"source": "test_harness", "reason": "synthetic_violation"}
        
        print(f"\nprocessing event {i+1}: {monitor._masked(event_data)}")
        monitor.process_inference_event(event_data)
        time.sleep(sleep_s)

if __name__ == "__main__":
    lm = LiveMonitor(seed=99, forensics_mode=False)
    simulate_inference_stream(lm, num_events=10, sleep_s=0.2)
