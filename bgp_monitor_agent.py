#!/usr/bin/env python3
"""
bgp_monitor_agent.py — Quirit BGP Monitor Agent
Desktop Node | Tuesday-2025-Sep-09T:10:24:44AMZ

- Integrates ternary socket (socket_custom.py).
- Simulates BGP update events and routes them through quirit lattice.
- Extendable: can plug into ExaBGP / FRR socket for real feeds later.
"""

import sys
import time
import random
from datetime import datetime, UTC

# Desktop boot banner
print(f"[Desktop] BGP Monitor Agent booting — {datetime.now(UTC).isoformat()}")

# Import our custom ternary socket
try:
    from socket_custom import TernarySocket
except ImportError as e:
    print("[Error] Could not import socket_custom:", e)
    sys.exit(1)


class BGPEvent:
    """Represents a simplified BGP event (symbolic or real)."""

    def __init__(self, prefix: str, action: str, peer: str):
        self.prefix = prefix
        self.action = action  # e.g., "announce", "withdraw"
        self.peer = peer
        self.timestamp = datetime.now(UTC).isoformat()

    def to_dict(self) -> dict:
        return {
            "ts": self.timestamp,
            "prefix": self.prefix,
            "action": self.action,
            "peer": self.peer,
        }


class BGPMonitorAgent:
    """BGP Monitor Agent routing events into quirit lattice."""

    def __init__(self):
        self.sock = TernarySocket("bgp-monitor")
        self.running = True

    def _generate_fake_event(self) -> BGPEvent:
        """Simulates a random BGP event."""
        prefixes = ["192.0.2.0/24", "198.51.100.0/24", "203.0.113.0/24"]
        actions = ["announce", "withdraw"]
        peers = ["AS64512", "AS64513", "AS64514"]

        return BGPEvent(
            prefix=random.choice(prefixes),
            action=random.choice(actions),
            peer=random.choice(peers),
        )

    def handle_event(self, event: BGPEvent):
        """
        Handles a BGP event by passing it through the ternary socket.
        """
        # Switch socket state randomly (shadow, tend, affirm)
        packet = self.sock.random()

        # Enrich packet with BGP event details
        enriched = {**packet, **event.to_dict()}

        print(f"[BGP] Event processed: {enriched}")
        return enriched

    def run(self, cycles: int = 5, interval: float = 2.0):
        """
        Main monitoring loop.
        cycles   = how many events to simulate (-1 for infinite).
        interval = seconds between polls.
        """
        counter = 0
        while self.running and (cycles < 0 or counter < cycles):
            event = self._generate_fake_event()
            self.handle_event(event)
            time.sleep(interval)
            counter += 1


# Ritual runtime
if __name__ == "__main__":
    agent = BGPMonitorAgent()
    print("=== BGP Monitor Agent | Quirit Edition ===")
    agent.run(cycles=5, interval=1.5)

