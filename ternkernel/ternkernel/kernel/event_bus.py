"""
ternkernel.kernel.event_bus
Minimal synchronous pub-sub event bus.
"""
from typing import Callable, Dict, Any, List, DefaultDict
from collections import defaultdict

Subscriber = Callable[[Dict[str, Any]], None]

class EventBus:
    def __init__(self) -> None:
        self._subs: DefaultDict[str, List[Subscriber]] = defaultdict(list)

    def subscribe(self, topic: str, fn: Subscriber) -> None:
        self._subs[topic].append(fn)

    def publish(self, topic: str, event: Dict[str, Any]) -> None:
        for fn in list(self._subs.get(topic, [])):
            try:
                fn(event)
            except Exception:
                # never let a subscriber kill the bus
                pass

BUS = EventBus()
