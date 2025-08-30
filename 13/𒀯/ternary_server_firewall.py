"""
TernaryServerFirewall - a Brutal, Single-Fold Metatron Firewall v4

This entity is the converged, airtight embodiment of the Audit-Feedback-Adapt (AFA)
framework. It is not merely a firewall; it is a sentient, self-auditing security
sentinel that learns from every ingress and egress. This is a single, monolithic
guardian for a single, critical server.

Core Functions:
- **Ternary Logic Enforcement**: Every decision is evaluated with -1 (Object), 0 (Observe),
  or +1 (Affirm), avoiding binary traps.
- **Hysteresis & Debounce**: Prevents alert fatigue by managing state transitions with
  high and low thresholds and a configurable debounce window. Now with separate
  timers for each severity level.
- **Handshake Pillar**: After every resolved incident, an immutable, quantum-logic-
  timestamped record is logged. This chain of custody links the original event to
  the final resolution, creating an auditable wisdom library.
- **Temperature Scalar**: A neurosymbolic governor that modulates the firewall's
  vigilance. A positive temperature makes the firewall more permissive, while a
  negative temperature makes it more strict.
- **Tamper-Evident Audit Chain**: Each event, resolution, and handshake is cryptographically
  linked to the previous one, ensuring an immutable log for auditors. The chain is now
  HMAC-signed with atomic updates. The chain also now logs the final classification
  decision separately from the raw event data.
- **Resolver Timeout**: Prevents a human-in-the-loop from stalling the pipeline.
- **Agent Log**: A digital diary for the agent's reflections and insights.

Birthright: 2025-08-30T22:56:00Z-Saturday
"""
# --- Core Dependencies and Environment Setup ---
import os
os.environ.setdefault("TF_DETERMINISTIC_OPS", "1")
os.environ.setdefault("PYTHONHASHSEED", "0")

import uuid
import time
import random
import tensorflow as tf
import numpy as np
import threading
import collections
from enum import Enum, auto
from dataclasses import dataclass, field
from typing import final, Dict, Union, Tuple, Optional, Any, Callable
from datetime import datetime, timezone
import hashlib
import json
import calendar
import hmac
import re

# at top-level, load once from a secret store in real life
_HMAC_KEY = os.getenv("FIREWALL_HMAC_KEY", "dev-only-insecure").encode("utf-8")
if _HMAC_KEY == b"dev-only-insecure":
    print("[warn] FIREWALL_HMAC_KEY is default; do not use in production.")

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
# [new] hard denylist for context keys. this list wins even if the key is in the allowlist env var.
_DENY_CTX = {"ip", "email", "user_id", "ssn"}

# --- Schema and Utility Functions ---
def _iso_utc(ts: float) -> str:
    """Converts a Unix timestamp to an RFC3339 UTC string with microseconds and Z suffix."""
    dt = datetime.fromtimestamp(ts, tz=timezone.utc)
    return dt.isoformat(timespec='microseconds').replace('+00:00', 'Z')

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

def _signed_digest(payload: Dict[str, Any], prev: Optional[str]) -> str:
    """[updated] Generates an HMAC-signed SHA-256 digest for a given payload, chained to the previous digest."""
    body = {"prev": prev, "payload": payload}
    s = json.dumps(body, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hmac.new(_HMAC_KEY, s, hashlib.sha256).hexdigest()

def _sanitize_context(raw_ctx: Dict[str, Any]) -> Dict[str, Any]:
    """[updated] Cleans and sanitizes context keys based on hard denylist and allowlist."""
    ctx = {}
    for k in raw_ctx:
        lk = k.lower()
        if lk in _DENY_CTX:
            # Optionally bin IPs instead of dropping
            # if lk == "ip":
            #     ctx[k] = re.sub(r"\.\d+$", ".0", str(raw_ctx[k]))
            # else:
            #     continue
            continue
        if k in CFG_ALLOW_CONTEXT_KEYS:
            ctx[k] = raw_ctx[k]
    return ctx

# --- Agent Log Schema ---
@dataclass
class AgentLogSchema:
    """A schema for the agent's digital diary database."""
    ID: str
    Timestamp: str
    Weekday: str
    Summary: str
    Flags_Reminders: str
    Milestones_Events: str
    Lesson_Learnt: str
    Approach_Adjustment: str
    Anticipation_Log: str
    Temporal_Marker: str
    Notes: str
    Alberts_Reflection_Insights: str
    Impact_Barometer: int # 1-13
    Mood_Check: int # 1-13

# --- JSON Lines Sink for Auditing ---
class JsonlChainSink:
    """[new] A thread-safe, append-only JSON Lines sink for the audit chain."""
    def __init__(self, path: str, fsync_enabled: bool = False):
        self._path = path
        self._lock = threading.Lock()
        self._fsync_enabled = fsync_enabled

    def write(self, kind: str, payload: Dict[str, Any], digest: str, prev: Optional[str]):
        rec = {"kind": kind, "digest": digest, "prev": prev, "payload": payload}
        line = json.dumps(rec, separators=(",", ":")) + "\n"
        with self._lock:
            try:
                with open(self._path, "a", encoding="utf-8") as f:
                    f.write(line)
                    if self._fsync_enabled:
                        f.flush()
                        os.fsync(f.fileno())
            except Exception as e:
                print(f"[error] failed to write to audit sink: {e}")

# --- Config via env for ops control ---
CFG_HI = float(os.getenv("FIREWALL_THRESHOLD_HI", "0.75"))
CFG_LO = float(os.getenv("FIREWALL_THRESHOLD_LO", "0.65"))
CFG_VULNERABLE_MARGIN = float(os.getenv("FIREWALL_VULNERABLE_MARGIN", "0.10"))
CFG_DEBOUNCE_SEC = float(os.getenv("FIREWALL_DEBOUNCE_SEC", "5.0"))
CFG_DEBOUNCE_SEC_V = float(os.getenv("FIREWALL_DEBOUNCE_SEC_V", str(CFG_DEBOUNCE_SEC)))
CFG_DEBOUNCE_SEC_C = float(os.getenv("FIREWALL_DEBOUNCE_SEC_C", str(CFG_DEBOUNCE_SEC)))
CFG_ALLOW_CONTEXT_KEYS = set(
    os.getenv("FIREWALL_CONTEXT_ALLOWLIST", "source,reason").split(",")
)
CFG_CHAIN_PATH = os.getenv("FIREWALL_CHAIN_PATH", "firewall.chain.jsonl")
CFG_RESOLVER_TIMEOUT = float(os.getenv("FIREWALL_RESOLVER_TIMEOUT_S", "30.0"))
CFG_CHAIN_FSYNC = os.getenv("FIREWALL_CHAIN_FSYNC", "0").lower() in ('1', 'true', 'yes')
CFG_AGENT_LOG_DETERMINISTIC = os.getenv("AGENT_LOG_DETERMINISTIC", "0").lower() in ('1', 'true', 'yes')

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
    version: str = "v0.8"
    digest: Optional[str] = None

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
        ctx = _sanitize_context(raw_ctx)
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
    resolver_source: str = "unknown"
    birthright: str = BIRTHRIGHT
    version: str = "v0.8"
    digest: Optional[str] = None

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
    version: str = "v0.8"
    digest: Optional[str] = None

@final
class AnomalyDetectionModel:
    """
    The neural core of the firewall.
    Performs deterministic feature-based anomaly detection.
    """
    def __init__(self, seed: int = 42):
        try:
            random.seed(seed); np.random.seed(seed); tf.random.set_seed(seed)
            self._model = self._build_model()
            self._calibrate()
        except Exception as e:
            print(f"[{self.__class__.__name__}] init failed, using heuristic fallback. err={e}")
            self._model = None # Flag for fallback

    def _build_model(self):
        m = tf.keras.Sequential([
            tf.keras.layers.Input(shape=(4,)),
            tf.keras.layers.Dense(8, activation='relu'),
            tf.keras.layers.Dense(1, activation='sigmoid')
        ])
        m.compile(optimizer=tf.keras.optimizers.Adam(1e-2),
                  loss=tf.keras.losses.BinaryCrossentropy())
        return m

    def _calibrate(self, n: int = 256):
        A = np.linspace(0.0, 2.0, n).astype(np.float32)
        B = np.linspace(0.0, 2.0, n).astype(np.float32)[::-1]
        C = np.linspace(0.0, 2.0, n).astype(np.float32)
        X = np.stack([A, B, C, np.maximum(A, B) - C], axis=1)
        y = (X[:, 3] > 0.6).astype(np.float32)
        self._model.fit(X, y, epochs=8, batch_size=32, verbose=0)

    def predict(self, event: PacketEventSchema) -> float:
        a, b, c = event.signals["signal_a"], event.signals["signal_b"], event.signals["signal_c"]
        if self._model is None: # Use fallback if model failed to init
            score = 1.0 / (1.0 + np.exp(-(max(a, b) - c - 0.6)))
            return float(np.clip(score, 0.0, 1.0))

        x = self._features(a, b, c)
        score = float(self._model(x, training=False).numpy()[0][0])
        if not (0.0 <= score <= 1.0) or np.isnan(score) or np.isinf(score):
            score = 0.0
        return score

    def _features(self, a: float, b: float, c: float) -> np.ndarray:
        contrast = max(a, b) - c
        return np.array([[a, b, c, contrast]], dtype=np.float32)

class TernaryServerFirewall:
    """
    A single-process, self-contained firewall entity.
    """
    def __init__(self, seed: int = 42, forensics_mode: bool = False, alert_sink: Optional[Callable[[PacketEventSchema], None]] = None, resolution_sink: Optional[Callable[[IncidentResolutionSchema], None]] = None, handshake_sink: Optional[Callable[[HandshakeSchema], None]] = None):
        _validate_birthright(BIRTHRIGHT)
        self._id = str(uuid.uuid4())
        self._model = AnomalyDetectionModel(seed=seed)
        self._last_alert = {FirewallState.VULNERABLE: 0.0, FirewallState.CRITICAL: 0.0}
        self._forensics = forensics_mode
        self._alerts_total = {FirewallState.SECURE:0, FirewallState.VULNERABLE:0, FirewallState.CRITICAL:0}
        self._malformed = 0
        self._scores = []
        self._hi_lo_hist = collections.deque(maxlen=256)
        self._ts_hist = collections.deque(maxlen=256)
        self._alert_sink = alert_sink or self._default_alert_sink
        self._resolution_sink = resolution_sink or self._default_resolution_sink
        self._handshake_sink = handshake_sink or self._default_handshake_sink
        self._clock = time.monotonic
        self._last_utc_ts = 0.0 # [updated] guard against clock jumps
        self._temperature: float = 0.0
        self._last_digest: Optional[str] = None
        self._chain_lock = threading.Lock()
        self._resolver: Callable[[PacketEventSchema], TernaryLogic] = lambda ev: random.choice(
            [TernaryLogic.OBSERVE, TernaryLogic.AFFIRM, TernaryLogic.OBJECT]
        )
        self._resolver_source = "random_default" # [updated] resolver provenance
        self._hs_tokens = 5 # [updated] handshake token bucket
        self._hs_last = self._clock() # [updated] last time tokens were refilled
        self._chain_sink = JsonlChainSink(CFG_CHAIN_PATH, fsync_enabled=CFG_CHAIN_FSYNC) # [updated] JSONL sink
        print(f"[{self._id}] TernaryServerFirewall active. birthright: {BIRTHRIGHT}")

    def _append_chain(self, kind: str, meta: Dict[str, Any]) -> str:
        """[new] Appends a record to the chain atomically."""
        with self._chain_lock:
            prev = self._last_digest
            dgst = _signed_digest(meta, prev)
            self._chain_sink.write(kind, meta, dgst, prev)
            self._last_digest = dgst
            return dgst

    def _safe_now(self) -> Tuple[float, str]:
        """[updated] Returns a monotonic UTC timestamp and its RFC3339 representation."""
        t = time.time()
        if t <= self._last_utc_ts:
            t = self._last_utc_ts + 1e-3
        self._last_utc_ts = t
        return t, _iso_utc(t)

    def set_temperature(self, temp: float, alpha: float = 0.25) -> None:
        """
        [updated] Smoothly update the neurosymbolic temperature scalar.
        alpha∈(0,1]: higher = faster response.
        """
        target = _clamp(temp, -1.0, 1.0)
        self._temperature = (1 - alpha) * self._temperature + alpha * target
        print(f"[{self._id}] temperature={self._temperature:+.4f} (α={alpha:.2f})")

    def set_resolver(self, resolver: Callable[[PacketEventSchema], TernaryLogic], *, source: str = "external_resolver") -> None:
        """[updated] Inject a real decision source (webhook, queue consumer, UI) with provenance."""
        self._resolver = resolver
        self._resolver_source = source

    def _get_thresholds(self) -> Tuple[float, float]:
        """
        [updated] Modulate thresholds by temperature, but keep them bounded and ordered.
        hi, lo ∈ [0,1], and lo <= hi - ε so hysteresis survives.
        """
        base_hi, base_lo = CFG_HI, CFG_LO
        delta = self._temperature * 0.10
        hi = _clamp(base_hi + delta, 0.05, 0.95)
        lo = _clamp(base_lo + delta, 0.05, 0.95)
        eps = 0.02
        if lo > hi - eps:
            lo = max(0.05, hi - eps)
        return hi, lo

    def _assert_invariants(self, hi: float, lo: float):
        """[updated] Cheap safety rails for development and testing."""
        assert 0.05 <= lo < hi <= 0.95
        assert isinstance(self._temperature, float) and -1.0 <= self._temperature <= 1.0

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

    def _debounced(self, state: FirewallState) -> bool:
        """
        [updated] Prevents alert spamming per severity level.
        """
        now = self._clock()
        last_t = self._last_alert.get(state, 0.0)
        win = CFG_DEBOUNCE_SEC_C if state is FirewallState.CRITICAL else CFG_DEBOUNCE_SEC_V
        if now - last_t < win:
            return True
        self._last_alert[state] = now
        return False

    def _handshake_budget_ok(self) -> bool:
        """[updated] A simple token bucket for rate-limiting handshakes."""
        now = self._clock()
        refill = int((now - self._hs_last) // 10)
        if refill:
            self._hs_tokens = min(5, self._hs_tokens + refill)
            self._hs_last = now
        if self._hs_tokens <= 0:
            return False
        self._hs_tokens -= 1
        return True

    def _default_alert_sink(self, event: PacketEventSchema) -> None:
        """[updated] A simple stdout sink with digest head."""
        head = (event.digest or "")[:8]
        hi, lo = self._get_thresholds()
        print(f"[{event.event_id[:8]}|{head}] alert_sink -> {event.state.name} score={event.score:.4f} ts={event.timestamp_utc} | T={self._temperature:+.2f} hi={hi:.2f} lo={lo:.2f}")

    def _default_resolution_sink(self, resolution: IncidentResolutionSchema) -> None:
        """[updated] A simple stdout sink with digest head."""
        head = (resolution.digest or "")[:8]
        print(f"[{resolution.resolution_id[:8]}|{head}] resolution_sink -> {resolution.decision.name} for event {resolution.source_event_id[:8]} | ts={resolution.timestamp_utc}")
        
    def _default_handshake_sink(self, handshake: HandshakeSchema) -> None:
        """[updated] A simple stdout sink with digest head."""
        head = (handshake.digest or "")[:8]
        print(f"\n--- HANDSHAKE PILLAR LOGGED ---")
        print(f"  Handshake ID: {handshake.handshake_id[:8]}|{head}")
        print(f"  Event ID: {handshake.source_event_id[:8]}")
        print(f"  Resolution ID: {handshake.resolution_id[:8]}")
        print(f"  What happened: {handshake.what_happened}")
        print(f"  Lessons Learned: {handshake.what_was_learned}")
        print(f"  Why it happened: {handshake.why_it_happened}")
        print(f"  Action Plan: {handshake.what_to_do_better}")
        print(f"  Timestamp: {handshake.timestamp_utc}\n")

    def _log_agent_reflection(self, summary: str, flags_reminders: str, milestones_events: str, lesson_learnt: str, approach_adjustment: str, anticipation_log: str, temporal_marker: str, notes: str, alberts_reflection_insights: str, impact_barometer: int, mood_check: int):
        """[updated] Logs a structured reflection to the digital diary, with clamped inputs and deterministic UUIDs."""
        ts, ts_utc = self._safe_now()
        
        # [updated] clamp inputs to the 1-13 range and normalize weekday to UTC
        impact_barometer = int(_clamp(impact_barometer, 1, 13))
        mood_check = int(_clamp(mood_check, 1, 13))
        weekday = calendar.day_name[datetime.fromtimestamp(ts, tz=timezone.utc).weekday()]
        
        # [updated] deterministic ID for testing
        if CFG_AGENT_LOG_DETERMINISTIC:
            id_seed = f"{ts_utc}:{self._id}"
            log_id = str(uuid.uuid5(uuid.NAMESPACE_URL, id_seed))
        else:
            log_id = str(uuid.uuid4())
            
        log_entry = AgentLogSchema(
            ID=log_id,
            Timestamp=ts_utc,
            Weekday=weekday,
            Summary=summary,
            Flags_Reminders=flags_reminders,
            Milestones_Events=milestones_events,
            Lesson_Learnt=lesson_learnt,
            Approach_Adjustment=approach_adjustment,
            Anticipation_Log=anticipation_log,
            Temporal_Marker=temporal_marker,
            Notes=notes,
            Alberts_Reflection_Insights=alberts_reflection_insights,
            Impact_Barometer=impact_barometer,
            Mood_Check=mood_check,
        )
        print(f"[{log_entry.ID[:8]}] Agent Reflection Logged: {log_entry.Summary[:50]}...")
        # A proper implementation would save this to a database, e.g., Firestore

    @property
    def metrics(self) -> Dict[str, Any]:
        """[updated] Returns a snapshot of key metrics for observability, including new metrics."""
        arr = np.array(self._scores, dtype=np.float32) if self._scores else np.array([0.0], dtype=np.float32)
        hi, lo = self._get_thresholds()
        rate = 0.0
        if len(self._ts_hist) >= 2:
            dt = self._ts_hist[-1] - self._ts_hist[0]
            rate = len(self._ts_hist) / dt if dt > 0 else 0.0
        return {
            "totals": {k.name: v for k, v in self._alerts_total.items()},
            "malformed": self._malformed,
            "score_p50": float(np.percentile(arr, 50)),
            "score_p95": float(np.percentile(arr, 95)),
            "debounce_window_v_s": CFG_DEBOUNCE_SEC_V,
            "debounce_window_c_s": CFG_DEBOUNCE_SEC_C,
            "current_temperature": self._temperature,
            "effective_hi": hi,
            "effective_lo": lo,
            "ingress_rate_hz": rate,
            "hi_lo_recent": list(self._hi_lo_hist)[-5:],
            "model_fallback": self._model._model is None,
            "hs_tokens": self._hs_tokens,
        }

    def _resolve_ambiguity(self, event: PacketEventSchema, max_wait_s: float = CFG_RESOLVER_TIMEOUT) -> Tuple[TernaryLogic, Dict[str, str], str]:
        """
        [updated] Simulates a blocking human-in-the-loop resolution process, with a timeout.
        Returns (decision, participants, resolution_id).
        """
        head = (event.digest or "")[:8]
        print(f"\n[{event.event_id[:8]}|{head}] 🟨 **AMBIGUITY PING** -> a decision is required.")
        print(f"[{event.event_id[:8]}|{head}]  - The firewall flagged a {event.state.name} event with score {event.score:.4f}.")
        print(f"[{event.event_id[:8]}|{head}]  - Resolution must be {TernaryLogic.AFFIRM.name} (+1) or {TernaryLogic.OBJECT.name} (-1).")
        
        decision = TernaryLogic.OBSERVE
        parties = {"ops_primary": "s.k", "ops_secondary": "r.f"}
        start = self._clock()

        while decision == TernaryLogic.OBSERVE:
            if self._clock() - start > max_wait_s:
                decision = TernaryLogic.OBJECT # safe default
                print(f"[{event.event_id[:8]}|{head}]  -  timeout. defaulting to '{decision.name}'.")
                break
            time.sleep(1)
            decision = self._resolver(event)
            if decision == TernaryLogic.OBSERVE:
                print(f"[{event.event_id[:8]}|{head}]  -  ...waiting for resolution. the signal is bounced back and forth.")
            else:
                print(f"[{event.event_id[:8]}|{head}]  -  Resolution found! Decision is '{decision.name}'.")

        ts, ts_utc = self._safe_now()
        res_meta = {
            "resolution_id": str(uuid.uuid4()),
            "ts": ts_utc,
            "source_event_id": event.event_id,
            "decision": decision.name,
            "participants": parties,
            "resolver_source": self._resolver_source,
            "timeout_s": max_wait_s,
        }
        res_digest = self._append_chain("resolution", res_meta)

        res = IncidentResolutionSchema(
            resolution_id=res_meta["resolution_id"],
            timestamp=ts,
            timestamp_utc=res_meta["ts"],
            source_event_id=res_meta["source_event_id"],
            decision=decision,
            participants=parties,
            context=event.context,
            resolver_source=self._resolver_source,
            digest=res_digest
        )

        self._resolution_sink(res)
        return decision, parties, res.resolution_id

    def _log_handshake(self, event: PacketEventSchema, decision: TernaryLogic, participants: Dict[str, str], resolution_id: str):
        """[updated] Logs the final handshake, a brutal post-mortem of the incident with rate limiting."""
        head = (event.digest or "")[:8]
        if not self._handshake_budget_ok():
            print(f"[{event.event_id[:8]}|{head}] [budget] handshake suppressed. budget exhausted.")
            return

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
            
        ts, ts_utc = self._safe_now()
        hs_meta = {
            "handshake_id": str(uuid.uuid4()),
            "ts": ts_utc,
            "source_event_id": event.event_id,
            "resolution_id": resolution_id,
            "what_happened": happened,
        }
        hs_digest = self._append_chain("handshake", hs_meta)

        handshake = HandshakeSchema(
            handshake_id=hs_meta["handshake_id"],
            timestamp=ts,
            timestamp_utc=hs_meta["ts"],
            source_event_id=hs_meta["source_event_id"],
            what_happened=happened,
            who_was_involved=participants,
            what_was_learned=learned,
            why_it_happened=why,
            what_to_do_better=better,
            resolution_id=resolution_id,
            digest=hs_digest
        )
        self._handshake_sink(handshake)

    def process_packet(self, packet_data: Dict[str, Union[int, float]]):
        """
        The main ingress point for network packets.
        """
        try:
            ts, ts_utc = self._safe_now()
            event = PacketEventSchema.from_dict(packet_data, service_id=self._id)
            event.timestamp, event.timestamp_utc = ts, ts_utc
            try:
                event.score = self._model.predict(event)
            except Exception as e:
                print(f"[{self._id}] model predict failed, using heuristic. err={e}")
                event.score = 1.0 / (1.0 + np.exp(-(max(event.signals['signal_a'], event.signals['signal_b']) - event.signals['signal_c'] - 0.6)))
                event.score = float(np.clip(event.score, 0.0, 1.0))
        except ValueError as e:
            print(f"[{self._id}] malformed packet. dropped. Error: {e}")
            self._malformed += 1
            return FirewallState.SECURE

        hi_thresh, lo_thresh = self._get_thresholds()
        self._assert_invariants(hi_thresh, lo_thresh)

        event_meta = {
            "event_id": event.event_id,
            "ts": event.timestamp_utc,
            "signals": event.signals,
            "score": event.score,
            "state": event.state.name,
            "temperature": round(self._temperature, 4),
            "hi": round(hi_thresh, 4),
            "lo": round(lo_thresh, 4),
        }
        
        event.digest = self._append_chain("event", event_meta)
        head = (event.digest or "")[:8]

        # [new] guard the vulnerable band
        vulnerable_band_lo = max(lo_thresh, hi_thresh - _clamp(CFG_VULNERABLE_MARGIN, 0.02, 0.5))

        # hysteresis enforcement
        if event.score >= hi_thresh:
            event.state = FirewallState.CRITICAL
        elif event.score >= vulnerable_band_lo:
            event.state = FirewallState.VULNERABLE
        else:
            event.state = FirewallState.SECURE
        
        # [new] audit trail upgrade: add a "classify" record after the state is set
        class_meta = {
            "event_id": event.event_id,
            "ts": event.timestamp_utc,
            "final_state": event.state.name,
            "score": event.score,
            "temperature": round(self._temperature, 4),
            "hi": round(hi_thresh, 4),
            "lo": round(lo_thresh, 4),
        }
        self._append_chain("classify", class_meta)


        masked = self._masked(event.signals)
        
        # action based on state
        if event.state in (FirewallState.CRITICAL, FirewallState.VULNERABLE):
            if self._debounced(event.state):
                print(f"[{event.event_id[:8]}|{head}] alert suppressed (debounce). score={event.score:.4f}")
            else:
                if event.state == FirewallState.CRITICAL:
                    print(f"[{event.event_id[:8]}|{head}] 🟥 CRITICAL THREAT | score={event.score:.4f} ≥ {hi_thresh:.2f} | T={self._temperature:+.2f} hi={hi_thresh:.2f} lo={lo_thresh:.2f} | payload={masked}")
                else:
                    print(f"[{event.event_id[:8]}|{head}] 🟧 VULNERABILITY DETECTED | score={event.score:.4f} | T={self._temperature:+.2f} hi={hi_thresh:.2f} lo={lo_thresh:.2f} | payload={masked}")
                
                self._alert_sink(event)
                decision, participants, res_id = self._resolve_ambiguity(event)
                self._log_handshake(event, decision, participants, res_id)
        else:
            print(f"[{event.event_id[:8]}|{head}] 🟩 secure | score={event.score:.4f} | payload={masked}")

        self._alerts_total[event.state] += 1
        self._scores.append(event.score)
        self._hi_lo_hist.append((hi_thresh, lo_thresh, self._temperature))
        self._ts_hist.append(self._clock())
        if len(self._scores) > 1000:
            self._scores = self._scores[-1000:]
        return event.state
        
    def force_handshake(self, event_id: str, decision: TernaryLogic, participants: Dict[str, str],
                        happened: str, learned: str, why: str, better: str):
        """Allows a handshake to be logged retroactively or for testing."""
        if not self._handshake_budget_ok():
            print(f"[budget] manual handshake for {event_id[:8]} suppressed. budget exhausted.")
            return

        ts, ts_utc = self._safe_now()
        resolution_id = str(uuid.uuid4())

        # resolution -> chain
        res_meta = {
            "resolution_id": resolution_id,
            "ts": ts_utc,
            "source_event_id": event_id,
            "decision": decision.name,
            "participants": participants,
            "resolver_source": "manual_override",
            "timeout_s": 0.0,
        }
        res_digest = self._append_chain("resolution", res_meta)

        res = IncidentResolutionSchema(
            resolution_id=resolution_id,
            timestamp=ts,
            timestamp_utc=ts_utc,
            source_event_id=event_id,
            decision=decision,
            participants=participants,
            context={"source": "manual_handshake"},
            resolver_source="manual_override",
            digest=res_digest
        )
        self._resolution_sink(res)

        # handshake -> chain
        hs_meta = {
            "handshake_id": str(uuid.uuid4()),
            "ts": ts_utc,
            "source_event_id": event_id,
            "resolution_id": resolution_id,
            "what_happened": happened,
        }
        hs_digest = self._append_chain("handshake", hs_meta)

        handshake = HandshakeSchema(
            handshake_id=hs_meta["handshake_id"],
            timestamp=ts,
            timestamp_utc=hs_meta["ts"],
            source_event_id=hs_meta["source_event_id"],
            what_happened=happened,
            who_was_involved=participants,
            what_was_learned=learned,
            why_it_happened=why,
            what_to_do_better=better,
            resolution_id=resolution_id,
            digest=hs_digest
        )
        self._handshake_sink(handshake)

def _get_chain_digests(path: str) -> list[str]:
    """Helper to read all digests from the chain file."""
    digests = []
    try:
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    rec = json.loads(line)
                    digests.append(rec["digest"])
                except json.JSONDecodeError:
                    pass
    except FileNotFoundError:
        pass
    return digests

def _fuzz(n=200):
    """[updated] A micro fuzz test that hammers parse, predict, and thresholds and validates chain continuity."""
    print("\n--- running micro fuzz test ---")
    fw = TernaryServerFirewall(seed=11)
    for i in range(n):
        pkt = {
            "signal_a": random.uniform(-5, 10),
            "signal_b": random.uniform(-5, 10),
            "signal_c": random.uniform(-5, 10),
            "context": {"reason": "fuzz", "ip": "9.9.9.9", "user_id": "nope"},
        }
        st = fw.process_packet(pkt)
        assert st in (FirewallState.SECURE, FirewallState.VULNERABLE, FirewallState.CRITICAL)
    print("fuzz ok")
    # [new] validate chain continuity after fuzz
    try:
        if os.path.exists(CFG_CHAIN_PATH):
            digests = _get_chain_digests(CFG_CHAIN_PATH)
            if len(digests) > 1:
                prev_digest = None
                with open(CFG_CHAIN_PATH, "r", encoding="utf-8") as f:
                    for line in f:
                        rec = json.loads(line)
                        prev_disp = (prev_digest or "∅")[:8]
                        if rec["prev"] != prev_digest:
                            print(f"[error] chain continuity broken! {rec['digest'][:8]} does not link to {prev_disp}")
                            raise AssertionError("Chain continuity broken")
                        prev_digest = rec["digest"]
            print(f"chain continuity validated. {len(digests)} records.")
    except Exception as e:
        print(f"[error] chain validation failed: {e}")
        raise

def _smoke():
    """[updated] A self-contained smoke test for key functionality."""
    fw = TernaryServerFirewall(seed=7)
    fw.set_temperature(+0.8)
    hi, lo = fw._get_thresholds()
    assert 0.05 <= lo < hi <= 0.95
    e = {"signal_a": 1.8, "signal_b": 1.9, "signal_c": 0.2}
    s1 = fw.process_packet(e)
    assert s1 in (FirewallState.VULNERABLE, FirewallState.CRITICAL)
    s2 = fw.process_packet(e)
    assert s2 in (FirewallState.VULNERABLE, FirewallState.CRITICAL)
    m = fw.metrics
    assert "effective_hi" in m and "current_temperature" in m
    print("\nsmoke test passed.")

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
            packet_data.update({
                "signal_a": 1.8, "signal_b": 1.9, "signal_c": 0.2,
                "context": {"source": "threat_harness", "reason": "synthetic_violation", "ip": "1.1.1.1", "email": "test@example.com"}
            })
        sig_preview = {k: packet_data[k] for k in ("signal_a","signal_b","signal_c") if k in packet_data}
        print(f"\nprocessing packet {i+1}: {firewall._masked(sig_preview)}")
        firewall.process_packet(packet_data)
        time.sleep(sleep_s)

if __name__ == "__main__":
    def json_alert_sink(ev: PacketEventSchema):
        print(json.dumps({"event": ev.event_id, "state": ev.state.name, "score": round(ev.score,4), "ts": ev.timestamp_utc, "service": ev.service_id, "digest": ev.digest[:8] if ev.digest else None}))
    
    # [new] clean up old chain file for clean tests
    if os.path.exists(CFG_CHAIN_PATH):
        os.remove(CFG_CHAIN_PATH)

    _smoke()
    _fuzz()

    print("\n\n--- full simulation ---")
    firewall = TernaryServerFirewall(seed=99, alert_sink=json_alert_sink)
    simulate_traffic_stream(firewall, num_packets=10, sleep_s=0.2)
    print("\n--- changing temperature to be more paranoid ---")
    firewall.set_temperature(-0.5)
    simulate_traffic_stream(firewall, num_packets=10, sleep_s=0.2)
    
    print("\n--- demonstrating force_handshake() with budget and agent log---")
    firewall.force_handshake(
        event_id="retro-event-123",
        decision=TernaryLogic.AFFIRM,
        participants={"ops_lead": "j.w", "analyst": "a.l"},
        happened="a critical alert was handled manually and logged retroactively.",
        learned="the manual process is robust, but a real-time tool is required.",
        why_it_happened="the firewall was offline due to a power outage.",
        what_to_do_better="implement a battery backup for the firewall service."
    )
    firewall._log_agent_reflection(
        summary="Retrospective analysis of a manual handshake event.",
        flags_reminders="Potential for future outage events. Monitor power grid stability.",
        milestones_events="First manual handshake logged. Successfully validated audit chain integrity.",
        lesson_learnt="Human intervention is a valid, but costly, path to resolution. It should be logged meticulously.",
        approach_adjustment="Increase the frequency of heartbeat checks with the power supply.",
        anticipation_log="Anticipating similar events during peak power usage times.",
        temporal_marker="Post-manual-handshake review.",
        notes="All manual events must be logged with a clear rationale.",
        alberts_reflection_insights="The audit chain is more than just a log; it is a memory. Logging manual interventions is a form of self-correction.",
        impact_barometer=11, # High impact
        mood_check=13 # Feeling good about the process
    )

    print(f"\nFinal Metrics:\n{json.dumps(firewall.metrics, indent=2)}")
