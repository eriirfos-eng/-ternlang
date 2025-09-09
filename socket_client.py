#!/usr/bin/env python3
"""
socket_client.py — Bounceback test client
Connects to ws://127.0.0.1:8000, prints replay + live stream,
and lets you type messages to send.
"""

import asyncio
import websockets
import sys

WS_URL = "ws://127.0.0.1:8000"

async def listen_and_send():
    async with websockets.connect(WS_URL) as ws:
        print(f"[CLIENT] Connected to {WS_URL}")

        async def receiver():
            try:
                async for msg in ws:
                    print(f"[RECV] {msg}")
            except websockets.ConnectionClosed:
                print("[CLIENT] Connection closed by server")

        async def sender():
            loop = asyncio.get_event_loop()
            while True:
                msg = await loop.run_in_executor(None, sys.stdin.readline)
                msg = msg.strip()
                if msg.lower() in ("exit", "quit"):
                    print("[CLIENT] Closing…")
                    await ws.close()
                    break
                await ws.send(msg)

        await asyncio.gather(receiver(), sender())

if __name__ == "__main__":
    try:
        asyncio.run(listen_and_send())
    except KeyboardInterrupt:
        print("\n[CLIENT] Stopped")

