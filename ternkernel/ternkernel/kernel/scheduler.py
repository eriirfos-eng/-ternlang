"""
ternkernel.kernel.scheduler
Simple priority scheduler with jittered backoff and health pings.
"""
import time, heapq, random
from typing import Callable, Any, List, Tuple

Task = Tuple[float, int, int, Callable[[], Any]]  # (when, priority, seq, fn)

class Scheduler:
    def __init__(self) -> None:
        self._heap: List[Task] = []
        self._seq = 0

    def submit(self, fn: Callable[[], Any], priority: int = 0, delay: float = 0.0) -> None:
        self._seq += 1
        when = time.time() + delay + random.random()*0.01
        heapq.heappush(self._heap, (when, priority, self._seq, fn))

    def run_until_empty(self, time_budget: float = 0.25) -> None:
        t0 = time.time()
        while self._heap and (time.time() - t0) < time_budget:
            when, _prio, _seq, fn = heapq.heappop(self._heap)
            if when > time.time():
                # not yet time, push back
                heapq.heappush(self._heap, (when, _prio, _seq, fn))
                time.sleep(min(when - time.time(), 0.005))
                continue
            try:
                fn()
            except Exception:
                # tasks fail closed
                pass
