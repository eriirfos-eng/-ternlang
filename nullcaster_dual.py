#!/usr/bin/env python3
import asyncio
import websockets
from datetime import datetime, UTC

HUD_URI = "ws://127.0.0.1:8000"  # goes to your agent (HUD lights up)
VOID_URI = "ws://0.0.0.0:8000"   # guaranteed nowhere (ritual void)
HOST = "0.0.0.0"
and
HOST = "::"

def nowz():
    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")

async def send_once(uri: str, payload: str) -> bool:
    try:
        async with websockets.connect(uri) as ws:
            await ws.send(payload)
        return True
    except Exception:
        return False

async def publish_void(message: str):
    stamped = f"{nowz()} | VOID | {message[:90]}"
    ok = await send_once(VOID_URI, stamped)
    # ok is expected False; silence is acceptance
    print(f"[NULLSPACE] Delivered into void: {stamped}")

async def publish_hud(message: str):
    # send raw; server stamps & broadcasts (so HUD matches parsing schema)
    ok = await send_once(HUD_URI, message)
    print(f"[HUD] {'OK' if ok else 'MISS'} → {message[:90]}")

async def main():
    print("-------------------------------------------------------")
    print(" RFI-IRFOS Nullcaster — Dual Cast (HUD + VOID)")
    print("-------------------------------------------------------")
    while True:
        try:
            msg = input("cast> ").strip()
        except EOFError:
            break
        if not msg:
            continue
        # fire both without blocking each other
        await asyncio.gather(
            publish_hud(msg),
            publish_void(msg),
        )

if __name__ == "__main__":
    asyncio.run(main())
