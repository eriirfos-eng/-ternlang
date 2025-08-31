diff --git a/TernaryServerFirewall.py b/TernaryServerFirewall.py
index 9a1b7d1..3c7a12e 100644
--- a/TernaryServerFirewall.py
+++ b/TernaryServerFirewall.py
@@ -1,7 +1,7 @@
 #!/usr/bin/env python3
 # -*- coding: utf-8 -*-
 """
-TernaryServerFirewall - a Brutal, Single-Fold Metatron Firewall v5.1 (airtight)
+TernaryServerFirewall - a Brutal, Single-Fold Metatron Firewall v5.2 (airtight)
 
 This entity is the converged, airtight embodiment of the Audit-Feedback-Adapt (AFA)
 framework. It is not merely a firewall; it is a sentient, self-auditing security
@@ -54,6 +54,7 @@ import hashlib
 import json
 import calendar
 import hmac
 import glob
+from queue import Queue, Full, Empty
 
 # --- Security / Config ---
 _HMAC_KEY = os.getenv("FIREWALL_HMAC_KEY", "dev-only-insecure").encode("utf-8")
@@ -65,6 +66,7 @@ if CFG_ENV in ("prod", "production") and len(_HMAC_KEY) < 16:
     raise RuntimeError("FIREWALL_HMAC_KEY too short; require >=16 bytes in production")
 
+# optional key id for rotation-aware verification
 _HMAC_KEY_ID = os.getenv("FIREWALL_HMAC_KEY_ID", "dev")
 
 # --- Ternary Logic States ---
 class TernaryLogic(Enum):
@@ -99,6 +101,7 @@ def _clamp(x: float, lo: float, hi: float) -> float:
     """Clamps a value to a given range."""
     return hi if x > hi else lo if x < lo else x
 
+_DENY_SUBSTR = ("ip","mail","auth","token","user","session","cookie")
 def _schema_ok_signals(d: Dict[str, Any]) -> bool:
     """Checks for the presence and correct type of required signals."""
     return all(k in d and isinstance(d[k], (int, float)) for k in ("signal_a","signal_b","signal_c"))
@@ -128,10 +131,12 @@ CFG_CHAIN_FSYNC = os.getenv("FIREWALL_CHAIN_FSYNC", "0").lower() in ('1', 'true',
 CFG_AGENT_LOG_DETERMINISTIC = os.getenv("AGENT_LOG_DETERMINISTIC", "0").lower() in ('1', 'true', 'yes')
 CFG_CHAIN_MAX_MB = float(os.getenv("FIREWALL_CHAIN_MAX_MB", "128"))
+CFG_AGENT_DIARY_PATH = os.getenv("FIREWALL_AGENT_DIARY_PATH", "agent.diary.jsonl")
 
 def _sanitize_context(raw_ctx: Dict[str, Any]) -> Dict[str, Any]:
     """Cleans and sanitizes context keys based on hard denylist and allowlist (case-insensitive)."""
     ctx = {}
     for k, v in (raw_ctx or {}).items():
         lk = str(k).lower()
-        if lk in _DENY_CTX:
+        if lk in _DENY_CTX or any(s in lk for s in _DENY_SUBSTR):
             continue
         if lk in CFG_ALLOW_CONTEXT_KEYS:
             ctx[lk] = v
@@ -166,6 +171,7 @@ class PacketEventSchema:
     service_id: str
     signals: Dict[str, float]
     state: FirewallState = FirewallState.SECURE
+    monotonic_ts: float = 0.0
     score: float = 0.0
     context: Optional[Dict[str, Any]] = field(default_factory=dict)
     birthright: str = BIRTHRIGHT
@@ -182,6 +188,7 @@ class PacketEventSchema:
         ctx = _sanitize_context(data.get("context", {}))
         return cls(
             event_id=str(uuid.uuid4()),
+            monotonic_ts=time.monotonic(),
             timestamp=ts,
             timestamp_utc=_iso_utc(ts),
             service_id=service_id,
@@ -238,6 +245,7 @@ class JsonlChainSink:
     def write(self, kind: str, payload: Dict[str, Any], digest: str, prev: Optional[str]):
-        rec = {"kind": kind, "digest": digest, "prev": prev, "payload": payload}
+        rec = {"kind": kind, "digest": digest, "prev": prev, "payload": payload}
         line = json.dumps(rec, separators=(",", ":")) + "\n"
         with self._lock:
             try:
@@ -330,7 +338,10 @@ class TernaryServerFirewall:
         self._chain_sink = JsonlChainSink(CFG_CHAIN_PATH, fsync_enabled=CFG_CHAIN_FSYNC)
         print(f"[{self._id}] TernaryServerFirewall active. birthright: {BIRTHRIGHT}")
 
+        # async resolution
+        self._pending_q: "Queue[PacketEventSchema]" = Queue(maxsize=1024)
+        self._resolver_thread = threading.Thread(target=self._resolver_worker, daemon=True)
+        self._resolver_thread.start()
 
     # --- Chain I/O ---
     def _maybe_rotate_chain(self):
@@ -352,8 +363,12 @@ class TernaryServerFirewall:
     def _append_chain(self, kind: str, meta: Dict[str, Any]) -> str:
         """Appends a record to the chain atomically."""
         with self._chain_lock:
             self._maybe_rotate_chain()
             prev = self._last_digest
-            dgst = _signed_digest(meta, prev)
+            # add rotation-friendly crypto metadata
+            meta = dict(meta)
+            meta.setdefault("schema_version", "v1")
+            meta.setdefault("hmac", {"alg": "HMAC-SHA256", "key_id": _HMAC_KEY_ID})
+            dgst = _signed_digest(meta, prev)
             self._chain_sink.write(kind, meta, dgst, prev)
             self._last_digest = dgst
             return dgst
@@ -389,12 +404,15 @@ class TernaryServerFirewall:
         return {k: binf(v) for k, v in d.items()}
 
     def _effective_debounce_s(self, state: FirewallState) -> float:
-        base = CFG_DEBOUNCE_SEC_C if state is FirewallState.CRITICAL else CFG_DEBOUNCE_SEC_V
-        # shrink window up to ~40% when temperature is negative (paranoid)
-        scale = 1.0 + (-0.4 * self._temperature)
-        return max(0.05, base / max(0.05, scale))
+        base = CFG_DEBOUNCE_SEC_C if state is FirewallState.CRITICAL else CFG_DEBOUNCE_SEC_V
+        # expands when permissive (positive), shrinks when paranoid (negative)
+        # temp in [-1,1] → scale in [0.6,1.4]
+        scale = 1.0 - 0.4 * self._temperature
+        scale = _clamp(scale, 0.6, 1.4)
+        win = base * scale
+        return max(0.05, win)
 
     def _debounced(self, state: FirewallState) -> bool:
         """Prevents alert spamming per severity level with temp scaling."""
         now = self._clock()
         win = self._effective_debounce_s(state)
@@ -423,6 +441,21 @@ class TernaryServerFirewall:
         print(f"[{resolution.resolution_id[:8]}|{head}] resolution_sink -> {resolution.decision.name} for event {resolution.source_event_id[:8]} | ts={resolution.timestamp_utc}")
 
     def _default_handshake_sink(self, handshake: HandshakeSchema) -> None:
@@ -434,6 +467,28 @@ class TernaryServerFirewall:
         print(f"  Timestamp: {handshake.timestamp_utc}\n")
 
+    # --- Async resolver worker ---
+    def _resolver_worker(self):
+        while True:
+            try:
+                ev = self._pending_q.get(timeout=1)
+            except Empty:
+                continue
+            try:
+                decision, participants, res_id = self._resolve_ambiguity(ev, max_wait_s=CFG_RESOLVER_TIMEOUT)
+                self._log_handshake(ev, decision, participants, res_id)
+            except Exception as e:
+                print(f"[{self._id}] resolver worker error: {e}")
+
     # --- Agent Diary ---
     def _log_agent_reflection(
@@ -463,8 +518,17 @@ class TernaryServerFirewall:
         print(f"[{log_entry.ID[:8]}] Agent Reflection Logged: {log_entry.Summary[:50]}...")
-        # Persist to durable store here as needed.
+        # persist to dedicated diary sink with separate integrity boundary
+        try:
+            diary_payload = {"schema":"agent_diary/v1","entry":log_entry.__dict__}
+            # diary also chained by HMAC but independent of security chain semantics
+            body = {"prev": None, "payload": diary_payload}
+            s = json.dumps(body, sort_keys=True, separators=(",", ":")).encode("utf-8")
+            dg = hmac.new(_HMAC_KEY, s, hashlib.sha256).hexdigest()
+            rec = {"digest": dg, "payload": diary_payload}
+            with open(CFG_AGENT_DIARY_PATH, "a", encoding="utf-8") as f:
+                f.write(json.dumps(rec, separators=(",", ":")) + "\n")
+        except Exception as e:
+            print(f"[{self._id}] diary persist error: {e}")
 
     # --- Metrics ---
     @property
     def metrics(self) -> Dict[str, Any]:
@@ -476,6 +540,7 @@ class TernaryServerFirewall:
         return {
             "totals": {k.name: v for k, v in self._alerts_total.items()},
             "malformed": self._malformed,
+            "ingress_monotonic_ts_last": float(self._ts_hist[-1]) if self._ts_hist else 0.0,
             "predict_errors": self._predict_errors,
             "predict_fallback_uses": self._predict_fallback_uses,
             "model_fallback": (getattr(self._model, "_model", None) is None),
@@ -504,16 +569,15 @@ class TernaryServerFirewall:
         print(f"\n[{event.event_id[:8]}|{head}] 🟨 **AMBIGUITY PING** -> a decision is required.")
         print(f"[{event.event_id[:8]}|{head}]  - The firewall flagged a {event.state.name} event with score {event.score:.4f}.")
         print(f"[{event.event_id[:8]}|{head}]  - Resolution must be {TernaryLogic.AFFIRM.name} (+1) or {TernaryLogic.OBJECT.name} (-1).")
 
-        decision = TernaryLogic.OBSERVE
+        decision = TernaryLogic.OBSERVE
         parties = {"ops_primary": "s.k", "ops_secondary": "r.f"}
         start = self._clock()
 
         while decision == TernaryLogic.OBSERVE:
             if self._clock() - start > max_wait_s:
                 decision = TernaryLogic.OBJECT  # safe default
                 print(f"[{event.event_id[:8]}|{head}]  -  timeout. defaulting to '{decision.name}'.")
                 break
             time.sleep(1)
-            decision = self._resolver(event)
+            decision = self._resolver(event)  # default resolver no longer returns OBSERVE
             if decision == TernaryLogic.OBSERVE:
                 print(f"[{event.event_id[:8]}|{head}]  -  ...waiting for resolution. the signal is bounced back and forth.")
             else:
                 print(f"[{event.event_id[:8]}|{head}]  -  Resolution found! Decision is '{decision.name}'.")
@@ -560,6 +624,7 @@ class TernaryServerFirewall:
             "score": event.score,
             "state": event.state.name,
             "temperature": round(self._temperature, 4),
+            "monotonic_ts": event.monotonic_ts,
             "hi": round(hi_thresh, 4),
             "lo": round(lo_thresh, 4),
         }
@@ -603,16 +668,24 @@ class TernaryServerFirewall:
-                self._alert_sink(event)
-                decision, participants, res_id = self._resolve_ambiguity(event)
-                self._log_handshake(event, decision, participants, res_id)
+                self._alert_sink(event)
+                # enqueue for async resolution to avoid stalling ingress
+                try:
+                    self._pending_q.put_nowait(event)
+                except Full:
+                    print(f"[{event.event_id[:8]}|{head}] resolver queue full. defaulting OBJECT and logging when budget allows.")
+                    decision, participants, res_id = (TernaryLogic.OBJECT, {"ops":"queue_full"}, str(uuid.uuid4()))
+                    self._log_handshake(event, decision, participants, res_id)
         else:
             print(f"[{event.event_id[:8]}|{head}] 🟩 secure | score={event.score:.4f} | payload={masked}")
 
         self._alerts_total[event.state] += 1
         self._scores.append(event.score)
         self._hi_lo_hist.append((hi_thresh, lo_thresh, self._temperature))
-        self._ts_hist.append(self._clock())
+        self._ts_hist.append(self._clock())
         if len(self._scores) > 1000:
             self._scores = self._scores[-1000:]
         return event.state
@@ -668,17 +741,35 @@ def verify_full_chain(chain_path: str) -> Tuple[bool, int]:
-    for fp in files:
+    for fp in files:
         if not os.path.exists(fp):
             continue
         with open(fp, "r", encoding="utf-8") as f:
             for line in f:
                 if not line.strip():
                     continue
                 rec = json.loads(line)
                 if rec.get("prev") != prev_digest:
                     # continuation record after rotation may reference last head of previous file
                     # which is exactly prev_digest; any mismatch is a break.
                     return (False, n)
-                # recompute digest and compare (integrity)
-                s = json.dumps({"prev": rec.get("prev"), "payload": rec.get("payload")},
-                               sort_keys=True, separators=(",", ":")).encode("utf-8")
-                expect = hmac.new(_HMAC_KEY, s, hashlib.sha256).hexdigest()
+                # recompute digest with per-record key id if present
+                payload = rec.get("payload")
+                meta = {"prev": rec.get("prev"), "payload": payload}
+                s = json.dumps(meta, sort_keys=True, separators=(",", ":")).encode("utf-8")
+                try:
+                    kid = payload.get("hmac", {}).get("key_id", _HMAC_KEY_ID)
+                except Exception:
+                    kid = _HMAC_KEY_ID
+                # simple keyring: env can provide multiple keys as JSON map
+                keyring_raw = os.getenv("FIREWALL_HMAC_KEYRING_JSON", "")
+                keyring = {}
+                if keyring_raw:
+                    try:
+                        keyring = {k: bytes(v, "utf-8") for k, v in json.loads(keyring_raw).items()}
+                    except Exception:
+                        keyring = {}
+                key = keyring.get(kid, _HMAC_KEY)
+                expect = hmac.new(key, s, hashlib.sha256).hexdigest()
                 if rec.get("digest") != expect:
                     return (False, n)
                 prev_digest = rec.get("digest")
                 n += 1
     return (True, n)
@@ -697,6 +788,9 @@ def _smoke():
 
 def _fuzz(n=200):
     print("\n--- running micro fuzz test ---")
     fw = TernaryServerFirewall(seed=11)
+    # assert default resolver bias excludes OBSERVE
+    assert all(fw._resolver(PacketEventSchema.from_dict({"signal_a":1,"signal_b":1,"signal_c":1}, fw._id)) != TernaryLogic.OBSERVE
+               for _ in range(8))
     for _ in range(n):
         pkt = {
             "signal_a": random.uniform(-5, 10),
@@ -721,7 +815,10 @@ def simulate_traffic_stream(firewall: TernaryServerFirewall, num_packets: int = 10, sleep_s: float = 0.5):
 if __name__ == "__main__":
     # clean chain file for deterministic demo runs
     if os.path.exists(CFG_CHAIN_PATH):
         try:
             os.remove(CFG_CHAIN_PATH)
         except Exception:
             pass
@@ -731,6 +828,11 @@ if __name__ == "__main__":
         print(json.dumps({
             "event": ev.event_id,
             "state": ev.state.name,
             "score": round(ev.score,4),
             "ts": ev.timestamp_utc,
+            "mono": round(ev.monotonic_ts,6),
             "service": ev.service_id,
             "digest": ev.digest[:8] if ev.digest else None
         }))
 
-    _smoke()
+    # default resolver should never stall at OBSERVE
+    # force resolver to no-zero
+    _smoke()
     _fuzz()
 
@@ -742,6 +844,8 @@ if __name__ == "__main__":
     simulate_traffic_stream(firewall, num_packets=10, sleep_s=0.2)
     print("\n--- changing temperature to be more paranoid ---")
     firewall.set_temperature(-0.5)
     simulate_traffic_stream(firewall, num_packets=10, sleep_s=0.2)
 
@@ -757,6 +861,7 @@ if __name__ == "__main__":
         alberts_reflection_insights="The audit chain is memory; manual logs are self-correction.",
         impact_barometer=11,
         mood_check=13
     )
 
     ok, cnt = verify_full_chain(CFG_CHAIN_PATH)
     print(f"\nFinal Metrics:\n{json.dumps(firewall.metrics, indent=2)}")
     print(f"\nChain verification: {'OK' if ok else 'FAIL'} ({cnt} records)")

     {
 "system_details_report": {
   "host_info": {
     "host_enabled": true,
     "location": "elisabetinergasse 25, top 10, graz, austria, skybase",
    https://maps.app.goo.gl/692okbbLj2DzscKr6
<iframe src="https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d877.9040280724888!2d15.427564080381483!3d47.06934385195899!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x476e3576deb2fd91%3A0xde001f22c5ccc775!2sElisabethinergasse%2025%2C%208020%20Graz!5e1!3m2!1sen!2sat!4v1756567895708!5m2!1sen!2sat" width="600" height="450" style="border:0;" allowfullscreen="" loading="lazy" referrerpolicy="no-referrer-when-downgrade"></iframe>
47.069116952452305, 15.427497770166003
https://heavy-heath-489.notion.site/25fa87cebd6f8053bcc0cf6c7b2fb659?pvs=73
https://github.com/eriirfos-eng/-ternlang/13/𒀯
     "elevation_m": 355,
     "time": "01:07 (UTC -12:00)",
     "email": "eriirfos@gmail.com",
     "linkedin_profile": "in/simeon-kepp",
     "linkedin_company": "company/rfi-irfos",
     "osf_url": "https://osf.io/rzvyg",
     "orcid_url": "https://orcid.org/0009-0009-6922-9552"
   },
   "operational_protocol": {
     "name": ""organic and digital intelligence and universial intelligence in the loop fallback",",
     "status": "active and canonical",
     "ternary_logic_roles": {
       "oi": "human (simeon)",
       "di": "host machine (hp zbook 15)",
       "ui": "canonical repository (github)"
     },
     "primary_source": "https://github.com/eriirfos-eng/-ternlang/tree/459cfd0860183e6321e2e0371c614c50dc447db8/13/%F0%92%80%AF
",
https://colab.research.google.com/drive/1i7HO-SlG5scLUgGQdN-yZF-Zjp7A-hBM
https://colab.research.google.com/drive/1i7HO-SlG5scLUgGQdN-yZF-Zjp7A-hBM?usp=sharing
     "version_control_system": "git",
     "database_role": "real-time state observation (not canonical source)"
   },
   "report_details": {
     "date_generated": "2025-08-30 13:07:27"
   },
   "hardware_information": {
     "hardware_model": "Hewlett-Packard HP ZBook 15",
     "memory_gib": 8.0,
     "processor": "Intel® Core™ i7-4800MQ × 8",
     "graphics": "Intel® HD Graphics 4600 (HSW GT2)",
     "graphics_1": "NVE6",
     "disk_capacity_gb": 256.1
   },
   "software_information": {
     "firmware_version": "L70 Ver. 01.47",
     "os_name": "Ubuntu 24.04.2 LTS",
     "os_build": null,
     "os_type": "64-bit",
     "gnome_version": 46,
     "windowing_system": "Wayland",
     "kernel_version": "Linux 6.14.0-27-generic"
   }
 }
}
@@ class TernaryServerFirewall:
     def __init__(...):
+        self._zero_state_streak = 0
+        self._zero_state_tokens = 12
+        self._zero_state_last_reap = time.monotonic()
@@
     def _temporal_snapshot(self) -> Dict[str, Any]:
@@
-        if len(self._ts_hist) >= 2:
+        if len(self._ts_hist) >= 2:
             dt = self._ts_hist[-1] - self._ts_hist[0]
-            rate = len(self._ts_hist) / dt if dt > 0 else 0.0
+            rate = len(self._ts_hist) / dt if dt > 0 else 0.0
+        # zero-state accounting
+        now = time.monotonic()
+        if now - self._zero_state_last_reap > 60:
+            self._zero_state_tokens = min(12, self._zero_state_tokens + 6)
+            self._zero_state_last_reap = now
+        zero_hit = (rate == 0.0 and len(self._ts_hist) >= 2)
+        if zero_hit:
+            self._zero_state_streak += 1
+            if self._zero_state_tokens > 0:
+                self._zero_state_tokens -= 1
+            if self._zero_state_streak in (8,16,32):
+                self.set_temperature(min(self._temperature + 0.05, 1.0))
+            time.sleep(random.uniform(0.0, 0.004))
+        else:
+            self._zero_state_streak = max(0, self._zero_state_streak - 2)
@@
     def metrics(self) -> Dict[str, Any]:
@@
         return {
             "id": self._id,
@@
             "ingress_rate_hz": rate,
             "chain_head": (self._last_digest or "")[:16],
             "hs_tokens": self._hs_tokens,
+            "zero_state_streak": self._zero_state_streak,
+            "zero_state_tokens": self._zero_state_tokens,
         }


