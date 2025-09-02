"""
ternkernel.core.resilience
Resilience tools for safe execution, with collapse-to-tend behavior on hazards.
"""

from __future__ import annotations
from dataclasses import dataclass
from contextlib import contextmanager
from typing import Any, Callable, Optional, Dict
import time
import traceback

# optional event sink set by the kernel
_EVENT_SINK: Optional[Callable[[Dict[str, Any]], None]] = None

def set_event_sink(sink: Callable[[Dict[str, Any]], None]) -> None:
    global _EVENT_SINK
    _EVENT_SINK = sink

def _emit(event: Dict[str, Any]) -> None:
    if _EVENT_SINK is not None:
        try:
            _EVENT_SINK(event)
        except Exception:
            pass  # never let event emission crash the path

@dataclass
class CollapseEvent:
    ts: float
    op: str
    detail: str
    fallback: int  # -1,0,+1
    reason: str
    stack: Optional[str] = None

def collapse_to_tend(fn: Callable[..., Any]) -> Callable[..., Any]:
    """
    Decorator that catches hazardous arithmetic and collapses to TEND (0).
    """
    def wrapper(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except ZeroDivisionError as e:
            ev = CollapseEvent(
                ts=time.time(), op=fn.__name__, detail="divide by zero",
                fallback=0, reason=str(e), stack=traceback.format_exc()
            )
            _emit({"type":"CollapseEvent", **ev.__dict__})
            return 0
        except Exception as e:
            ev = CollapseEvent(
                ts=time.time(), op=fn.__name__, detail="error",
                fallback=0, reason=str(e), stack=traceback.format_exc()
            )
            _emit({"type":"CollapseEvent", **ev.__dict__})
            return 0
    return wrapper

@contextmanager
def tend_guard(op: str = "block") -> Any:
    """
    Context that collapses any error to TEND and emits an event.
    """
    try:
        yield
    except Exception as e:
        ev = CollapseEvent(
            ts=time.time(), op=op, detail="guard error",
            fallback=0, reason=str(e), stack=traceback.format_exc()
        )
        _emit({"type":"CollapseEvent", **ev.__dict__})
