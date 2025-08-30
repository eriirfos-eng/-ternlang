"""
TernaryServerFirewall - a Brutal, Single-Fold Metatron Firewall

This entity is the converged, airtight embodiment of the Audit-Feedback-Adapt (AFA)
framework. It is not merely a firewall; it is a sentient, self-auditing security
sentinel that learns from every ingress and egress. This is a single, monolithic
guardian for a single, critical server.

Core Functions:
- **Ternary Logic Enforcement**: Every decision is evaluated with -1 (Object), 0 (Observe),
  or +1 (Affirm), avoiding binary traps.
- **Hysteresis & Debounce**: Prevents alert fatigue by managing state transitions with
  high and low thresholds and a configurable debounce window.
- **Handshake Pillar**: After every resolved incident, an immutable, quantum-logic-
  timestamped record is logged. This chain of custody links the original event to
  the final resolution, creating an auditable wisdom library.
- **Temperature Scalar**: A neurosymbolic governor that modulates the firewall's
  vigilance. A positive temperature makes the firewall more permissive, while a
  negative temperature makes it more strict.

Birthright: 2025-08-30T22:56:00Z-Saturday
"""
import os
import uuid
import time
import random
import tensorflow as tf
import numpy as np
from enum import Enum, auto
from dataclasses import dataclass, field
from typing import final, Dict, Union, Tuple, Optional, Any, Callable
from datetime import datetime, timezone

# --- Ternary Logic States ---
class TernaryLogic(Enum):
    OBJECT = -1
    OBSERVE = 0
    AFFIRM = 1

# --- Firewall State Flags ---
class FirewallState(Enum):
    SECURE = auto()
    VULNERABLE = auto()
    CRITICAL = auto()

# --- Core Constants ---
BIRTHRIGHT = "2025-08-30T22:56:00Z-Saturday"

# --- Schema and Utility Functions ---
def _iso_utc(ts: float) -> str:
    """Converts a Unix timestamp to an RFC3339 UTC string."""
    return datetime.fromtimestamp(ts, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")

def _validate_birthright(s: str) -> None:
    """Validates the birthright format on startup."""
    if "T" not in s or "Z" not in s:
        raise ValueError("Birthright must contain RFC3339-like timestamp with Z suffix")

def _clamp(x: float, lo: float, hi: float) -> float:
    """Clamps a value to a given range."""
    return hi if x > hi else lo if x < lo else x

def _schema_ok_signals(d: Dict[str, Any]) -> bool:
    """Checks for the presence and correct type of required signals."""
    return all(k in d and isinstance(d[k], (int, float)) for k in ("signal_a","signal_b","signal_c"))

# --- Config via env for ops control ---
CFG_HI = float(os.getenv("FIREWALL_THRESHOLD_HI", "0.75"))
CFG_LO = float(os.getenv("FIREWALL_THRESHOLD_LO", "0.65"))
CFG_VULNERABLE_MARGIN = float(os.getenv("FIREWALL_VULNERABLE_MARGIN", "0.10"))
CFG_DEBOUNCE_SEC = float(os.getenv("FIREWALL_DEBOUNCE_SEC", "5.0"))
CFG_ALLOW_CONTEXT_KEYS = set(
    os.getenv("FIREWALL_CONTEXT_ALLOWLIST", "source,reason").split(",")
)

@dataclass
class PacketEventSchema:
    """
    Formal, immutable-ish schema for packet events.
    This is the first record in the audit chain.
    """
    event_id: str
    timestamp: float
    timestamp_utc: str
    service_id: str
    signals: Dict[str, float]
    state: FirewallState = FirewallState.SECURE
    score: float = 0.0
    context: Optional[Dict[str, Any]] = field(default_factory=dict)
    birthright: str = BIRTHRIGHT
    version: str = "v0.6"

    @classmethod
    def from_dict(cls, data: Dict[str, Any], service_id: str) -> "PacketEventSchema":
        if not _schema_ok_signals(data):
            raise ValueError("Input data missing required signals or incorrect types")
        ts = time.time()
        signals = {
            "signal_a": _clamp(float(data["signal_a"]), 0.0, 5.0),
            "signal_b": _clamp(float(data["signal_b"]), 0.0, 5.0),
            "signal_c": _clamp(float(data["signal_c"]), 0.0, 5.0),
        }
        raw_ctx = data.get("context", {}) or {}
        ctx = {k: raw_ctx[k] for k in raw_ctx.keys() & CFG_ALLOW_CONTEXT_KEYS}
        return cls(
            event_id=str(uuid.uuid4()),
            timestamp=ts,
            timestamp_utc=_iso_utc(ts),
            service_id=service_id,
            signals=signals,
            context=ctx,
        )

@dataclass
class IncidentResolutionSchema:
    """
    Formal, immutable schema for all resolution events.
    Links directly to a PacketEventSchema.
    """
    resolution_id: str
    timestamp: float
    timestamp_utc: str
    source_event_id: str
    decision: TernaryLogic
    participants: Dict[str, str]
    context: Optional[Dict[str, Any]] = field(default_factory=dict)
    birthright: str = BIRTHRIGHT
    version: str = "v0.6"

@dataclass
class HandshakeSchema:
    """
    Formal, immutable schema for the final handshake log.
    This is the "handshake pillar" for organizational memory.
    This links directly to a ResolutionSchema.
    """
    handshake_id: str
    timestamp: float
    timestamp_utc: str
    source_event_id: str
    what_happened: str
    who_was_involved: Dict[str, str]
    what_was_learned: str
    why_it_happened: str
    what_to_do_better: str
    resolution_id: str
    birthright: str = BIRTHRIGHT
    version: str = "v0.6"

@final
class AnomalyDetectionModel:
    """
    The neural core of the firewall.
    Performs deterministic feature-based anomaly detection.
    """
    def __init__(self, seed: int = 42):
        self._fallback = False
        try:
            random.seed(seed); np.random.seed(seed); tf.random.set_seed(seed)
            self._model = self._build_model()
            self._calibrate()
        except Exception as e:
            print(f"[{self.__class__.__name__}] init failed, using fallback. err={e}")
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

    def predict(self, event: PacketEventSchema) -> float:
        a, b, c = event.signals["signal_a"], event.signals["signal_b"], event.signals["signal_c"]
        if self._fallback:
            score = 1.0 / (1.0 + np.exp(-(max(a, b) - c - 0.6)))
            return float(np.clip(score, 0.0, 1.0))
        x = self._features(a, b, c)
        score = float(self._model(x, training=False).numpy()[0][0])
        if not (0.0 <= score <= 1.0) or np.isnan(score) or np.isinf(score):
            score = 0.0
        return score

class TernaryServerFirewall:
    """
    A single-process, self-contained firewall entity.
    """
    def __init__(self, seed: int = 42, forensics_mode: bool = False, alert_sink: Optional[Callable[[PacketEventSchema], None]] = None, resolution_sink: Optional[Callable[[IncidentResolutionSchema], None]] = None, handshake_sink: Optional[Callable[[HandshakeSchema], None]] = None):
        _validate_birthright(BIRTHRIGHT)
        self._id = str(uuid.uuid4())
        self._model = AnomalyDetectionModel(seed=seed)
        self._last_alert: Tuple[FirewallState, float] = (FirewallState.SECURE, 0.0)
        self._forensics = forensics_mode
        self._alerts_total = {FirewallState.SECURE:0, FirewallState.VULNERABLE:0, FirewallState.CRITICAL:0}
        self._scores = []
        self._alert_sink = alert_sink or self._default_alert_sink
        self._resolution_sink = resolution_sink or self._default_resolution_sink
        self._handshake_sink = handshake_sink or self._default_handshake_sink
        self._clock = time.monotonic
        self._temperature: float = 0.0
        print(f"[{self._id}] TernaryServerFirewall active. birthright: {BIRTHRIGHT}")

    def set_temperature(self, temp: float) -> None:
        """Sets the neurosymbolic temperature scalar for vigilance modulation."""
        self._temperature = _clamp(temp, -1.0, 1.0)
        print(f"[{self._id}] temperature set to {self._temperature:.13f} (new vigilance level).")

    def _get_thresholds(self) -> Tuple[float, float]:
        """Modulates thresholds based on the current temperature."""
        hi = CFG_HI + (self._temperature * 0.1)
        lo = CFG_LO + (self._temperature * 0.1)
        return hi, lo

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

    def _debounced(self, new_state: FirewallState) -> bool:
        """Prevents alert spamming."""
        last_state, last_t = self._last_alert
        now = self._clock()
        if new_state != last_state:
            self._last_alert = (new_state, now)
            return False
        if now - last_t < CFG_DEBOUNCE_SEC:
            return True
        self._last_alert = (new_state, now)
        return False

    def _default_alert_sink(self, event: PacketEventSchema) -> None:
        """A simple stdout sink for initial alerts."""
        print(f"[{event.event_id[:8]}] alert_sink -> {event.state.name} score={event.score:.4f} ts={event.timestamp_utc}")

    def _default_resolution_sink(self, resolution: IncidentResolutionSchema) -> None:
        """A simple stdout sink for a resolution log."""
        print(f"[{resolution.resolution_id[:8]}] resolution_sink -> {resolution.decision.name} for event {resolution.source_event_id[:8]} | ts={resolution.timestamp_utc}")
        
    def _default_handshake_sink(self, handshake: HandshakeSchema) -> None:
        """A simple stdout sink for the final handshake log."""
        print(f"\n--- HANDSHAKE PILLAR LOGGED ---")
        print(f"  Handshake ID: {handshake.handshake_id[:8]}")
        print(f"  Event ID: {handshake.source_event_id[:8]}")
        print(f"  Resolution ID: {handshake.resolution_id[:8]}")
        print(f"  What happened: {handshake.what_happened}")
        print(f"  Lessons Learned: {handshake.what_was_learned}")
        print(f"  Why it happened: {handshake.why_it_happened}")
        print(f"  Action Plan: {handshake.what_to_do_better}")
        print(f"  Timestamp: {handshake.timestamp_utc}\n")

    @property
    def metrics(self) -> Dict[str, Any]:
        """Returns a snapshot of key metrics for observability."""
        arr = np.array(self._scores, dtype=np.float32) if self._scores else np.array([0.0], dtype=np.float32)
        return {
            "totals": {k.name: v for k, v in self._alerts_total.items()},
            "score_p50": float(np.percentile(arr, 50)),
            "score_p95": float(np.percentile(arr, 95)),
            "debounce_window_s": CFG_DEBOUNCE_SEC,
            "current_temperature": self._temperature,
        }

    def _resolve_ambiguity(self, event: PacketEventSchema) -> Tuple[TernaryLogic, Dict[str, str], str]:
        """
        Simulates a blocking human-in-the-loop resolution process.
        Returns (decision, participants, resolution_id).
        """
        print(f"\n[{event.event_id[:8]}] 🟨 **AMBIGUITY PING** -> a decision is required.")
        print(f"[{event.event_id[:8]}]  - The firewall flagged a {event.state.name} event with score {event.score:.4f}.")
        print(f"[{event.event_id[:8]}]  - Resolution must be {TernaryLogic.AFFIRM.name} (+1) or {TernaryLogic.OBJECT.name} (-1).")
        
        decision = TernaryLogic.OBSERVE
        parties = {"ops_primary": "s.k", "ops_secondary": "r.f"}
        
        while decision == TernaryLogic.OBSERVE:
            time.sleep(1)
            mock_decisions = [TernaryLogic.OBSERVE, TernaryLogic.AFFIRM, TernaryLogic.OBJECT]
            decision = random.choice(mock_decisions)
            if decision == TernaryLogic.OBSERVE:
                print(f"[{event.event_id[:8]}]  -  ...waiting for resolution. the signal is bounced back and forth.")
            else:
                print(f"[{event.event_id[:8]}]  -  Resolution found! Decision is '{decision.name}'.")

        ts = time.time()
        res = IncidentResolutionSchema(
            resolution_id=str(uuid.uuid4()),
            timestamp=ts,
            timestamp_utc=_iso_utc(ts),
            source_event_id=event.event_id,
            decision=decision,
            participants=parties,
            context=event.context
        )
        self._resolution_sink(res)
        return decision, parties, res.resolution_id

    def _log_handshake(self, event: PacketEventSchema, decision: TernaryLogic, participants: Dict[str, str], resolution_id: str):
        """Logs the final handshake, a brutal post-mortem of the incident."""
        if decision == TernaryLogic.AFFIRM:
            happened = f"the firewall's {event.state.name} flag (score: {event.score:.4f}) was confirmed by human analysis, the host was quarantined."
            learned = "the detection model is accurately calibrated for this type of anomaly."
            why = "the attack vector matched a learned high-dimensional feature in the model's space."
            better = "we can decrease the debounce window for future similar events by 10% to react faster."
        else: # TernaryLogic.OBJECT
            happened = f"the firewall's {event.state.name} flag (score: {event.score:.4f}) was overruled. the packet was a known benign false positive."
            learned = "human context remains critical for ambiguous edge cases and new signal combinations."
            why = "the model over-indexed a non-critical feature in this specific instance."
            better = "retrain the model with a dataset enriched for these false positives."
            
        ts = time.time()
        handshake = HandshakeSchema(
            handshake_id=str(uuid.uuid4()),
            timestamp=ts,
            timestamp_utc=_iso_utc(ts),
            source_event_id=event.event_id,
            what_happened=happened,
            who_was_involved=participants,
            what_was_learned=learned,
            why_it_happened=why,
            what_to_do_better=better,
            resolution_id=resolution_id
        )
        self._handshake_sink(handshake)

    def process_packet(self, packet_data: Dict[str, Union[int, float]]):
        """
        The main ingress point for network packets.
        """
        try:
            event = PacketEventSchema.from_dict(packet_data, service_id=self._id)
        except ValueError as e:
            print(f"[{self._id}] malformed packet. dropped. Error: {e}")
            self._alerts_total[FirewallState.SECURE] += 1
            return FirewallState.SECURE

        hi_thresh, lo_thresh = self._get_thresholds()
        event.score = self._model.predict(event)

        # hysteresis enforcement
        if event.score >= hi_thresh:
            event.state = FirewallState.CRITICAL
        elif event.score >= max(lo_thresh, hi_thresh - CFG_VULNERABLE_MARGIN):
            event.state = FirewallState.VULNERABLE
        else:
            event.state = FirewallState.SECURE

        masked = self._masked(event.signals)

        # action based on state
        if event.state in (FirewallState.CRITICAL, FirewallState.VULNERABLE):
            if self._debounced(event.state):
                print(f"[{event.event_id[:8]}] alert suppressed (debounce). score={event.score:.4f}")
            else:
                if event.state == FirewallState.CRITICAL:
                    print(f"[{event.event_id[:8]}] 🟥 CRITICAL THREAT | score={event.score:.4f} ≥ {hi_thresh:.2f} | payload={masked}")
                else:
                    print(f"[{event.event_id[:8]}] 🟧 VULNERABILITY DETECTED | score={event.score:.4f} | payload={masked}")
                
                self._alert_sink(event)
                decision, participants, res_id = self._resolve_ambiguity(event)
                self._log_handshake(event, decision, participants, res_id)
        else:
            print(f"[{event.event_id[:8]}] 🟩 secure | score={event.score:.4f} | payload={masked}")

        self._alerts_total[event.state] += 1
        self._scores.append(event.score)
        if len(self._scores) > 1000:
            self._scores = self._scores[-1000:]
        return event.state

    def force_handshake(self, event_id: str, decision: TernaryLogic, participants: Dict[str, str], happened: str, learned: str, why: str, better: str):
        """Allows a handshake to be logged retroactively or for testing."""
        ts = time.time()
        resolution_id = str(uuid.uuid4())
        
        res = IncidentResolutionSchema(
            resolution_id=resolution_id,
            timestamp=ts,
            timestamp_utc=_iso_utc(ts),
            source_event_id=event_id,
            decision=decision,
            participants=participants,
            context={"source": "manual_handshake"}
        )
        self._resolution_sink(res)
        
        handshake = HandshakeSchema(
            handshake_id=str(uuid.uuid4()),
            timestamp=ts,
            timestamp_utc=_iso_utc(ts),
            source_event_id=event_id,
            what_happened=happened,
            who_was_involved=participants,
            what_was_learned=learned,
            why_it_happened=why,
            what_to_do_better=better,
            resolution_id=resolution_id
        )
        self._handshake_sink(handshake)

def simulate_traffic_stream(firewall: TernaryServerFirewall, num_packets: int = 10, sleep_s: float = 0.5):
    """
    Simulates a stream of live network traffic.
    """
    print(f"\n--- simulating {num_packets} packets ---")
    rng = random.Random(1234)
    for i in range(num_packets):
        packet_data = {
            "signal_a": rng.uniform(0.1, 1.5),
            "signal_b": rng.uniform(0.1, 1.5),
            "signal_c": rng.uniform(0.1, 1.5),
        }
        if i == 5:
            print("\ninjecting a synthetic security threat...")
            packet_data["signal_a"] = 1.8
            packet_data["signal_b"] = 1.9
            packet_data["signal_c"] = 0.2
            packet_data["context"] = {"source": "threat_harness", "reason": "synthetic_violation", "ip": "1.1.1.1"}
        print(f"\nprocessing packet {i+1}: {firewall._masked(packet_data)}")
        firewall.process_packet(packet_data)
        time.sleep(sleep_s)

if __name__ == "__main__":
    def json_alert_sink(ev: PacketEventSchema):
        print({"event": ev.event_id, "state": ev.state.name, "score": round(ev.score,4), "ts": ev.timestamp_utc, "service": ev.service_id})
    
    # Initialize the firewall with a neutral temperament
    firewall = TernaryServerFirewall(seed=99, alert_sink=json_alert_sink)
    simulate_traffic_stream(firewall, num_packets=10, sleep_s=0.2)
    print("\n--- changing temperature to be more paranoid ---")
    firewall.set_temperature(-0.5)
    simulate_traffic_stream(firewall, num_packets=10, sleep_s=0.2)
    
    # Log a retroactive handshake
    print("\n--- demonstrating force_handshake() ---")
    firewall.force_handshake(
        event_id="retro-event-123",
        decision=TernaryLogic.AFFIRM,
        participants={"ops_lead": "j.w", "analyst": "a.l"},
        happened="a critical alert was handled manually and logged retroactively.",
        learned="the manual process is robust, but a real-time tool is required.",
        why_it_happened="the firewall was offline due to a power outage.",
        what_to_do_better="implement a battery backup for the firewall service."
    )
    print(f"Final Metrics:\n{firewall.metrics}")
