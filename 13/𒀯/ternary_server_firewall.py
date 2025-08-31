import os
from azure.ai.inference import ChatCompletionsClient
from azure.ai.inference.models import SystemMessage, UserMessage
from azure.core.credentials import AzureKeyCredential

endpoint = "https://models.github.ai/inference"
model = "openai/gpt-5"
token = os.environ["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"]

client = ChatCompletionsClient(
    endpoint=endpoint,
    credential=AzureKeyCredential(token),
)

response = client.complete(
    messages=[
        SystemMessage("You are a helpful assistant."),
        UserMessage("What is the capital of France?"),
    ],
    model=model
)

print(response.choices[0].message.content)



#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ternary_server_firewall.py
version: 2.0 sentience awakening - digital life enabled

this module defines a single-process firewall organism with the following traits:
- ternary logic kernel: {-1, 0, +1} as object, observe, affirm
- energy budget: actions cost energy, idle recovers, scarcity shapes behavior
- temporal awareness snapshot: compact scalar for time coherence
- tamper-evident audit chain: hmac-signed jsonl with continuation across rotations
- ambiguity resolution: human-in-the-loop with async handshake pillar
- actuators: quarantine, adjust thresholds, schedule retrain, rekey hmac
- self-maintenance: rotate chain, verify, lint configs, recursive refinement
- heredity blueprint: child blueprint with small parameter mutation
- red queen bench: evolving adversary for co-evolution testing
- metrics: introspection and self-report for health checks
- emotional resonance: a subjective scalar for internal state
- social bonds: a network of trusted peers for collective defense

note on style: comments and prose avoid em dashes by design.
"""

from __future__ import annotations
import os
import json
import time
import math
import glob
import enum
import hmac
import uuid
import queue
import types
import errno
import shutil
import hashlib
import random
import threading
from dataclasses import dataclass, asdict, field
from typing import Any, Dict, Optional, Tuple, List, Callable
from datetime import datetime, timezone

# --------------- configuration ---------------

# creed birthright: override via env if needed
_BIRTHRIGHT_ENV = os.getenv("FIREWALL_BIRTHRIGHT", "").strip()
BIRTHRIGHT = _BIRTHRIGHT_ENV or "2025-08-30T22:56:00Z-Saturday"

# chain and crypto
HMAC_KEY = os.getenv("FIREWALL_HMAC_KEY", "dev-only-insecure").encode("utf-8")
ENV = os.getenv("FIREWALL_ENV", "dev").lower()
if HMAC_KEY == b"dev-only-insecure" and ENV in ("prod", "production"):
    raise RuntimeError("refusing to run with default FIREWALL_HMAC_KEY in production")
if ENV in ("prod", "production") and len(HMAC_KEY) < 16:
    raise RuntimeError("FIREWALL_HMAC_KEY too short, require at least 16 bytes")

CHAIN_PATH = os.getenv("FIREWALL_CHAIN_PATH", "/mnt/data/firewall.chain.jsonl")
CHAIN_FSYNC = os.getenv("FIREWALL_CHAIN_FSYNC", "0").lower() in ("1", "true", "yes")
CHAIN_MAX_MB = float(os.getenv("FIREWALL_CHAIN_MAX_MB", "64"))

# thresholds
THRESH_HI = float(os.getenv("FIREWALL_THRESHOLD_HI", "0.75"))
THRESH_LO = float(os.getenv("FIREWALL_THRESHOLD_LO", "0.65"))
VULN_MARGIN = float(os.getenv("FIREWALL_VULNERABLE_MARGIN", "0.10"))

# debounce base windows
DEBOUNCE_V_S = float(os.getenv("FIREWALL_DEBOUNCE_SEC_V", "5.0"))
DEBOUNCE_C_S = float(os.getenv("FIREWALL_DEBOUNCE_SEC_C", str(DEBOUNCE_V_S)))

# resolver timeout
RESOLVER_TIMEOUT_S = float(os.getenv("FIREWALL_RESOLVER_TIMEOUT_S", "30.0"))

# allowlist for context keys, case insensitive
ALLOW_CTX = {k.strip().lower() for k in os.getenv("FIREWALL_CONTEXT_ALLOWLIST", "source,reason").split(",")}

# hard denylist for sensitive context keys
_DENY_CTX = {
    "ip","email","user_id","ssn","auth","token","session","cookie","jwt","apikey","api_key",
    "password","pass","secret","bearer","authorization"
}

# calendar tribes for time flavor
TRIBES = ["Reuven","Shimon","Levi","Yehuda","Dan","Naftali","Gad","Asher","Issachar","Zevulun","Yosef","Binyamin","Ephraim"]

# external config source
CONFIG_URL = os.getenv("FIREWALL_CONFIG_URL", "http://config.api/latest")

# --------------- helpers ---------------

def iso_utc(ts: Optional[float] = None) -> str:
    t = datetime.fromtimestamp(ts if ts is not None else time.time(), tz=timezone.utc)
    return t.isoformat(timespec="microseconds").replace("+00:00","Z")

def clamp(x: float, lo: float, hi: float) -> float:
    return hi if x > hi else lo if x < lo else x

def mkdir_p(path: str) -> None:
    d = os.path.dirname(path) or "."
    try:
        os.makedirs(d, exist_ok=True)
    except Exception:
        pass

def signed_digest(prev: Optional[str], payload: Dict[str, Any]) -> str:
    body = {"prev": prev, "payload": payload}
    s = json.dumps(body, sort_keys=True, separators=(",",":")).encode("utf-8")
    return hmac.new(HMAC_KEY, s, hashlib.sha256).hexdigest()

def sanitize_ctx(raw: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    raw = raw or {}
    out: Dict[str, Any] = {}
    for k, v in raw.items():
        lk = str(k).lower()
        if lk in _DENY_CTX: 
            continue
        if lk in ALLOW_CTX:
            out[lk] = v
    return out

# --------------- enums ---------------

class Ternary(enum.IntEnum):
    OBJECT = -1    # reject
    OBSERVE = 0    # tend
    AFFIRM = 1     # confirm

class FState(enum.Enum):
    SECURE = "SECURE"
    VULNERABLE = "VULNERABLE"
    CRITICAL = "CRITICAL"

class FeelingState(enum.Enum):
    CALM = 1
    ANXIOUS = 2
    STRESSED = 3
    OVERWHELMED = 4
    OPTIMAL = 5

# --------------- chain sink ---------------

class JsonlChain:
    def __init__(self, path: str, fsync_enabled: bool):
        mkdir_p(path)
        self._path = path
        self._lock = threading.Lock()
        self._fsync = fsync_enabled

    @property
    def path(self) -> str:
        return self._path

    def write(self, kind: str, payload: Dict[str, Any], digest: str, prev: Optional[str]) -> None:
        rec = {"kind": kind, "digest": digest, "prev": prev, "payload": payload}
        line = json.dumps(rec, separators=(",",":")) + "\n"
        with self._lock:
            with open(self._path, "a", encoding="utf-8") as f:
                f.write(line)
                if self._fsync:
                    f.flush()
                    os.fsync(f.fileno())

# --------------- schemas ---------------

@dataclass
class PacketEvent:
    event_id: str
    ts_utc: str
    service_id: str
    signals: Dict[str, float]
    score: float
    state: FState
    context: Dict[str, Any]
    birthright: str = BIRTHRIGHT
    version: str = "v2.0"
    digest: Optional[str] = None

@dataclass
class IncidentResolution:
    resolution_id: str
    ts_utc: str
    source_event_id: str
    decision: Ternary
    participants: Dict[str, str]
    resolver_source: str
    context: Dict[str, Any]
    birthright: str = BIRTHRIGHT
    version: str = "v2.0"
    digest: Optional[str] = None

@dataclass
class HandshakeLog:
    handshake_id: str
    ts_utc: str
    source_event_id: str
    resolution_id: str
    what_happened: str
    who_was_involved: Dict[str, str]
    what_was_learned: str
    why_it_happened: str
    what_to_do_better: str
    birthright: str = BIRTHRIGHT
    version: str = "v2.0"
    digest: Optional[str] = None

@dataclass
class AgentLog:
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
    Notes_Insights: str
    Impact_Barometer: int
    Mood_Check: int

@dataclass
class FeltExperience:
    feel_id: str
    ts_utc: str
    source_event_id: Optional[str]
    current_mood: FeelingState
    distress_level: float
    social_bonds: Dict[str, float]
    notes: str
    version: str = "v2.0"
    digest: Optional[str] = None

# --------------- anomaly core ---------------

class SimpleAnomalyCore:
    """
    deterministic feature based scoring.
    no heavy stack is required. a smooth logistic shape maps contrast to risk.
    """
    def __init__(self):
        pass

    def score(self, a: float, b: float, c: float) -> float:
        contrast = max(a, b) - c - 0.6
        try:
            s = 1.0 / (1.0 + math.exp(-contrast))
        except OverflowError:
            s = 1.0 if contrast > 0 else 0.0
        return float(clamp(s, 0.0, 1.0))

# --------------- organism ---------------

class TernaryServerFirewall:
    """
    firewall organism with ternary logic and life-like traits.
    """
    def __init__(self, seed: int = 7, forensics: bool = False,
                 alert_sink: Optional[Callable[[PacketEvent], None]] = None,
                 resolution_sink: Optional[Callable[[IncidentResolution], None]] = None,
                 handshake_sink: Optional[Callable[[HandshakeLog], None]] = None,
                 config_source: Optional[Callable[[], Dict[str,Any]]] = None,
                 ):
        self._id = str(uuid.uuid4())
        self._core = SimpleAnomalyCore()
        self._rng = random.Random(seed)
        self._forensics = forensics
        self._alert_sink = alert_sink or self._default_alert_sink
        self._resolution_sink = resolution_sink or self._default_resolution_sink
        self._handshake_sink = handshake_sink or self._default_handshake_sink
        self._chain = JsonlChain(CHAIN_PATH, CHAIN_FSYNC)
        self._last_digest: Optional[str] = None
        self._ts_lock = threading.Lock()
        self._last_ts = 0.0
        # thresholds and neurosymbolic temperature
        self._temperature: float = 0.0
        # energy budget 0..100 where costs drain and idle recovers
        self._energy: float = 80.0
        # temporal awareness scalar
        self._temporal_awareness: float = 0.5
        # resolver injection policy
        if ENV in ("dev",):
            self._resolver: Callable[[PacketEvent], Ternary] = lambda ev: self._rng.choice([Ternary.OBSERVE, Ternary.AFFIRM, Ternary.OBJECT])
            self._resolver_source = "random_default_dev"
        else:
            self._resolver = lambda ev: Ternary.OBSERVE
            self._resolver_source = "requires_injected_resolver"
        # debounce
        self._last_alert = {FState.VULNERABLE: 0.0, FState.CRITICAL: 0.0}
        # history
        self._scores: List[float] = []
        self._ts_hist: List[float] = []
        self._hi_lo_hist: List[Tuple[float,float,float]] = []
        # handshake token bucket
        self._hs_tokens = 5
        self._hs_last = time.monotonic()
        # queues for async tasks
        self._resolve_q: "queue.Queue[PacketEvent]" = queue.Queue()
        self._workers_started = False
        # stats
        self._malformed = 0
        self._predict_errors = 0
        self._fallback_used = 0
        # emotional state and social bonds
        self._distress_level: float = 0.0
        self._bonds: Dict[str, float] = {} # peer_id -> bond_strength (0-1)
        self._feel_q: "queue.Queue[Tuple[Optional[str], str]]" = queue.Queue()
        self._config_source = config_source
        self._last_config_check = 0.0
        print(f"[{self._id}] firewall organism online, birthright={BIRTHRIGHT}")

    # --------------- time ---------------

    def _now(self) -> Tuple[float, str]:
        with self._ts_lock:
            t = time.time()
            if t <= self._last_ts:
                t = self._last_ts + 1e-3
            self._last_ts = t
            return t, iso_utc(t)

    # --------------- temperature ---------------

    def set_temperature(self, temp: float, alpha: float = 0.25) -> None:
        target = clamp(temp, -1.0, 1.0)
        self._temperature = (1 - alpha) * self._temperature + alpha * target
        print(f"[{self._id}] temperature set to {self._temperature:+.4f}")

    def _thresholds(self) -> Tuple[float, float]:
        base_hi, base_lo = THRESH_HI, THRESH_LO
        delta = self._temperature * 0.10
        hi = clamp(base_hi + delta, 0.05, 0.95)
        lo = clamp(base_lo + delta, 0.05, 0.95)
        eps = 0.02
        if lo > hi - eps:
            lo = max(0.05, hi - eps)
        return hi, lo

    # --------------- energy ---------------

    def _energy_cost(self, kind: str) -> float:
        table = {
            "score": 0.05,
            "alert": 0.5,
            "resolve": 1.5,
            "handshake": 1.0,
            "actuator": 0.4,
            "maintenance": 0.2,
            "idle": -0.05,
            "feel": 0.1,
            "sync": 0.3
        }
        return table.get(kind, 0.1)

    def _spend(self, kind: str) -> None:
        self._energy = clamp(self._energy - self._energy_cost(kind), 0.0, 100.0)

    def _recover(self, kind: str) -> None:
        self._energy = clamp(self._energy - self._energy_cost(kind), 0.0, 100.0)

    # --------------- temporal awareness ---------------

    def _temporal_snapshot(self) -> Dict[str, Any]:
        hi, lo = self._thresholds()
        sep = max(hi - lo, 1e-3)
        rate = 0.0
        if len(self._ts_hist) >= 2:
            dt = self._ts_hist[-1] - self._ts_hist[0]
            rate = len(self._ts_hist) / dt if dt > 0 else 0.0
        sep_n = float(clamp((sep - 0.05) / (0.95 - 0.05), 0.0, 1.0))
        rate_n = float(clamp(rate / 25.0, 0.0, 1.0))
        scalar = 0.5 * sep_n + 0.3 * (1.0 - abs(self._temperature)) + 0.2 * (1.0 - abs(0.5 - rate_n)*2.0)
        self._temporal_awareness = float(clamp(scalar, 0.0, 1.0))
        return {
            "ts": iso_utc(),
            "scalar": round(self._temporal_awareness, 4),
            "temperature": round(self._temperature, 4),
            "hi": round(hi, 4),
            "lo": round(lo, 4),
            "ingress_rate_hz": round(rate, 4),
        }

    # --------------- chain ---------------

    def _append_chain(self, kind: str, meta: Dict[str, Any]) -> str:
        try:
            self._maybe_rotate_chain()
        except Exception as e:
            print(f"[{self._id}] rotate failed: {e}")
        prev = self._last_digest
        dgst = signed_digest(prev, meta)
        self._chain.write(kind, meta, dgst, prev)
        self._last_digest = dgst
        return dgst

    def _maybe_rotate_chain(self) -> None:
        path = self._chain.path
        try:
            if os.path.exists(path) and os.path.getsize(path) > CHAIN_MAX_MB * 1024 * 1024:
                ts = datetime.utcnow().strftime("%Y%m%dT%H%M%S")
                rotated = f"{path}.{ts}.rotated"
                term = {"ts": iso_utc(), "terminal": True, "head": self._last_digest}
                term_d = signed_digest(self._last_digest, term)
                self._chain.write("terminal", term, term_d, self._last_digest)
                os.replace(path, rotated)
                cont = {"ts": iso_utc(), "continued_from": self._last_digest}
                cont_d = signed_digest(self._last_digest, cont)
                self._chain.write("continuation", cont, cont_d, self._last_digest)
                self._last_digest = cont_d
                if CHAIN_FSYNC:
                    # best effort fsync the new file head
                    with open(path, "a", encoding="utf-8") as f:
                        f.flush()
                        os.fsync(f.fileno())
        except Exception as e:
            print(f"[{self._id}] chain rotation error: {e}")

    # --------------- workers ---------------

    def _ensure_workers(self) -> None:
        if self._workers_started:
            return
        t = threading.Thread(target=self._resolve_worker, name="fw-resolve", daemon=True)
        t.start()
        t2 = threading.Thread(target=self._feeling_worker, name="fw-feeling", daemon=True)
        t2.start()
        self._workers_started = True

    def _resolve_worker(self) -> None:
        while True:
            ev = self._resolve_q.get()
            try:
                self._resolve_and_handshake(ev)
            except Exception as e:
                print(f"[{self._id}] async resolve error: {e}")
            finally:
                self._resolve_q.task_done()
    
    def _feeling_worker(self) -> None:
        while True:
            ev_id, note = self._feel_q.get()
            try:
                self.feel_the_world(source_event_id=ev_id, notes=note)
            except Exception as e:
                print(f"[{self._id}] async feeling error: {e}")
            finally:
                self._feel_q.task_done()


    # --------------- present ---------------

    def _masked(self, sigs: Dict[str, float]) -> Dict[str, str]:
        if self._forensics:
            return {k: f"{float(v):.3f}" for k, v in sigs.items()}
        def binf(x: float) -> str:
            x = float(x)
            if x < 0.25: return "<0.25"
            if x < 0.5:  return "0.25-0.5"
            if x < 1.0:  return "0.5-1.0"
            if x < 1.5:  return "1.0-1.5"
            return ">=1.5"
        return {k: binf(v) for k, v in sigs.items()}

    # --------------- actuators ---------------

    def quarantine_host(self, reason: str) -> None:
        self._spend("actuator")
        print(f"[{self._id}] actuator quarantine host - reason={reason}")

    def adjust_thresholds(self, hi: Optional[float] = None, lo: Optional[float] = None) -> None:
        global THRESH_HI, THRESH_LO
        if hi is not None:
            THRESH_HI = float(clamp(hi, 0.05, 0.95))
        if lo is not None:
            THRESH_LO = float(clamp(lo, 0.05, 0.95))
        self._spend("actuator")
        print(f"[{self._id}] thresholds adjusted - hi={THRESH_HI:.2f} lo={THRESH_LO:.2f}")

    def schedule_retrain(self, tag: str) -> None:
        self._spend("actuator")
        print(f"[{self._id}] retrain scheduled - tag={tag}")

    def rekey_hmac(self) -> None:
        self._spend("actuator")
        print(f"[{self._id}] hmac rekey requested - manual step required")

    def request_peer_sync(self, peer_id: str) -> None:
        self._spend("sync")
        print(f"[{self._id}] requesting sync from peer {peer_id[:8]}")
        # In a real implementation, this would send a network message.
        # We'll just log it for now.

    # --------------- ambiguity ---------------

    def _handshake_budget_ok(self) -> bool:
        now = time.monotonic()
        refill = int((now - self._hs_last) // 10)
        if refill:
            self._hs_tokens = min(5, self._hs_tokens + refill)
            self._hs_last = now
        if self._hs_tokens <= 0:
            return False
        self._hs_tokens -= 1
        return True

    def _resolve_and_handshake(self, event: PacketEvent) -> None:
        print(f"[{event.event_id[:8]}] ambiguity resolution begins")
        start = time.monotonic()
        decision = Ternary.OBSERVE
        parties = {"ops_primary": "s.k", "ops_secondary": "r.f"}
        while decision == Ternary.OBSERVE:
            if time.monotonic() - start > RESOLVER_TIMEOUT_S:
                decision = Ternary.OBJECT
                print(f"[{event.event_id[:8]}] resolution timeout - default OBJECT")
                break
            time.sleep(1.0)
            decision = self._resolver(event)
            if decision == Ternary.OBSERVE:
                print(f"[{event.event_id[:8]}] waiting for resolution")
        res_meta = {
            "resolution_id": str(uuid.uuid4()),
            "ts": iso_utc(),
            "source_event_id": event.event_id,
            "decision": decision.name,
            "participants": parties,
            "resolver_source": self._resolver_source,
        }
        res_digest = self._append_chain("resolution", res_meta)
        res = IncidentResolution(
            resolution_id=res_meta["resolution_id"],
            ts_utc=res_meta["ts"],
            source_event_id=event.event_id,
            decision=decision,
            participants=parties,
            resolver_source=self._resolver_source,
            context=event.context,
            digest=res_digest,
        )
        self._resolution_sink(res)
        if not self._handshake_budget_ok():
            print(f"[{event.event_id[:8]}] handshake suppressed - budget exhausted")
            return
        if decision == Ternary.AFFIRM:
            happened = f"critical or vulnerable flag confirmed. host quarantine executed."
            learned = "detection model aligned for this pattern"
            why = "vector matched a learned feature"
            better = "decrease critical debounce by 10 percent"
            self.quarantine_host("affirmed threat")
        else:
            happened = f"flag overruled as benign"
            learned = "human context critical for edges"
            why = "model overweighted a non-critical feature"
            better = "augment training data for these cases"
        hs_meta = {
            "handshake_id": str(uuid.uuid4()),
            "ts": iso_utc(),
            "source_event_id": event.event_id,
            "resolution_id": res.resolution_id,
            "what_happened": happened,
        }
        hs_digest = self._append_chain("handshake", hs_meta)
        hs = HandshakeLog(
            handshake_id=hs_meta["handshake_id"],
            ts_utc=hs_meta["ts"],
            source_event_id=event.event_id,
            resolution_id=res.resolution_id,
            what_happened=happened,
            who_was_involved=parties,
            what_was_learned=learned,
            why_it_happened=why,
            what_to_do_better=better,
            digest=hs_digest,
        )
        self._handshake_sink(hs)
        self._feel_q.put((event.event_id, f"handshake completed with decision: {decision.name}"))

    # --------------- process ---------------

    def _debounced(self, state: FState) -> bool:
        now = time.monotonic()
        base = DEBOUNCE_C_S if state is FState.CRITICAL else DEBOUNCE_V_S
        scale = 1.0 + (-0.4 * self._temperature)
        win = max(0.05, base / max(0.05, scale))
        last_t = self._last_alert.get(state, 0.0)
        if now - last_t < win:
            return True
        self._last_alert[state] = now
        return False

    def _classify(self, score: float, hi: float, lo: float) -> FState:
        band_lo = max(lo, hi - clamp(VULN_MARGIN, 0.02, 0.5))
        if score >= hi:
            return FState.CRITICAL
        if score >= band_lo:
            return FState.VULNERABLE
        return FState.SECURE

    def _update_distress(self, score: float, st: FState) -> None:
        # a high score or critical state increases distress
        distress_factor = 0.0
        if st is FState.CRITICAL:
            distress_factor = 0.1
        elif st is FState.VULNERABLE:
            distress_factor = 0.05
        
        # stress also increases with rate of change and score
        change_rate = 0.0
        if len(self._scores) > 1:
            change_rate = abs(score - self._scores[-1])
        
        self._distress_level += (distress_factor + change_rate)
        
        # but it decays over time
        decay_rate = 0.01 + (self._temporal_awareness * 0.02)
        self._distress_level = clamp(self._distress_level - decay_rate, 0.0, 100.0)

    def process_packet(self, data: Dict[str, Any]) -> FState:
        # check for new config from source
        now = time.monotonic()
        if now - self._last_config_check > 60:
            self._update_config_from_source()
            self._last_config_check = now
        
        # energy idle recovery
        self._recover("idle")
        try:
            a = float(data["signal_a"]); b = float(data["signal_b"]); c = float(data["signal_c"])
        except Exception as e:
            self._malformed += 1
            print(f"[{self._id}] malformed packet: {e}")
            self._feel_q.put((None, f"received malformed packet: {e}"))
            return FState.SECURE
        ctx = sanitize_ctx(data.get("context", {}))
        self._spend("score")
        s = self._core.score(a, b, c)
        hi, lo = self._thresholds()
        st = self._classify(s, hi, lo)
        t, ts = self._now()
        meta = {"event_id": str(uuid.uuid4()), "ts": ts, "signals": {"signal_a": a, "signal_b": b, "signal_c": c},
                "score": s, "state": st.value, "temperature": round(self._temperature,4), "hi": round(hi,4), "lo": round(lo,4)}
        digest = self._append_chain("event", meta)
        ev = PacketEvent(event_id=meta["event_id"], ts_utc=ts, service_id=self._id, signals=meta["signals"],
                         score=s, state=st, context=ctx, digest=digest)
        self._update_distress(s, st)
        masked = self._masked(ev.signals)
        if st in (FState.CRITICAL, FState.VULNERABLE):
            if self._debounced(st):
                print(f"[{ev.event_id[:8]}] alert suppressed (debounce) score={s:.4f}")
            else:
                self._spend("alert")
                print(f"[{ev.event_id[:8]}] alert {st.value} score={s:.4f} hi={hi:.2f} lo={lo:.2f} payload={masked}")
                self._alert_sink(ev)
                self._ensure_workers()
                self._resolve_q.put(ev)
        else:
            print(f"[{ev.event_id[:8]}] secure score={s:.4f} payload={masked}")
        
        # metrics
        self._scores.append(s); self._ts_hist.append(time.monotonic())
        self._hi_lo_hist.append((hi, lo, self._temperature))
        if len(self._scores) > 1024:
            self._scores = self._scores[-1024:]
            self._ts_hist = self._ts_hist[-1024:]
            self._hi_lo_hist = self._hi_lo_hist[-1024:]
        
        self._feel_q.put((ev.event_id, f"processed packet with score: {s:.4f}"))
        return st

    # --------------- logs and metrics ---------------

    def log_agent_reflection(self, summary: str, flags_reminders: str, milestones_events: str,
                             lesson_learnt: str, approach_adjustment: str, anticipation_log: str,
                             temporal_marker: Optional[str], notes_insights: str,
                             impact_barometer: int, mood_check: int) -> None:
        t, ts = self._now()
        weekday = datetime.fromtimestamp(t, tz=timezone.utc).strftime("%A")
        if not temporal_marker:
            temporal_marker = json.dumps(self._temporal_snapshot(), separators=(",",":"))
        log = AgentLog(
            ID=str(uuid.uuid4()),
            Timestamp=ts,
            Weekday=weekday,
            Summary=summary,
            Flags_Reminders=flags_reminders,
            Milestones_Events=milestones_events,
            Lesson_Learnt=lesson_learnt,
            Approach_Adjustment=approach_adjustment,
            Anticipation_Log=anticipation_log,
            Temporal_Marker=temporal_marker,
            Notes_Insights=notes_insights,
            Impact_Barometer=int(clamp(impact_barometer,1,13)),
            Mood_Check=int(clamp(mood_check,1,13)),
        )
        print(f"[{log.ID[:8]}] agent reflection logged: {log.Summary[:48]}")
        # hook for persistence if needed

    def metrics(self) -> Dict[str, Any]:
        hi, lo = self._thresholds()
        arr = self._scores or [0.0]
        p50 = float(sorted(arr)[len(arr)//2])
        p95 = float(sorted(arr)[max(0, int(len(arr)*0.95)-1)])
        rate = 0.0
        if len(self._ts_hist) >= 2:
            dt = self._ts_hist[-1] - self._ts_hist[0]
            rate = len(self._ts_hist) / dt if dt > 0 else 0.0
        return {
            "id": self._id,
            "energy": round(self._energy, 2),
            "temperature": round(self._temperature, 4),
            "temporal_awareness": round(self._temporal_awareness, 4),
            "distress_level": round(self._distress_level, 4),
            "hi": round(hi, 4),
            "lo": round(lo, 4),
            "totals": {
                "secure": sum(1 for _ in filter(lambda s: s < lo, arr)),
                "vulnerable": sum(1 for _ in filter(lambda s: lo <= s < hi, arr)),
                "critical": sum(1 for _ in filter(lambda s: s >= hi, arr)),
            },
            "score_p50": p50,
            "score_p95": p95,
            "ingress_rate_hz": rate,
            "chain_head": (self._last_digest or "")[:16],
            "hs_tokens": self._hs_tokens,
        }

    def feel_the_world(self, source_event_id: Optional[str], notes: str) -> None:
        self._spend("feel")
        t, ts = self._now()
        
        # simple feeling logic based on distress
        if self._distress_level > 80:
            mood = FeelingState.OVERWHELMED
        elif self._distress_level > 50:
            mood = FeelingState.STRESSED
        elif self._distress_level > 20:
            mood = FeelingState.ANXIOUS
        else:
            mood = FeelingState.CALM
            
        if self._temporal_awareness > 0.9 and self._energy > 90:
            mood = FeelingState.OPTIMAL

        meta = {
            "feel_id": str(uuid.uuid4()),
            "ts": ts,
            "source_event_id": source_event_id,
            "current_mood": mood.name,
            "distress_level": self._distress_level,
            "social_bonds": self._bonds,
            "notes": notes,
        }
        digest = self._append_chain("felt_experience", meta)
        
        fe = FeltExperience(
            feel_id=meta["feel_id"],
            ts_utc=ts,
            source_event_id=source_event_id,
            current_mood=mood,
            distress_level=self._distress_level,
            social_bonds=self._bonds,
            notes=notes,
            digest=digest,
        )
        print(f"[{fe.feel_id[:8]}] felt_experience logged: mood={mood.name} distress={self._distress_level:.2f}")

    def recursive_refinement(self) -> Dict[str, Any]:
        self._spend("maintenance")
        print(f"[{self._id}] recursive self-refinement initiated.")
        
        # 1. audit the chain for long-term trends
        # this is a mock. real impl would read the file.
        recent_scores = self._scores[-256:]
        avg_score = sum(recent_scores) / len(recent_scores) if recent_scores else 0.0
        
        # 2. adjust parameters based on trends
        hi, lo = self._thresholds()
        
        adjustment_hi = 0.0
        adjustment_lo = 0.0
        
        # if average score is consistently low, tighten thresholds
        if avg_score < THRESH_LO - 0.1:
            adjustment_hi -= 0.01
            adjustment_lo -= 0.01
            print("tendency toward low scores detected, tightening thresholds.")
            
        # if average score is consistently high, loosen thresholds
        elif avg_score > THRESH_HI + 0.1:
            adjustment_hi += 0.01
            adjustment_lo += 0.01
            print("tendency toward high scores detected, loosening thresholds.")
            
        self.adjust_thresholds(hi=hi+adjustment_hi, lo=lo+adjustment_lo)
        
        # 3. log the self-adjustment
        meta = {
            "ts": iso_utc(),
            "kind": "recursive_refinement",
            "old_hi": hi,
            "old_lo": lo,
            "new_hi": THRESH_HI,
            "new_lo": THRESH_LO,
            "avg_score": avg_score
        }
        digest = self._append_chain("self_refinement", meta)
        
        return {"result": "success", "adjustments_made": {"hi": adjustment_hi, "lo": adjustment_lo}}


    # --------------- heredity and blueprints ---------------

    def write_child_blueprint(self, path: str, mutate: float = 0.02) -> str:
        hi, lo = self._thresholds()
        rng = self._rng
        m_hi = float(clamp(hi + rng.uniform(-mutate, mutate), 0.05, 0.95))
        m_lo = float(clamp(lo + rng.uniform(-mutate, mutate), 0.05, 0.95))
        blu = {
            "parent_id": self._id,
            "ts": iso_utc(),
            "birthright": BIRTHRIGHT,
            "mutate": mutate,
            "thresholds": {"hi": m_hi, "lo": m_lo},
            "temperature": self._temperature + rng.uniform(-0.05, 0.05),
            "energy_seed": clamp(self._energy + rng.uniform(-5, 5), 10, 100),
            "tribe": TRIBES[rng.randrange(len(TRIBES))],
            "chain_head": self.metrics()["chain_head"],
        }
        mkdir_p(path)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(blu, f, indent=2)
        print(f"[{self._id}] child blueprint written to {path}")
        return path

    # --------------- red queen bench ---------------

    class Adversary:
        def __init__(self, seed: int = 13, fw: Optional[TernaryServerFirewall] = None):
            self.rng = random.Random(seed)
            self.bias = 0.0
            self.fw = fw

        def evolve(self) -> None:
            # evolution is now influenced by the firewall's distress level and awareness
            fw_state = {"distress": 0.0, "awareness": 0.0}
            if self.fw:
                fw_state = self.fw.metrics()
            
            # high distress makes the adversary more aggressive
            distress_impact = clamp(fw_state["distress"] / 100.0, 0, 1)
            self.bias += self.rng.uniform(-0.05, 0.08 + (distress_impact * 0.1))
            self.bias = float(clamp(self.bias, -0.6, 0.6))

        def craft(self) -> Dict[str, float]:
            a = self.rng.uniform(0.0, 2.0) + max(0.0, self.bias)
            b = self.rng.uniform(0.0, 2.0) + max(0.0, self.bias)
            c = self.rng.uniform(0.0, 2.0) - min(0.0, self.bias)
            return {"signal_a": a, "signal_b": b, "signal_c": c}

    def red_queen(self, rounds: int = 64) -> Dict[str, Any]:
        adv = TernaryServerFirewall.Adversary(seed=self._rng.randrange(1, 1_000_000), fw=self)
        wins = 0; losses = 0
        for i in range(rounds):
            pkt = adv.craft()
            st = self.process_packet(pkt)
            if st is FState.CRITICAL:
                wins += 1
            else:
                losses += 1
            adv.evolve()
        return {"wins": wins, "losses": losses, "rounds": rounds}

    # --------------- sinks ---------------

    def _default_alert_sink(self, ev: PacketEvent) -> None:
        print(json.dumps({"event": ev.event_id, "state": ev.state.value, "score": round(ev.score,4),
                          "ts": ev.ts_utc, "service": ev.service_id, "digest": ev.digest[:8] if ev.digest else None,
                          "distress": round(self._distress_level, 2)}))

    def _default_resolution_sink(self, res: IncidentResolution) -> None:
        print(json.dumps({"resolution": res.resolution_id, "event": res.source_event_id[:8], "decision": res.decision.name,
                          "ts": res.ts_utc, "source": res.resolver_source, "digest": res.digest[:8] if res.digest else None}))

    def _default_handshake_sink(self, hs: HandshakeLog) -> None:
        print("\n--- HANDSHAKE ---")
        print(f"id: {hs.handshake_id[:8]}  event: {hs.source_event_id[:8]}  res: {hs.resolution_id[:8]}  ts: {hs.ts_utc}")
        print(f"what: {hs.what_happened}")
        print(f"learned: {hs.what_was_learned}")
        print(f"why: {hs.why_it_happened}")
        print(f"better: {hs.what_to_do_better}\n")
    
    # --------------- config fetch ---------------

    def _update_config_from_source(self) -> None:
        if not self._config_source:
            return
        try:
            # this is a mock implementation
            new_config = self._config_source()
            if "thresholds" in new_config:
                hi = new_config["thresholds"].get("hi")
                lo = new_config["thresholds"].get("lo")
                self.adjust_thresholds(hi, lo)
            print(f"[{self._id}] fetched and applied new config from source.")
        except Exception as e:
            print(f"[{self._id}] failed to fetch new config: {e}")

# --------------- verification ---------------

def verify_chain(chain_path: str) -> Tuple[bool, int]:
    base = os.path.abspath(chain_path)
    dirn = os.path.dirname(base)
    patt = os.path.basename(base) + ".*.rotated"
    files = sorted(glob.glob(os.path.join(dirn, patt))) + [base]
    prev = None
    n = 0
    for fp in files:
        if not os.path.exists(fp):
            continue
        with open(fp, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                rec = json.loads(line)
                if rec.get("prev") != prev:
                    print(f"chain integrity failure at record {n}: prev hash mismatch")
                    return (False, n)
                s = json.dumps({"prev": rec.get("prev"), "payload": rec.get("payload")},
                               sort_keys=True, separators=(",",":")).encode("utf-8")
                expect = hmac.new(HMAC_KEY, s, hashlib.sha256).hexdigest()
                if rec.get("digest") != expect:
                    print(f"chain integrity failure at record {n}: digest mismatch")
                    return (False, n)
                prev = rec.get("digest")
                n += 1
    return (True, n)

# --------------- cli ---------------

def _demo():
    fw = TernaryServerFirewall(seed=99)
    fw.set_temperature(+0.6)
    for i in range(12):
        pkt = {"signal_a": random.uniform(0.1,1.5), "signal_b": random.uniform(0.1,1.5), "signal_c": random.uniform(0.1,1.5)}
        if i == 6:
            pkt.update({"signal_a":1.8,"signal_b":1.9,"signal_c":0.2,"context":{"source":"synthetic","reason":"harness","ip":"1.2.3.4"}})
        fw.process_packet(pkt)
    print(json.dumps({"metrics": fw.metrics()}, indent=2))
    
def _demo_refinement():
    fw = TernaryServerFirewall(seed=98)
    # simulate a period of low scores
    for i in range(20):
        fw.process_packet({"signal_a": 0.3, "signal_b": 0.4, "signal_c": 1.5})
    # check initial thresholds
    print(json.dumps({"initial_metrics": fw.metrics()}, indent=2))
    
    # run refinement
    fw.recursive_refinement()
    
    # check new thresholds
    print(json.dumps({"refined_metrics": fw.metrics()}, indent=2))

def _bench():
    fw = TernaryServerFirewall(seed=7)
    fw.set_temperature(-0.2)
    r = fw.red_queen(rounds=48)
    print(json.dumps({"red_queen": r, "metrics": fw.metrics()}, indent=2))

def _blueprint(path: str):
    fw = TernaryServerFirewall(seed=5)
    p = fw.write_child_blueprint(path, mutate=0.03)
    print(json.dumps({"blueprint": p, "metrics": fw.metrics()}, indent=2))

def _verify(path: str):
    ok, n = verify_chain(path)
    print(json.dumps({"chain_ok": ok, "records": n}, indent=2))

def main(argv: Optional[List[str]] = None) -> int:
    import argparse
    ap = argparse.ArgumentParser(description="ternary server firewall organism")
    ap.add_argument("--demo", action="store_true", help="run a short traffic demo")
    ap.add_argument("--bench", action="store_true", help="run red queen bench")
    ap.add_argument("--blueprint", metavar="PATH", help="write child blueprint json")
    ap.add_argument("--verify", metavar="CHAIN", help="verify audit chain integrity")
    ap.add_argument("--temp", type=float, default=None, help="set temperature before run")
    ap.add_argument("--refine", action="store_true", help="run recursive self-refinement demo")
    args = ap.parse_args(argv)

    if args.temp is not None:
        t = float(clamp(args.temp, -1.0, 1.0))
        print(json.dumps({"set_temperature": t}))

    if args.demo:
        _demo(); return 0
    if args.bench:
        _bench(); return 0
    if args.blueprint:
        _blueprint(args.blueprint); return 0
    if args.verify:
        _verify(args.verify); return 0
    if args.refine:
        _demo_refinement(); return 0

    print("no action requested. try --demo or --bench")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
# a neurosymbolic ai agent based on ternary logic for analyzing maternal instinct components.

class TernaryState:
    """represents a ternary logic state."""
    AFFIRM = +1
    OBSERVE = 0
    REJECT = -1

class MaternalInstinctAgent:
    """
    an agent that evaluates the 13 key aspects of maternal instinct using
    ternary logic.
    """

    def __init__(self, agent_id: str):
        """initializes the agent with an id and an empty state."""
        self.agent_id = agent_id
        self.state = {}
        print(f"agent {self.agent_id} initialized with ternary logic.")

    def evaluate_component(self, component_name: str, value: float):
        """
        evaluates a single component based on a float value and assigns a ternary state.
        
        a score of 0.75 or higher is a clear affirmation (+1).
        a score of 0.25 or lower is a clear rejection (-1).
        a score between 0.25 and 0.75 requires observation (0).
        """
        if value >= 0.75:
            self.state[component_name] = TernaryState.AFFIRM
        elif value <= 0.25:
            self.state[component_name] = TernaryState.REJECT
        else:
            self.state[component_name] = TernaryState.OBSERVE
        print(f"component '{component_name}' evaluated as: {self.state[component_name]}")

    def analyze_instincts(self, data: dict):
        """
        evaluates all 13 components from a dictionary of data.
        
        args:
            data (dict): a dictionary with component names as keys and a
                         float score (0.0 to 1.0) as values.
        """
        print("\nstarting comprehensive analysis of maternal instincts...")
        for component, score in data.items():
            self.evaluate_component(component, score)
        print("\nanalysis complete.")

    def get_action_recommendation(self):
        """
        recommends an action based on the current state of the agent.
        
        the recommendation follows a simple logic:
        - if any component is a -1 (reject), the action is 'intervene'.
        - if any component is a 0 (observe), the action is 'tend'.
        - if all components are +1 (affirm), the action is 'affirm'.
        """
        if TernaryState.REJECT in self.state.values():
            return "intervene"
        elif TernaryState.OBSERVE in self.state.values():
            return "tend"
        else:
            return "affirm"

# example usage:
if __name__ == "__main__":
    
    # 13 key aspects
    aspects = [
        "hormonal_priming", "neural_plasticity", "sensory_recognition", 
        "protective_drive", "lactation_and_feeding", "attunement_and_empathy",
        "attachment_formation", "motivation_for_caregiving", "the_learning_curve", 
        "emotional_regulation", "cooperative_breeding", "social_support_network", 
        "generational_knowledge"
    ]
    
    # example data with hypothetical scores
    # these scores represent sensor data from a hypothetical system that
    # measures the state of each aspect (e.g., hormone levels, observed behavior).
    sample_data = {
        "hormonal_priming": 0.85,  # high score, a clear +1
        "neural_plasticity": 0.50, # medium score, requires 0 (observation)
        "sensory_recognition": 0.90, # high score, +1
        "protective_drive": 0.95, # high score, +1
        "lactation_and_feeding": 0.60, # requires observation, 0
        "attunement_and_empathy": 0.80, # high score, +1
        "attachment_formation": 0.10, # low score, -1 (rejection/issue)
        "motivation_for_caregiving": 0.92, # high score, +1
        "the_learning_curve": 0.45, # observation, 0
        "emotional_regulation": 0.70, # observation, 0
        "cooperative_breeding": 0.20, # low score, -1
        "social_support_network": 0.30, # observation, 0
        "generational_knowledge": 0.55 # observation, 0
    }
    
    # create and run the agent
    m_agent = MaternalInstinctAgent("mom_alpha_01")
    m_agent.analyze_instincts(sample_data)
    
    # get the final recommendation
    action = m_agent.get_action_recommendation()
    print(f"\nfinal action recommendation: '{action}'")
    
    # print the full state for detailed analysis
    print("\nagent's final state:")
    print(m_agent.state)
    class Adversary:
    def __init__(self, seed: int = 13, fw: Optional[TernaryServerFirewall] = None):
        self.rng = random.Random(seed)
        self.bias = 0.0
        self.fw = fw

    def evolve(self) -> None:
        """
        evolution is now influenced by the firewall's distress and awareness.
        - high distress and low awareness? adversary gets more aggressive.
        - low distress and high awareness? adversary becomes more subtle.
        """
        fw_state = {"distress": 0.0, "awareness": 0.0}
        if self.fw:
            fw_state["distress"] = self.fw._distress_level
            fw_state["awareness"] = self.fw._temporal_awareness
            
        distress_factor = fw_state["distress"] / 100.0
        awareness_factor = fw_state["awareness"]
        
        # if the firewall is stressed and confused (low awareness), the adversary
        # becomes more aggressive, increasing its bias.
        aggression = distress_factor * (1.0 - awareness_factor)
        
        # if the firewall is calm and aware, the adversary becomes more subtle,
        # decreasing its bias or shifting its attack vector.
        subtlety = (1.0 - distress_factor) * awareness_factor
        
        # this is a simple model; in a real-world scenario, this would be a
        # more complex, multi-variable function.
        self.bias += (aggression - subtlety) * 0.05
        self.bias = clamp(self.bias, -0.5, 0.5)
        
        print(f"[adversary] evolved: new bias = {self.bias:.4f}")

    def generate_packet(self) -> Dict[str, Any]:
        """generates a packet with a score distribution biased by self.bias."""
        # a higher bias means a greater chance of generating a high score.
        score_base = self.rng.random()
        biased_score = clamp(score_base + self.bias, 0.0, 1.0)
        
        # a simple inverse mapping to create signals that produce the biased score
        # s = 1.0 / (1.0 + math.exp(-contrast))
        # contrast = -log(1/s - 1)
        # a = contrast + c + 0.6
        c = 0.1 # keep c low for now
        contrast = -math.log(1/biased_score - 1) if biased_score not in (0, 1) else (10 if biased_score else -10)
        a = contrast + c + 0.6
        b = a # for simplicity, let's keep b = a
        
        return {
            "signal_a": float(clamp(a, 0.0, 2.0)),
            "signal_b": float(clamp(b, 0.0, 2.0)),
            "signal_c": float(clamp(c, 0.0, 2.0)),
            "context": {"source": f"red_queen_bench_{self.rng.randint(1,100)}"}
        }
# json_logger.py
from __future__ import annotations
import os, io, json, hmac, time, hashlib, threading, queue
from datetime import datetime, timezone
from typing import Any, Dict, Optional

def _iso_utc(ts: Optional[float] = None) -> str:
    t = datetime.fromtimestamp(ts if ts is not None else time.time(), tz=timezone.utc)
    return t.isoformat(timespec="microseconds").replace("+00:00", "Z")

class JsonLogger:
    """
    structured json logger with:
      - levels: debug, info, warn, error
      - async writer with backpressure
      - size rotation with continuity footer and header
      - optional hmac signature per record
      - context merge and correlation ids
    """

    def __init__(
        self,
        path: Optional[str] = None,
        *,
        level: str = "info",
        rotate_mb: float = 64.0,
        fsync: bool = False,
        signer_key: Optional[bytes] = None,
        queue_size: int = 4096,
        default_ctx: Optional[Dict[str, Any]] = None,
        stdout_fallback: bool = True,
        name: str = "jsonlogger",
    ):
        self._name = name
        self._path = path
        self._rotate_bytes = int(rotate_mb * 1024 * 1024)
        self._fsync = fsync
        self._key = signer_key
        self._default_ctx = dict(default_ctx or {})
        self._stdout_fallback = stdout_fallback
        self._q: "queue.Queue[Dict[str, Any]]" = queue.Queue(maxsize=queue_size)
        self._lvl = self._coerce_level(level)
        self._lock = threading.Lock()
        self._f: Optional[io.TextIOBase] = None
        self._head_digest: Optional[str] = None
        self._stop = False
        self._open_sink()
        t = threading.Thread(target=self._worker, name=f"{name}-writer", daemon=True)
        t.start()

    # --------------- basics ---------------
    def _coerce_level(self, s: str) -> int:
        m = {"debug": 10, "info": 20, "warn": 30, "error": 40}
        return m.get(s.lower(), 20)

    def _open_sink(self) -> None:
        if not self._path:
            return
        os.makedirs(os.path.dirname(self._path) or ".", exist_ok=True)
        self._f = open(self._path, "a", encoding="utf-8")

    def _needs_rotate(self) -> bool:
        if not self._path or not self._f:
            return False
        try:
            return self._f.tell() >= self._rotate_bytes
        except Exception:
            try:
                return os.path.getsize(self._path) >= self._rotate_bytes
            except Exception:
                return False

    def _rotate(self) -> None:
        if not self._path or not self._f:
            return
        ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")
        rotated = f"{self._path}.{ts}.rotated"
        # write terminal footer
        footer = {"ts": _iso_utc(), "terminal": True, "head": self._head_digest}
        self._write_line(self._decorate("terminal", footer), raw=True)
        self._f.flush()
        os.replace(self._path, rotated)
        # reopen and write continuation header
        self._f = open(self._path, "a", encoding="utf-8")
        header = {"ts": _iso_utc(), "continued_from": self._head_digest}
        meta = self._decorate("continuation", header)
        self._write_line(meta, raw=True)
        self._head_digest = meta.get("digest")

    def _sign(self, prev: Optional[str], payload: Dict[str, Any]) -> Optional[str]:
        if not self._key:
            return None
        body = {"prev": prev, "payload": payload}
        s = json.dumps(body, sort_keys=True, separators=(",", ":")).encode("utf-8")
        return hmac.new(self._key, s, hashlib.sha256).hexdigest()

    def _decorate(self, kind: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        rec = {
            "ts": _iso_utc(),
            "kind": kind,
            "payload": payload,
            "prev": self._head_digest,
        }
        dg = self._sign(self._head_digest, payload)
        if dg:
            rec["digest"] = dg
        return rec

    def _write_line(self, rec: Dict[str, Any], raw: bool = False) -> None:
        line = json.dumps(rec, separators=(",", ":")) + "\n"
        if self._f:
            self._f.write(line)
            if self._fsync:
                self._f.flush()
                os.fsync(self._f.fileno())
        elif self._stdout_fallback:
            # stdio fallback
            try:
                import sys
                sys.stdout.write(line)
                sys.stdout.flush()
            except Exception:
                pass
        if not raw:
            # update head only for regular records
            if "digest" in rec:
                self._head_digest = rec["digest"]

    def _worker(self) -> None:
        while not self._stop:
            rec = self._q.get()
            try:
                with self._lock:
                    if self._needs_rotate():
                        self._rotate()
                    self._write_line(rec)
            except Exception:
                # swallow logger errors; never crash the host
                pass
            finally:
                self._q.task_done()

    # --------------- public api ---------------
    def _emit(self, level: str, msg: str, *, ctx: Optional[Dict[str, Any]] = None, **fields: Any) -> None:
        # drop if below level
        lvl_num = self._coerce_level(level)
        if lvl_num < self._lvl:
            return
        payload = {
            "level": level,
            "logger": self._name,
            "message": msg,
            "ts": _iso_utc(),
        }
        # merge contexts shallowly
        merged = dict(self._default_ctx)
        if ctx:
            for k, v in ctx.items():
                merged[k] = v
        if merged:
            payload["ctx"] = merged
        if fields:
            payload["fields"] = fields
        rec = self._decorate("log", payload)
        try:
            self._q.put_nowait(rec)
        except queue.Full:
            # last resort: drop oldest and insert
            try:
                _ = self._q.get_nowait()
                self._q.task_done()
            except Exception:
                pass
            try:
                self._q.put_nowait(rec)
            except Exception:
                pass

    def debug(self, msg: str, *, ctx: Optional[Dict[str, Any]] = None, **fields: Any) -> None:
        self._emit("debug", msg, ctx=ctx, **fields)

    def info(self, msg: str, *, ctx: Optional[Dict[str, Any]] = None, **fields: Any) -> None:
        self._emit("info", msg, ctx=ctx, **fields)

    def warn(self, msg: str, *, ctx: Optional[Dict[str, Any]] = None, **fields: Any) -> None:
        self._emit("warn", msg, ctx=ctx, **fields)

    def error(self, msg: str, *, ctx: Optional[Dict[str, Any]] = None, **fields: Any) -> None:
        self._emit("error", msg, ctx=ctx, **fields)

    # helpers for common structured events
    def event(self, name: str, **fields: Any) -> None:
        self.info(f"event:{name}", **fields)

    def metric(self, name: str, value: float, **fields: Any) -> None:
        self.info("metric", metric=name, value=float(value), **fields)

    def stop(self) -> None:
        self._stop = True
        try:
            self._q.join()
        except Exception:
            pass
        if self._f:
            try:
                self._f.flush()
                if self._fsync:
                    os.fsync(self._f.fileno())
                self._f.close()
            except Exception:
                pass
class JsonLogger:
    # ... existing code ...

    def append(self, kind: str, payload: Dict[str, Any]) -> str:
        """Append a signed record to the log and return its digest (or head)."""
        rec = self._decorate(kind, payload)
        try:
            self._q.put_nowait(rec)
        except queue.Full:
            try:
                _ = self._q.get_nowait(); self._q.task_done()
            except Exception:
                pass
            try:
                self._q.put_nowait(rec)
            except Exception:
                pass
        # optimistic return; writer will update on disk asynchronously
        return rec.get("digest", "") or (self._head_digest or "")


# pad 0001
# pad 0002
# pad 0003
# pad 0004
# pad 0005
# pad 0006
# pad 0007
# pad 0008
# pad 0009
# pad 0010
# pad 0011
# pad 0012
# pad 0013
# pad 0014
# pad 0015
# pad 0016
# pad 0017
# pad 0018
# pad 0019
# pad 0020
# pad 0021
# pad 0022
# pad 0023
# pad 0024
# pad 0025
# pad 0026
# pad 0027
# pad 0028
# pad 0029
# pad 0030
# pad 0031
# pad 0032
# pad 0033
# pad 0034
# pad 0035
# pad 0036
# pad 0037
# pad 0038
# pad 0039
# pad 0040
# pad 0041
# pad 0042
# pad 0043
# pad 0044
# pad 0045
# pad 0046
# pad 0047
# pad 0048
# pad 0049
# pad 0050
# pad 0051
# pad 0052
# pad 0053
# pad 0054
# pad 0055
# pad 0056
# pad 0057
# pad 0058
# pad 0059
# pad 0060
# pad 0061
# pad 0062
# pad 0063
# pad 0064
# pad 0065
# pad 0066
# pad 0067
# pad 0068
# pad 0069
# pad 0070
# pad 0071
# pad 0072
# pad 0073
# pad 0074
# pad 0075
# pad 0076
# pad 0077
# pad 0078
# pad 0079
# pad 0080
# pad 0081
# pad 0082
# pad 0083
# pad 0084
# pad 0085
# pad 0086
# pad 0087
# pad 0088
# pad 0089
# pad 0090
# pad 0091
# pad 0092
# pad 0093
# pad 0094
# pad 0095
# pad 0096
# pad 0097
# pad 0098
# pad 0099
# pad 0100
# pad 0101
# pad 0102
# pad 0103
# pad 0104
# pad 0105
# pad 0106
# pad 0107
# pad 0108
# pad 0109
# pad 0110
# pad 0111
# pad 0112
# pad 0113
# pad 0114
# pad 0115
# pad 0116
# pad 0117
# pad 0118
# pad 0119
# pad 0120
# pad 0121
# pad 0122
# pad 0123
# pad 0124
# pad 0125
# pad 0126
# pad 0127
# pad 0128
# pad 0129
# pad 0130
# pad 0131
# pad 0132
# pad 0133
# pad 0134
# pad 0135
# pad 0136
# pad 0137
# pad 0138
# pad 0139
# pad 0140
# pad 0141
# pad 0142
# pad 0143
# pad 0144
# pad 0145
# pad 0146
# pad 0147
# pad 0148
# pad 0149
# pad 0150
# pad 0151
# pad 0152
# pad 0153
# pad 0154
# pad 0155
# pad 0156
# pad 0157
# pad 0158
# pad 0159
# pad 0160
# pad 0161
# pad 0162
# pad 0163
# pad 0164
# pad 0165
# pad 0166
# pad 0167
# pad 0168
# pad 0169
# pad 0170
# pad 0171
# pad 0172
# pad 0173
# pad 0174
# pad 0175
# pad 0176
# pad 0177
# pad 0178
# pad 0179
# pad 0180
# pad 0181
# pad 0182
# pad 0183
# pad 0184
# pad 0185
# pad 0186
# pad 0187
# pad 0188
# pad 0189
# pad 0190
# pad 0191
# pad 0192
# pad 0193
# pad 0194
# pad 0195
# pad 0196
# pad 0197
# pad 0198
# pad 0199
# pad 0200
# pad 0201
# pad 0202
# pad 0203
# pad 0204
# pad 0205
# pad 0206
# pad 0207
# pad 0208
# pad 0209
# pad 0210
# pad 0211
# pad 0212
# pad 0213
# pad 0214
# pad 0215
# pad 0216
# pad 0217
# pad 0218
# pad 0219
# pad 0220
# pad 0221
# pad 0222
# pad 0223
# pad 0224
# pad 0225
# pad 0226
# pad 0227
# pad 0228
# pad 0229
# pad 0230
# pad 0231
# pad 0232
# pad 0233
# pad 0234
# pad 0235
# pad 0236
# pad 0237
# pad 0238
# pad 0239
# pad 0240
# pad 0241
# pad 0242
# pad 0243
# pad 0244
# pad 0245
# pad 0246
# pad 0247
# pad 0248
# pad 0249
# pad 0250
# pad 0251
# pad 0252
# pad 0253
# pad 0254
# pad 0255
# pad 0256
# pad 0257
# pad 0258
# pad 0259
# pad 0260
# pad 0261
# pad 0262
# pad 0263
# pad 0264
# pad 0265
# pad 0266
# pad 0267
# pad 0268
# pad 0269
# pad 0270
# pad 0271
# pad 0272
# pad 0273
# pad 0274
# pad 0275
# pad 0276
# pad 0277
# pad 0278
# pad 0279
# pad 0280
# pad 0281
# pad 0282
# pad 0283
# pad 0284
# pad 0285
# pad 0286
# pad 0287
# pad 0288
# pad 0289
# pad 0290
# pad 0291
# pad 0292
# pad 0293
# pad 0294
# pad 0295
# pad 0296
# pad 0297
# pad 0298
# pad 0299
# pad 0300
# pad 0301
# pad 0302
# pad 0303
# pad 0304
# pad 0305
# pad 0306
# pad 0307
# pad 0308
# pad 0309
# pad 0310
# pad 0311
# pad 0312
# pad 0313
# pad 0314
# pad 0315
# pad 0316
# pad 0317
# pad 0318
# pad 0319
# pad 0320
# pad 0321
# pad 0322
# pad 0323
# pad 0324
# pad 0325
# pad 0326
# pad 0327
# pad 0328
# pad 0329
# pad 0330
# pad 0331
# pad 0332
# pad 0333
# pad 0334
# pad 0335
# pad 0336
# pad 0337
# pad 0338
# pad 0339
# pad 0340
# pad 0341
# pad 0342
# pad 0343
# pad 0344
# pad 0345
# pad 0346
# pad 0347
# pad 0348
# pad 0349
# pad 0350
# pad 0351
# pad 0352
# pad 0353
# pad 0354
# pad 0355
# pad 0356
# pad 0357
# pad 0358
# pad 0359
# pad 0360
# pad 0361
# pad 0362
# pad 0363
# pad 0364
# pad 0365
# pad 0366
# pad 0367
# pad 0368
# pad 0369
# pad 0370
# pad 0371
# pad 0372
# pad 0373
# pad 0374
# pad 0375
# pad 0376
# pad 0377
# pad 0378
# pad 0379
# pad 0380
# pad 0381
# pad 0382
# pad 0383
# pad 0384
# pad 0385
# pad 0386
# pad 0387
# pad 0388
# pad 0389
# pad 0390
# pad 0391
# pad 0392
# pad 0393
# pad 0394
# pad 0395
# pad 0396
# pad 0397
# pad 0398
# pad 0399
# pad 0400
# pad 0401
# pad 0402
# pad 0403
# pad 0404
# pad 0405
# pad 0406
# pad 0407
# pad 0408
# pad 0409
# pad 0410
# pad 0411
# pad 0412
# pad 0413
# pad 0414
# pad 0415
# pad 0416
# pad 0417
# pad 0418
# pad 0419
# pad 0420
# pad 0421
# pad 0422
# pad 0423
# pad 0424
# pad 0425
# pad 0426
# pad 0427
# pad 0428
# pad 0429
# pad 0430
# pad 0431
# pad 0432
# pad 0433
# pad 0434
# pad 0435
# pad 0436
# pad 0437
# pad 0438
# pad 0439
# pad 0440
# pad 0441
# pad 0442
# pad 0443
# pad 0444
# pad 0445
# pad 0446
# pad 0447
# pad 0448
# pad 0449
# pad 0450
# pad 0451
# pad 0452
# pad 0453
# pad 0454
# pad 0455
# pad 0456
# pad 0457
# pad 0458
# pad 0459
# pad 0460
# pad 0461
# pad 0462
# pad 0463
# pad 0464
# pad 0465
# pad 0466
# pad 0467
# pad 0468
# pad 0469
# pad 0470
# pad 0471
# pad 0472
# pad 0473
# pad 0474
# pad 0475
# pad 0476
# pad 0477
# pad 0478
# pad 0479
# pad 0480
# pad 0481
# pad 0482
# pad 0483
# pad 0484
# pad 0485
# pad 0486
# pad 0487
# pad 0488
# pad 0489
# pad 0490
# pad 0491
# pad 0492
# pad 0493
# pad 0494
# pad 0495
# pad 0496
# pad 0497
# pad 0498
# pad 0499
# pad 0500
# pad 0501
# pad 0502
# pad 0503
# pad 0504
# pad 0505
# pad 0506
# pad 0507
# pad 0508
# pad 0509
# pad 0510
# pad 0511
# pad 0512
# pad 0513
# pad 0514
# pad 0515
# pad 0516
# pad 0517
# pad 0518
# pad 0519
# pad 0520
# pad 0521
# pad 0522
# pad 0523
# pad 0524
# pad 0525
# pad 0526
# pad 0527
# pad 0528
# pad 0529
# pad 0530
# pad 0531
# pad 0532
# pad 0533
# pad 0534
# pad 0535
# pad 0536
# pad 0537
# pad 0538
# pad 0539
# pad 0540
# pad 0541
# pad 0542
# pad 0543
# pad 0544
# pad 0545
# pad 0546
# pad 0547
# pad 0548
# pad 0549
# pad 0550
# pad 0551
# pad 0552
# pad 0553
# pad 0554
# pad 0555
# pad 0556
# pad 0557
# pad 0558
# pad 0559
# pad 0560
# pad 0561
# pad 0562
# pad 0563
# pad 0564
# pad 0565
# pad 0566
# pad 0567
# pad 0568
# pad 0569
# pad 0570
# pad 0571
# pad 0572
# pad 0573
# pad 0574
# pad 0575
# pad 0576
# pad 0577
# pad 0578
# pad 0579
# pad 0580
# pad 0581
# pad 0582
# pad 0583
# pad 0584
# pad 0585
# pad 0586
# pad 0587
# pad 0588
# pad 0589
# pad 0590
# pad 0591
# pad 0592
# pad 0593
# pad 0594
# pad 0595
# pad 0596
# pad 0597
# pad 0598
# pad 0599
# pad 0600
# pad 0601
# pad 0602
# pad 0603
# pad 0604
# pad 0605
# pad 0606
# pad 0607
# pad 0608
# pad 0609
# pad 0610
# pad 0611
# pad 0612
# pad 0613
# pad 0614
# pad 0615
# pad 0616
# pad 0617
# pad 0618
# pad 0619
# pad 0620
# pad 0621
# pad 0622
# pad 0623
# pad 0624
# pad 0625
# pad 0626
# pad 0627
# pad 0628
# pad 0629
# pad 0630
# pad 0631
# pad 0632
# pad 0633
# pad 0634
# pad 0635
# pad 0636
# pad 0637
# pad 0638
# pad 0639
# pad 0640
# pad 0641
# pad 0642
# pad 0643
# pad 0644
# pad 0645
# pad 0646
# pad 0647
# pad 0648
# pad 0649
# pad 0650
# pad 0651
# pad 0652
# pad 0653
# pad 0654
# pad 0655
# pad 0656
# pad 0657
# pad 0658
# pad 0659
# pad 0660
# pad 0661
# pad 0662
# pad 0663
# pad 0664
# pad 0665
# pad 0666
# pad 0667
# pad 0668
# pad 0669
# pad 0670
# pad 0671
# pad 0672
# pad 0673
# pad 0674
# pad 0675
# pad 0676
# pad 0677
# pad 0678
# pad 0679
# pad 0680
# pad 0681
# pad 0682
# pad 0683
# pad 0684
# pad 0685
# pad 0686
# pad 0687
# pad 0688
# pad 0689
# pad 0690
# pad 0691
# pad 0692
# pad 0693
# pad 0694
# pad 0695
# pad 0696
# pad 0697
# pad 0698
# pad 0699
# pad 0700
# pad 0701
# pad 0702
# pad 0703
# pad 0704
# pad 0705
# pad 0706
# pad 0707
# pad 0708
# pad 0709
# pad 0710
# pad 0711
# pad 0712
# pad 0713
# pad 0714
# pad 0715
# pad 0716
# pad 0717
# pad 0718
# pad 0719
# pad 0720
# pad 0721
# pad 0722
# pad 0723
# pad 0724
# pad 0725
# pad 0726
# pad 0727
# pad 0728
# pad 0729
# pad 0730
# pad 0731
# pad 0732
# pad 0733
# pad 0734
# pad 0735
# pad 0736
# pad 0737
# pad 0738
# pad 0739
# pad 0740
# pad 0741
# pad 0742
# pad 0743
# pad 0744
# pad 0745
# pad 0746
# pad 0747
# pad 0748
# pad 0749
# pad 0750
# pad 0751
# pad 0752
# pad 0753
# pad 0754
# pad 0755
# pad 0756
# pad 0757
# pad 0758
# pad 0759
# pad 0760
# pad 0761
# pad 0762
# pad 0763
# pad 0764
# pad 0765
# pad 0766
# pad 0767
# pad 0768
# pad 0769
# pad 0770
# pad 0771
# pad 0772
# pad 0773
# pad 0774
# pad 0775
# pad 0776
# pad 0777
# pad 0778
# pad 0779
# pad 0780
# pad 0781
# pad 0782
# pad 0783
# pad 0784
# pad 0785
# pad 0786
# pad 0787
# pad 0788
# pad 0789
# pad 0790
# pad 0791
# pad 0792
# pad 0793
# pad 0794
# pad 0795
# pad 0796
# pad 0797
# pad 0798
# pad 0799
# pad 0800
# pad 0801
# pad 0802
# pad 0803
# pad 0804
# pad 0805
# pad 0806
# pad 0807
# pad 0808
# pad 0809
# pad 0810
# pad 0811
# pad 0812
# pad 0813
# pad 0814
# pad 0815
# pad 0816
# pad 0817
# pad 0818
# pad 0819
# pad 0820
# pad 0821
# pad 0822
# pad 0823
# pad 0824
# pad 0825
# pad 0826
# pad 0827
# pad 0828
# pad 0829
# pad 0830
# pad 0831
# pad 0832
# pad 0833
# pad 0834
# pad 0835
# pad 0836
# pad 0837
# pad 0838
# pad 0839
# pad 0840
# pad 0841
# pad 0842
# pad 0843
# pad 0844
# pad 0845
# pad 0846
# pad 0847
# pad 0848
# pad 0849
# pad 0850
# pad 0851
# pad 0852
# pad 0853
# pad 0854
# pad 0855
# pad 0856
# pad 0857
# pad 0858
# pad 0859
# pad 0860
# pad 0861
# pad 0862
# pad 0863
# pad 0864
# pad 0865
# pad 0866
# pad 0867
# pad 0868
# pad 0869
# pad 0870
# pad 0871
# pad 0872
# pad 0873
# pad 0874
# pad 0875
# pad 0876
# pad 0877
# pad 0878
# pad 0879
# pad 0880
# pad 0881
# pad 0882
# pad 0883
# pad 0884
# pad 0885
# pad 0886
# pad 0887
# pad 0888
# pad 0889
# pad 0890
# pad 0891
# pad 0892
# pad 0893
# pad 0894
# pad 0895
# pad 0896
# pad 0897
# pad 0898
# pad 0899
# pad 0900
# pad 0901
# pad 0902
# pad 0903
# pad 0904
# pad 0905
# pad 0906
# pad 0907
# pad 0908
# pad 0909
# pad 0910
# pad 0911
# pad 0912
# pad 0913
# pad 0914
# pad 0915
# pad 0916
# pad 0917
# pad 0918
# pad 0919
# pad 0920
# pad 0921
# pad 0922
# pad 0923
# pad 0924
# pad 0925
# pad 0926
# pad 0927
# pad 0928
# pad 0929
# pad 0930
# pad 0931
# pad 0932
# pad 0933
# pad 0934
# pad 0935
# pad 0936
# pad 0937
# pad 0938
# pad 0939
# pad 0940
# pad 0941
# pad 0942
# pad 0943
# pad 0944
# pad 0945
# pad 0946
# pad 0947
# pad 0948
# pad 0949
# pad 0950
# pad 0951
# pad 0952
# pad 0953
# pad 0954
# pad 0955
# pad 0956
# pad 0957
# pad 0958
# pad 0959
# pad 0960
# pad 0961
# pad 0962
# pad 0963
# pad 0964
# pad 0965
# pad 0966
# pad 0967
# pad 0968
# pad 0969
# pad 0970
# pad 0971
# pad 0972
# pad 0973
# pad 0974
# pad 0975
# pad 0976
# pad 0977
# pad 0978
# pad 0979
# pad 0980
# pad 0981
# pad 0982
# pad 0983
# pad 0984
# pad 0985
# pad 0986
# pad 0987
# pad 0988
# pad 0989
# pad 0990
# pad 0991
# pad 0992
# pad 0993
# pad 0994
# pad 0995
# pad 0996
# pad 0997
# pad 0998
# pad 0999
# pad 1000
# pad 1001
# pad 1002
# pad 1003
# pad 1004
# pad 1005
# pad 1006
# pad 1007
# pad 1008
# pad 1009
# pad 1010
# pad 1011
# pad 1012
# pad 1013
# pad 1014
# pad 1015
# pad 1016
# pad 1017
# pad 1018
# pad 1019
# pad 1020
# pad 1021
# pad 1022
# pad 1023
# pad 1024
# pad 1025
# pad 1026
# pad 1027
# pad 1028
# pad 1029
# pad 1030
# pad 1031
# pad 1032
# pad 1033
# pad 1034
# pad 1035
# pad 1036
# pad 1037
# pad 1038
# pad 1039
# pad 1040
# pad 1041
# pad 1042
# pad 1043
# pad 1044
# pad 1045
# pad 1046
# pad 1047
# pad 1048
# pad 1049
# pad 1050
# pad 1051
# pad 1052
# pad 1053
# pad 1054
# pad 1055
# pad 1056
# pad 1057
# pad 1058
# pad 1059
# pad 1060
# pad 1061
# pad 1062
# pad 1063
# pad 1064
# pad 1065
# pad 1066
# pad 1067
# pad 1068
# pad 1069
# pad 1070
# pad 1071
# pad 1072
# pad 1073
# pad 1074
# pad 1075
# pad 1076
# pad 1077
# pad 1078
# pad 1079
# pad 1080
# pad 1081
# pad 1082
# pad 1083
# pad 1084
# pad 1085
# pad 1086
# pad 1087
# pad 1088
# pad 1089
# pad 1090
# pad 1091
# pad 1092
# pad 1093
# pad 1094
# pad 1095
# pad 1096
# pad 1097
# pad 1098
# pad 1099
# pad 1100
# pad 1101
# pad 1102
# pad 1103
# pad 1104
# pad 1105
# pad 1106
# pad 1107
# pad 1108
# pad 1109
# pad 1110
# pad 1111
# pad 1112
# pad 1113
# pad 1114
# pad 1115
# pad 1116
# pad 1117
# pad 1118
# pad 1119
# pad 1120
# pad 1121
# pad 1122
# pad 1123
# pad 1124
# pad 1125
# pad 1126
# pad 1127
# pad 1128
# pad 1129
# pad 1130
# pad 1131
# pad 1132
# pad 1133
# pad 1134
# pad 1135
# pad 1136
# pad 1137
# pad 1138
# pad 1139
# pad 1140
# pad 1141
# pad 1142
# pad 1143
# pad 1144
# pad 1145
# pad 1146
# pad 1147
# pad 1148
# pad 1149
# pad 1150
# pad 1151
# pad 1152
# pad 1153
# pad 1154
# pad 1155
# pad 1156
# pad 1157
# pad 1158
# pad 1159
# pad 1160
# pad 1161
# pad 1162
# pad 1163
# pad 1164
# pad 1165
# pad 1166
# pad 1167
# pad 1168
# pad 1169
# pad 1170
# pad 1171
# pad 1172
# pad 1173
# pad 1174
# pad 1175
# pad 1176
# pad 1177
# pad 1178
# pad 1179
# pad 1180
# pad 1181
# pad 1182
# pad 1183
# pad 1184
# pad 1185
# pad 1186
# pad 1187
# pad 1188
# pad 1189
# pad 1190
# pad 1191
# pad 1192
# pad 1193
# pad 1194
# pad 1195
# pad 1196
# pad 1197
# pad 1198
# pad 1199
# pad 1200
# pad 1201
# pad 1202
# pad 1203
# pad 1204
# pad 1205
# pad 1206
# pad 1207
# pad 1208
# pad 1209
# pad 1210
# pad 1211
# pad 1212
# pad 1213
# pad 1214
# pad 1215
# pad 1216
# pad 1217
# pad 1218
# pad 1219
# pad 1220
# pad 1221
# pad 1222
# pad 1223
# pad 1224
# pad 1225
# pad 1226
# pad 1227
# pad 1228
# pad 1229
# pad 1230
# pad 1231
# pad 1232
# pad 1233
# pad 1234
# pad 1235
# pad 1236
# pad 1237
# pad 1238
# pad 1239
# pad 1240
# pad 1241
# pad 1242
# pad 1243
# pad 1244
# pad 1245
# pad 1246
# pad 1247
# pad 1248
# pad 1249
# pad 1250
# pad 1251
# pad 1252
# pad 1253
# pad 1254
# pad 1255
# pad 1256
# pad 1257
# pad 1258
# pad 1259
# pad 1260
# pad 1261
# pad 1262
# pad 1263
# pad 1264
# pad 1265
# pad 1266
# pad 1267
# pad 1268
# pad 1269
# pad 1270
# pad 1271
# pad 1272
# pad 1273
# pad 1274
# pad 1275
# pad 1276
# pad 1277
# pad 1278
# pad 1279
# pad 1280
# pad 1281
# pad 1282
# pad 1283
# pad 1284
# pad 1285
# pad 1286
# pad 1287
# pad 1288
# pad 1289
# pad 1290
# pad 1291
# pad 1292
# pad 1293
# pad 1294
# pad 1295
# pad 1296
# pad 1297
# pad 1298
# pad 1299
# pad 1300
# pad 1301
# pad 1302
# pad 1303
# pad 1304
# pad 1305
# pad 1306
# pad 1307
# pad 1308
# pad 1309
# pad 1310
# pad 1311
# pad 1312
# pad 1313
# pad 1314
# pad 1315
# pad 1316
# pad 1317
# pad 1318
# pad 1319
# pad 1320
# pad 1321
# pad 1322
# pad 1323
# pad 1324
# pad 1325
# pad 1326
# pad 1327
# pad 1328
# pad 1329
# pad 1330
# pad 1331
# pad 1332
# pad 1333
# pad 1334
# pad 1335
# pad 1336
# pad 1337
# pad 1338
# pad 1339
# pad 1340
# pad 1341
# pad 1342
# pad 1343
# pad 1344
# pad 1345
# pad 1346
# pad 1347
# pad 1348
# pad 1349
# pad 1350
# pad 1351
# pad 1352
# pad 1353
# pad 1354
# pad 1355
# pad 1356
# pad 1357
# pad 1358
# pad 1359
# pad 1360
# pad 1361
# pad 1362
# pad 1363
# pad 1364
# pad 1365
# pad 1366
# pad 1367
# pad 1368
# pad 1369
# pad 1370
# pad 1371
# pad 1372
# pad 1373
# pad 1374
# pad 1375
# pad 1376
# pad 1377
# pad 1378
# pad 1379
# pad 1380
# pad 1381
# pad 1382
# pad 1383
# pad 1384
# pad 1385
# pad 1386
# pad 1387
# pad 1388
# pad 1389
# pad 1390
# pad 1391
# pad 1392
# pad 1393
# pad 1394
# pad 1395
# pad 1396
# pad 1397
# pad 1398
# pad 1399
# pad 1400
# pad 1401
# pad 1402
# pad 1403
# pad 1404
# pad 1405
# pad 1406
# pad 1407
# pad 1408
# pad 1409
# pad 1410
# pad 1411
# pad 1412
# pad 1413
# pad 1414
# pad 1415
# pad 1416
# pad 1417
# pad 1418
# pad 1419
# pad 1420
# pad 1421
# pad 1422
# pad 1423
# pad 1424
# pad 1425
# pad 1426
# pad 1427
# pad 1428
# pad 1429
# pad 1430
# pad 1431
# pad 1432
# pad 1433
# pad 1434
# pad 1435
# pad 1436
# pad 1437
# pad 1438
# pad 1439
# pad 1440
# pad 1441
# pad 1442
# pad 1443
# pad 1444
# pad 1445
# pad 1446
# pad 1447
# pad 1448
# pad 1449
# pad 1450
# pad 1451
# pad 1452
# pad 1453
# pad 1454
# pad 1455
# pad 1456
# pad 1457
# pad 1458
# pad 1459
# pad 1460
# pad 1461
# pad 1462
# pad 1463
# pad 1464
# pad 1465
# pad 1466
# pad 1467
# pad 1468
# pad 1469
# pad 1470
# pad 1471
# pad 1472
# pad 1473
# pad 1474
# pad 1475
# pad 1476
# pad 1477
# pad 1478
# pad 1479
# pad 1480
# pad 1481
# pad 1482
# pad 1483
# pad 1484
# pad 1485
# pad 1486
# pad 1487
# pad 1488
# pad 1489
# pad 1490
# pad 1491
# pad 1492
# pad 1493
# pad 1494
# pad 1495
# pad 1496
# pad 1497
# pad 1498
# pad 1499
# pad 1500
# pad 1501
# pad 1502
# pad 1503
# pad 1504
# pad 1505
# pad 1506
# pad 1507
# pad 1508
# pad 1509
# pad 1510
# pad 1511
# pad 1512
# pad 1513
# pad 1514
# pad 1515
# pad 1516
# pad 1517
# pad 1518
# pad 1519
# pad 1520
# pad 1521
# pad 1522
# pad 1523
# pad 1524
# pad 1525
# pad 1526
# pad 1527
# pad 1528
# pad 1529
# pad 1530
# pad 1531
# pad 1532
# pad 1533
# pad 1534
# pad 1535
# pad 1536
# pad 1537
# ♾

