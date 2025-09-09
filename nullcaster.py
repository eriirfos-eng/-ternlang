# nullcaster.py
import asyncio
import websockets
import datetime
import hashlib

def sigil():
    now = datetime.datetime.utcnow().isoformat()
    return hashlib.sha1(now.encode()).hexdigest()[:8]

async def broadcaster():
    """Interactive mode: you broadcast to whoever listens (if anyone)."""
    uri = "ws://0.0.0.0:8000"
    async with websockets.connect(uri) as ws:
        while True:
            msg = input("Enter message: ")
            await ws.send(msg)
            print(f"[BROADCAST] {msg}")

async def publish_nullspace(message):
    """Ritual mode: send into void, never expecting return."""
    stamped = f"{sigil()} | VOID | {message[:90]}"
    try:
        async with websockets.connect("::") as ws:
            await ws.send(stamped)
    except Exception:
        # Failure is success here: the nullspace accepts by not answering.
        pass
    print(f"[NULLSPACE] Delivered into void: {stamped}")

if __name__ == "__main__":
    # Example: run ritual emission once, then enter broadcast loop
    asyncio.run(publish_nullspace("Genesis emission — seed cast into null."))
    asyncio.run(broadcaster())
#!/usr/bin/env python3
import asyncio, websockets, datetime

def sigil():
    return datetime.datetime.now(datetime.UTC).strftime("%Y-%m-%dT%H:%M:%SZ")

async def publish_nullspace(message):
    stamped = f"{sigil()} | VOID | {message[:90]}"
    try:
        async with websockets.connect("ws://0.0.0.0:8000") as ws:
            await ws.send(stamped)
    except Exception:
        # Nullspace always absorbs — failure is the ritual
        pass
    print(f"[NULLSPACE] Delivered into void: {stamped}")

async def main():
    while True:
        msg = input("Enter void-cast: ")
        await publish_nullspace(msg)

if __name__ == "__main__":
    asyncio.run(main())
