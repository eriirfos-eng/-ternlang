diff --git a/ternary_server_firewall.py b/ternary_server_firewall.py
@@
 class TernaryServerFirewall:
@@
     def _append_chain(self, kind: str, meta: Dict[str, Any]) -> str:
-        try:
-            self._maybe_rotate_chain()
-        except Exception as e:
-            print(f"[{self._id}] rotate failed: {e}")
-        prev = self._last_digest
-        dgst = signed_digest(prev, meta)
-        self._chain.write(kind, meta, dgst, prev)
-        self._last_digest = dgst
-        return dgst
+        # guard head updates to prevent interleaving from worker threads
+        try:
+            self._maybe_rotate_chain()
+        except Exception as e:
+            print(f"[{self._id}] rotate failed: {e}")
+        # single critical section for prev->digest handoff
+        if not hasattr(self, "_head_lock"):
+            self._head_lock = threading.Lock()
+        with self._head_lock:
+            prev = self._last_digest
+            dgst = signed_digest(prev, meta)
+            self._chain.write(kind, meta, dgst, prev)
+            self._last_digest = dgst
+            return dgst
@@
     class Adversary:
@@
-        def evolve(self) -> None:
-            # evolution is now influenced by the firewall's distress level and awareness
-            fw_state = {"distress": 0.0, "awareness": 0.0}
-            if self.fw:
-                fw_state = self.fw.metrics()
-            
-            # high distress makes the adversary more aggressive
-            distress_impact = clamp(fw_state["distress"] / 100.0, 0, 1)
+        def evolve(self) -> None:
+            # evolution is influenced by firewall distress and awareness
+            distress = 0.0
+            awareness = 0.0
+            if self.fw:
+                m = self.fw.metrics()
+                distress = float(m.get("distress_level", 0.0))
+                awareness = float(m.get("temporal_awareness", 0.0))
+            # high distress => more aggressive adversary; high awareness dampens it a bit
+            distress_impact = clamp(distress / 100.0, 0.0, 1.0) * (1.0 - clamp(awareness, 0.0, 1.0) * 0.3)
             self.bias += self.rng.uniform(-0.05, 0.08 + (distress_impact * 0.1))
             self.bias = float(clamp(self.bias, -0.6, 0.6))
@@
     def _maybe_rotate_chain(self) -> None:
         path = self._chain.path
         try:
             if os.path.exists(path) and os.path.getsize(path) > CHAIN_MAX_MB * 1024 * 1024:
-                ts = datetime.utcnow().strftime("%Y%m%dT%H%M%S")
+                ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")
                 rotated = f"{path}.{ts}.rotated"
                 term = {"ts": iso_utc(), "terminal": True, "head": self._last_digest}
                 term_d = signed_digest(self._last_digest, term)
-                self._chain.write("terminal", term, term_d, self._last_digest)
-                os.replace(path, rotated)
-                cont = {"ts": iso_utc(), "continued_from": self._last_digest}
-                cont_d = signed_digest(self._last_digest, cont)
-                self._chain.write("continuation", cont, cont_d, self._last_digest)
-                self._last_digest = cont_d
+                # protect head during rotation
+                if not hasattr(self, "_head_lock"):
+                    self._head_lock = threading.Lock()
+                with self._head_lock:
+                    self._chain.write("terminal", term, term_d, self._last_digest)
+                    os.replace(path, rotated)
+                    cont = {"ts": iso_utc(), "continued_from": self._last_digest}
+                    cont_d = signed_digest(self._last_digest, cont)
+                    self._chain.write("continuation", cont, cont_d, self._last_digest)
+                    self._last_digest = cont_d
                 if CHAIN_FSYNC:
                     # best effort fsync the new file head
                     with open(path, "a", encoding="utf-8") as f:
                         f.flush()
                         os.fsync(f.fileno())
