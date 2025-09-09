#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RFI-IRFOS Unified Ternary Agent | Civilization Mirror++
Life-Mode Edition v2.1 — stable patch
- Corrected imports (ping_keepalife_agent)
- Graceful fallback if agents not found
- Single asyncio main loop (no shadow conflicts)
"""

import asyncio
import socket
import time
import importlib
from datetime import datetime, UTC
import websockets
try:
    import multiply_agent
except ImportError as e:
    print(f"[WARN] multiply_agent missing: {e}")
    multiply_agent = None

# --- Try to import agents safely ---
logger = None
keepalive_ping = None
start_heartbeat = None

try:
    from ping_keepalife_agent import keepalife_ping
except ImportError as e:
    print(f"[WARN] ping_keepalife_agent missing: {e}")

try:
    from heartbeat_agent import start_heartbeat
except ImportError as e:
    print(f"[WARN] heartbeat_agent missing: {e}")

try:
    from logger_agent import setup_logger
    logger = setup_logger()
except ImportError as e:
    print(f"[WARN] logger_agent missing: {e}")

if logger:
    logger.info("Unified Ternary Agent booting...")

# --- Config ---
HOST = "0.0.0.0"
START_PORT = 8000
MAX_CACHE = 13
NET_SAMPLE_SEC = 1.0
PING_INTERVAL = 20
PING_TIMEOUT = 20

# --- State ---
clients = set()
package_cache = []


def sigil():
    """UTC timestamp sigil."""
    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


async def broadcast(message: str):
    """Send to all connected clients."""
    if not clients:
        return
    dead = set()
    tasks = []
    for ws in list(clients):
        try:
            tasks.append(asyncio.create_task(ws.send(message)))
        except Exception:
            dead.add(ws)
    if tasks:
        await asyncio.gather(*tasks, return_exceptions=True)
    for ws in dead:
        clients.discard(ws)
    tasks = [produce_net(), heartbeat()]
    if keepalive_ping:
        tasks.append(keepalive())
    if start_heartbeat:
        start_heartbeat(interval=60)

    if multiply_agent:
        tasks.append(multiply_agent.multiply())


async def publish(payload: str):
    """Stamp, cache, broadcast."""
    stamped = f"{sigil()} | {payload}"
    package_cache.append(stamped)
    if len(package_cache) > MAX_CACHE:
        package_cache.pop(0)
    await broadcast(stamped)


# --- WebSocket Handler ---
async def handler(websocket):
    clients.add(websocket)
    print(f"[WS] Client connected: {len(clients)}")
    try:
        for msg in package_cache:
            await websocket.send(f"[REPLAY] {msg}")
        async for message in websocket:
            await publish(message)
    except websockets.ConnectionClosed:
        pass
    finally:
        clients.discard(websocket)
        print(f"[WS] Client disconnected: {len(clients)}")


# --- Producers ---
def _read_proc_net_dev():
    """Return iface -> (rx, tx)."""
    data = {}
    try:
        with open("/proc/net/dev", "r") as f:
            lines = f.readlines()[2:]
        for line in lines:
            if ":" not in line:
                continue
            iface, rest = line.split(":", 1)
            iface = iface.strip()
            fields = rest.split()
            if len(fields) >= 16:
                rx_bytes = int(fields[0])
                tx_bytes = int(fields[8])
                data[iface] = (rx_bytes, tx_bytes)
    except Exception:
        pass
    return data


async def produce_net():
    prev = _read_proc_net_dev()
    await asyncio.sleep(NET_SAMPLE_SEC)
    while True:
        curr = _read_proc_net_dev()
        for iface, (rx, tx) in curr.items():
            if iface in prev:
                prx, ptx = prev[iface]
                drx, dtx = max(0, rx - prx), max(0, tx - ptx)
                if drx or dtx:
                    await publish(f"NET | {iface} rx={drx}B tx={dtx}B total_rx={rx}B total_tx={tx}B")
        prev = curr
        await asyncio.sleep(NET_SAMPLE_SEC)


async def heartbeat():
    while True:
        await publish("HEARTBEAT | agent=RFI-IRFOS v2.1 life-mode")
        await asyncio.sleep(15)


async def keepalive():
    """Run ping_keepalife if available."""
    if keepalive_ping:
        while True:
            try:
                keepalive_ping("8.8.8.8")
                await publish("PING | keepalive ok")
            except Exception as e:
                await publish(f"PING | error {e}")
            await asyncio.sleep(30)


# --- Auto-port finder ---
def find_open_port(start=START_PORT):
    port = start
    while True:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind((HOST, port))
                return port
            except OSError:
                port += 1


# --- Main ---
async def main():
    port = find_open_port()
    print("-------------------------------------------------------")
    print(" RFI-IRFOS Unified Ternary Agent v2.1 | Life Mode ON ")
    print("-------------------------------------------------------")
    print(f"[AGENT] WebSocket ws://{HOST}:{port}")

    tasks = [produce_net(), heartbeat()]
    if keepalive_ping:
        tasks.append(keepalive())
    if start_heartbeat:
        # optional background heartbeat agent
        start_heartbeat(interval=60)

    async with websockets.serve(
        handler, HOST, port,
        ping_interval=PING_INTERVAL,
        ping_timeout=PING_TIMEOUT,
        max_queue=32,
    ):
        await asyncio.gather(*tasks)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n[AGENT] Shutdown requested — bye.")
