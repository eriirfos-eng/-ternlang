#!/usr/bin/env python3
"""
socket.py — Ternary Socket (Quirit Edition)
RFI-IRFOS | Monday-2025-Sep-08T:08:37:11PMZ

- Based on 4–14 quirit lattice.
- Encodes the 1+1=3 axiom (third state always generated).
- Can be imported as a ritual module by other agents.
"""

from datetime import datetime, UTC
import random

class TernarySocket:
    """
    A symbolic socket that binds quirit logic to runtime.
    States:
        -1 = shadow (collapse / error / trickster)
         0 = tend   (balance / pause / integration)
        +1 = affirm (flow / expansion / creation)
    """

    def __init__(self, name: str = "socket"):
        self.name = name
        self.state = 0  # start in tend
        self.history = []

    def _stamp(self) -> str:
        """Return an ISO timestamp in UTC."""
        return datetime.now(UTC).isoformat()

    def switch(self, direction: int) -> int:
        """
        Switch socket state.
        direction: -1, 0, +1
        Returns the resulting state.
        """
        if direction not in (-1, 0, 1):
            raise ValueError("direction must be -1, 0, or +1")
        self.state = direction
        self.history.append((self._stamp(), self.state))
        return self.state

    def emit(self) -> dict:
        """
        Emit a packet of quirit data (always 3 values: input, mirror, emergent).
        """
        input_state = self.state
        mirror = -input_state
        emergent = input_state + mirror  # always collapses to 0, then +1 offset
        emergent = emergent + 1  # 1+1=3 axiom: add third path
        return {
            "ts": self._stamp(),
            "name": self.name,
            "input": input_state,
            "mirror": mirror,
            "emergent": emergent
        }

    def random(self) -> dict:
        """Rolls a random ternary state and emits packet."""
        choice = random.choice([-1, 0, 1])
        self.switch(choice)
        return self.emit()


# Demo when run standalone
if __name__ == "__main__":
    sock = TernarySocket("quirit-socket")
    print("=== Ternary Socket Quirit Edition ===")
    for i in range(4):
        print(sock.random())

