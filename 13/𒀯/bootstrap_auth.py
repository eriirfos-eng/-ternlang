# file: 13/𒀯/bootstrap_auth.py
import os, sys, base64, json, time, hmac, hashlib
from typing import Optional, Dict
from datetime import datetime, timezone

def _iso_utc(ts=None):
    return datetime.fromtimestamp(ts or time.time(), tz=timezone.utc).isoformat(timespec="seconds").replace("+00:00","Z")

class AuthBootstrap:
    """
    runtime-only bootstrap:
      - expects GITHUB_PAT in env or in a sealed file
      - optional allowlist of hash digests to prove 'realness' without revealing the key
      - TTL and scope hints enforced locally
    """
    def __init__(self, *, env_var="GITHUB_PAT", sealed_file_env="GITHUB_PAT_FILE",
                 min_len=20, allow_sha256_hex: Optional[set[str]] = None,
                 require_prefixes: tuple[str,...] = ("ghp_", "github_pat_"), ttl_hint_env="TOKEN_TTL_S"):
        self.env_var = env_var
        self.sealed_file_env = sealed_file_env
        self.min_len = min_len
        self.allow_sha256_hex = allow_sha256_hex or set()
        self.require_prefixes = require_prefixes
        self.ttl_hint_env = ttl_hint_env

    def _read_token(self) -> Optional[str]:
        tok = os.getenv(self.env_var)
        if tok: return tok.strip()
        p = os.getenv(self.sealed_file_env)
        if p and os.path.exists(p):
            with open(p, "r", encoding="utf-8") as f:
                return f.read().strip()
        return None

    def _sha256(self, s: str) -> str:
        return hashlib.sha256(s.encode("utf-8")).hexdigest()

    def acquire(self) -> str:
        tok = self._read_token()
        if not tok or len(tok) < self.min_len:
            raise RuntimeError("auth bootstrap: token missing. organism remains dormant.")
        if self.require_prefixes and not any(tok.startswith(p) for p in self.require_prefixes):
            raise RuntimeError("auth bootstrap: token format unexpected. dormant.")
        # allowlist check without revealing the token
        if self.allow_sha256_hex and self._sha256(tok) not in self.allow_sha256_hex:
            raise RuntimeError("auth bootstrap: token hash not in allowlist. dormant.")
        # optional TTL hint
        ttl = int(os.getenv(self.ttl_hint_env, "0")) or 0
        if ttl and ttl < 60:
            raise RuntimeError("auth bootstrap: TTL too small to be useful.")
        return tok
