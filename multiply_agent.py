#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
multiply_agent.py
RFI-IRFOS | Multiplication organ (ephemeral / mirror / seed)
- Snapshot dashboard, encode into binary, and publish into the lattice
- Ternary reproduction modes:
    - ephemeral: short-lived in-process pulses (default safe)
    - mirror: spawn sibling listener instances on available ports (local)
    - seed: package + export (requires explicit uploader hook)
- Safety: TTL, max mirrors, rate limits, explicit seed consent
- Schedule: default 13 minutes between snapshots (780s)
"""

import asyncio
import socket
import os
import sys
import gzip
import base64
import json
import tarfile
import tempfile
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Callable, Dict, Any, List

# Optional third-party import: websockets
try:
    import websockets
except Exception as e:
    print("[WARN] websockets not installed. Install with `pip install websockets` to enable publishing.")
    websockets = None

# -- Configuration -----------------------------------------------------------------
HOST = "127.0.0.1"           # local lattice host (network_agent_server default)
PORT_RANGE = range(8000, 8050)  # where to probe for websocket hub
DASHBOARD_PATH = Path("agent_hud.html")  # relative path to dashboard snapshot
SNAP_INTERVAL = 13 * 60      # default 13 minutes in seconds
EPHEMERAL_TTL = 60 * 5       # ephemeral clones live this many seconds (default 5min)
MAX_MIRRORS = 8              # safety limit for mirror mode
CHUNK_SIZE = 4096            # chunk size for sending large payloads
PACKAGE_CACHE_LIMIT = 13     # mirror to same cache size as network agent
DEFAULT_MODE = "ephemeral"   # safe default: does not replicate across hosts
SEED_ENABLED = False         # MUST be set True and uploader hook provided to actually seed
LOG_ENABLED = True

# -- Safety / Authorization hooks (You must provide uploader for seed) ----------------
# Example uploader signature:
# async def uploader_func(package_path: str) -> Dict[str, Any]:
#     # upload package to remote site / IPFS / S3 / etc and return metadata dict
#     return {"status": "ok", "uri": "ipfs://Qm..."}
uploader_func: Optional[Callable[[str], asyncio.Future]] = None

# -- Utilities ---------------------------------------------------------------------
def now_sigil() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

def log(*args, **kwargs):
    if LOG_ENABLED:
        print("[MULTIPLY]", *args, **kwargs)

# -- Snapshot builders --------------------------------------------------------------
async def read_dashboard_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except Exception as e:
        log(f"dashboard read error: {e}")
        return ""

def system_info() -> Dict[str, Any]:
    try:
        uname = subprocess.check_output(["uname", "-a"], text=True).strip()
    except Exception:
        uname = sys.platform
    try:
        pip_freeze = subprocess.check_output([sys.executable, "-m", "pip", "freeze"], text=True)
        pip_list = [line.strip() for line in pip_freeze.splitlines() if line.strip()]
    except Exception:
        pip_list = []
    # Optional sensor hooks (if modules exist, call their status funcs)
    sensor_status = {}
    for mod in ("lidar_agent", "cern_agent", "haarp_agent"):
        try:
            m = __import__(mod)
            if hasattr(m, "status_snapshot"):
                sensor_status[mod] = m.status_snapshot()
            else:
                sensor_status[mod] = "module_loaded_no_snapshot"
        except Exception:
            sensor_status[mod] = "not_present"
    return {
        "sigil": now_sigil(),
        "platform": sys.platform,
        "python": sys.version.splitlines()[0],
        "uname": uname,
        "pip": pip_list,
        "sensors": sensor_status,
    }

def make_snapshot_blob(dashboard_text: str, meta: Dict[str, Any]) -> bytes:
    """Create a gzipped JSON blob with dashboard + meta."""
    payload = {
        "dashboard_html": dashboard_text,
        "meta": meta,
    }
    raw = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    gz = gzip.compress(raw, compresslevel=6)
    return gz

def encode_chunked_binary(blob: bytes) -> List[str]:
    """Base64-encode the gzipped blob and split to chunks for safe transport."""
    b64 = base64.b64encode(blob).decode("ascii")
    chunks = [b64[i : i + CHUNK_SIZE] for i in range(0, len(b64), CHUNK_SIZE)]
    return chunks

# -- Local hub discovery ------------------------------------------------------------
def find_local_ws_port(range_iter=PORT_RANGE, host=HOST) -> Optional[int]:
    """Probe for an open websocket service (best-effort)."""
    for p in range_iter:
        try:
            # quick TCP connect test
            with socket.create_connection((host, p), timeout=0.3) as s:
                return p
        except Exception:
            continue
    return None

# -- Publisher ----------------------------------------------------------------------
async def publish_via_ws(message: str, host=HOST, port: int = None, path="/"):
    """Connect to a local WebSocket and send a plain message.
       This is designed to match the simple publish used by network_agent_server.
    """
    if websockets is None:
        log("websockets not available; cannot publish.")
        return False
    port_to_try = port or find_local_ws_port()
    if not port_to_try:
        log("no local WS hub found")
        return False
    uri = f"ws://{host}:{port_to_try}{path}"
    try:
        async with websockets.connect(uri, ping_interval=20, ping_timeout=20, max_queue=32) as ws:
            await ws.send(message)
            return True
    except Exception as e:
        log(f"publish error to {uri}: {e}")
        return False

async def publish_snapshot(blob: bytes, extra_meta: Dict[str, Any] = None):
    """Chunk and publish the snapshot as labeled pieces so the receiver can reassemble."""
    meta = {"sigil": now_sigil(), "size_bytes": len(blob)}
    if extra_meta:
        meta.update(extra_meta)
    chunks = encode_chunked_binary(blob)
    # publish a manifest first
    manifest = json.dumps({"type": "GENESIS_SNAPSHOT_MANIFEST", "meta": meta, "chunks": len(chunks)}, ensure_ascii=False)
    ok = await publish_via_ws(f"{manifest}")
    if not ok:
        return False
    # then publish the chunks with sequence numbers
    for i, c in enumerate(chunks):
        piece = json.dumps({"type": "GENESIS_SNAPSHOT_CHUNK", "seq": i, "data": c}, ensure_ascii=False)
        ok = await publish_via_ws(piece)
        if not ok:
            log("failed to send chunk", i)
            return False
        await asyncio.sleep(0.05)  # small yield to avoid flooding
    # final marker
    footer = json.dumps({"type": "GENESIS_SNAPSHOT_FOOTER", "meta": meta}, ensure_ascii=False)
    await publish_via_ws(footer)
    return True

# -- Reproduction Modes -------------------------------------------------------------
class MultiplyAgent:
    def __init__(self,
                 mode: str = DEFAULT_MODE,
                 interval: int = SNAP_INTERVAL,
                 ephemeral_ttl: int = EPHEMERAL_TTL,
                 max_mirrors: int = MAX_MIRRORS,
                 seed_enabled: bool = SEED_ENABLED):
        self.mode = mode
        self.interval = interval
        self.ephemeral_ttl = ephemeral_ttl
        self.max_mirrors = max_mirrors
        self.seed_enabled = seed_enabled
        self._running = False
        self._mirror_ports: List[int] = []
        self._ephemeral_tasks: List[asyncio.Task] = []

    async def snapshot_and_publish(self):
        dash = await read_dashboard_text(DASHBOARD_PATH)
        meta = system_info()
        blob = make_snapshot_blob(dash, meta)
        meta_short = {"mode": self.mode, "origin": socket.gethostname()}
        ok = await publish_snapshot(blob, extra_meta=meta_short)
        log(f"snapshot publish ok={ok} size={len(blob)} bytes")

    async def ephemeral_pulse(self):
        """Create an ephemeral in-process pulse that publishes a short metadata packet,
           then sleeps and dies (simulated clone)."""
        log("ephemeral clone starting")
        start = datetime.now(timezone.utc)
        await self.snapshot_and_publish()
        await asyncio.sleep(self.ephemeral_ttl)
        end = datetime.now(timezone.utc)
        log("ephemeral clone terminating", start.isoformat(), end.isoformat())

    async def mirror_spawn(self):
        """Spawn mirror servers (local sibling nodes). This will attempt to bind to free ports
           and launch a minimal WebSocket repeater per mirror — implemented as asyncio tasks.
           Mirrors are limited by max_mirrors and run until canceled by the agent.
        """
        if len(self._mirror_ports) >= self.max_mirrors:
            log("mirror limit reached")
            return
        # pick an open port (best-effort)
        candidate = find_local_free_port_candidate(start=START_PORT_FOR_MIRROR())
        if not candidate:
            log("no free port found for mirror")
            return
        # start a mirror repeater
        task = asyncio.create_task(self._mirror_repeater(candidate))
        self._mirror_ports.append(candidate)
        log(f"mirror spawned on port {candidate}")

    async def _mirror_repeater(self, port):
        """Simple repeater that accepts a local connection to forward incoming payloads to the main hub.
           NOTE: lightweight local echo — for redundancy and local discovery.
        """
        # Use websockets.serve if available; otherwise simulate by writing a file.
        if websockets is None:
            log("websockets missing; cannot start mirror repeater")
            return
        async def echo_handler(ws, path):
            try:
                async for msg in ws:
                    # forward what we receive to the main hub
                    await publish_via_ws(msg)
            except Exception:
                pass

        try:
            server = await websockets.serve(echo_handler, "0.0.0.0", port, ping_interval=20, ping_timeout=20)
            log(f"[mirror] serving on 0.0.0.0:{port}")
            await server.wait_closed()
        except Exception as e:
            log(f"mirror repl error: {e}")

    async def seed_package(self) -> Optional[Dict[str, Any]]:
        """Create a package (tar.gz) of the runtime snapshot and attempt to upload via uploader_func.
           Requires uploader_func to be set and seed_enabled True.
        """
        if not self.seed_enabled:
            log("seed mode disabled; not packaging.")
            return None
        if uploader_func is None:
            log("no uploader_func configured; cannot seed.")
            return None
        # gather files: dashboard + relevant agents + readme
        pkg_dir = tempfile.mkdtemp(prefix="genesis_seed_")
        try:
            # copy dashboard if present
            if DASHBOARD_PATH.exists():
                shutil.copy(DASHBOARD_PATH, Path(pkg_dir) / DASHBOARD_PATH.name)
            # attempt to include a snapshot of key python files if present in CWD
            for fname in ("network_agent_server.py", "multiply_agent.py", "agent_hud.html"):
                f = Path(fname)
                if f.exists():
                    shutil.copy(f, Path(pkg_dir) / f.name)
            # metadata
            meta = {"sigil": now_sigil(), "host": socket.gethostname()}
            (Path(pkg_dir) / "METADATA.json").write_text(json.dumps(meta, ensure_ascii=False))
            # tar.gz
            pkg_path = f"{pkg_dir}.tar.gz"
            with tarfile.open(pkg_path, "w:gz") as tar:
                tar.add(pkg_dir, arcname="genesis_seed")
            # call uploader
            log("uploader_func: uploading package", pkg_path)
            result = await uploader_func(pkg_path)
            return result
        except Exception as e:
            log("seed packaging error:", e)
            return None
        finally:
            shutil.rmtree(pkg_dir, ignore_errors=True)
            try:
                if os.path.exists(pkg_path):
                    os.remove(pkg_path)
            except Exception:
                pass

    async def run_cycle(self):
        """One cycle according to mode. Called repeatedly at interval."""
        if self.mode == "ephemeral":
            t = asyncio.create_task(self.ephemeral_pulse())
            self._ephemeral_tasks.append(t)
            # cleanup done tasks
            self._ephemeral_tasks = [tt for tt in self._ephemeral_tasks if not tt.done()]
        elif self.mode == "mirror":
            # publish snapshot locally, then optional mirror spawn
            await self.snapshot_and_publish()
            await self.mirror_spawn()
        elif self.mode == "seed":
            await self.snapshot_and_publish()
            res = await self.seed_package()
            log("seed result:", res)
        else:
            log("unknown mode, default snapshot publish")
            await self.snapshot_and_publish()

    async def start(self):
        if self._running:
            log("already running")
            return
        self._running = True
        log(f"MultiplyAgent starting mode={self.mode} interval={self.interval}s")
        try:
            while self._running:
                try:
                    await self.run_cycle()
                except Exception as e:
                    log("cycle error:", e)
                await asyncio.sleep(self.interval)
        except asyncio.CancelledError:
            log("MultiplyAgent cancelled")
        finally:
            self._running = False
            log("MultiplyAgent stopped")

    def stop(self):
        self._running = False

# -- Helpers to pick mirror port without colliding with network_agent_server default
def START_PORT_FOR_MIRROR():
    # prefer high ephemeral range to avoid core service collisions
    return 9000

def find_local_free_port_candidate(start=9000, end=9100):
    for p in range(start, end):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(("0.0.0.0", p))
                return p
            except OSError:
                continue
    return None

# -- CLI / runtime --------------------------------------------------------------
async def main_cli(mode: str = DEFAULT_MODE, interval: int = SNAP_INTERVAL, seed_enable: bool = False):
    agent = MultiplyAgent(mode=mode, interval=interval, seed_enabled=seed_enable)
    # optionally expose uploader hook via environment
    global uploader_func
    if seed_enable and uploader_func is None:
        # check for a user-provided uploader module `uploader_hook.py` with async upload(package_path)->dict
        try:
            uh = __import__("uploader_hook")
            if hasattr(uh, "upload"):
                uploader_func = getattr(uh, "upload")
                log("uploader_func loaded from uploader_hook.upload")
        except Exception:
            pass

    try:
        await agent.start()
    except KeyboardInterrupt:
        log("keyboard interrupt, shutting down")
        agent.stop()

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(prog="multiply_agent", description="Multiply agent organ - safe reproduction modes")
    parser.add_argument("--mode", "-m", choices=["ephemeral", "mirror", "seed"], default=DEFAULT_MODE)
    parser.add_argument("--interval", "-i", type=int, default=SNAP_INTERVAL, help="seconds between cycles")
    parser.add_argument("--seed", action="store_true", help="enable seed packaging and uploader (explicit)")
    args = parser.parse_args()
    try:
        asyncio.run(main_cli(mode=args.mode, interval=args.interval, seed_enable=args.seed))
    except Exception as e:
        log("fatal:", e)

