from contextlib import ContextDecorator, contextmanager
from dataclasses import dataclass
import functools
import os
import math
from typing import Callable, Any, Dict

REFRAIN, TEND, AFFIRM = -1, 0, 1

@dataclass(frozen=True)
class CollapseEvent:
    op: str
    a: float
    b: float
    state: str = "TEND"
    meta: Dict[str, Any] = None

DIV0_POLICY = os.getenv("TERNLANG_DIV0_POLICY", "tend").lower()  # tend|raise|nan

def _emit(event: CollapseEvent) -> None:
    # minimal hook; replace with proper logger/telemetry later
    print(f"[DZNA] {event}")

def collapse_to_tend(op_name: str) -> Callable:
    """Decorator: on ZeroDivisionError, return (0, 'TEND') and emit event."""
    def deco(fn: Callable):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            try:
                out = fn(*args, **kwargs)
                return out
            except ZeroDivisionError:
                if DIV0_POLICY == "raise":
                    raise
                if DIV0_POLICY == "nan":
                    _emit(CollapseEvent(op=op_name, a=args[0], b=args[1], meta={"policy":"nan"}))
                    return math.nan, "TEND"  # keep protocol stable
                a = kwargs.get("a", args[0] if args else None)
                b = kwargs.get("b", args[1] if len(args) > 1 else kwargs.get("b"))
                _emit(CollapseEvent(op=op_name, a=a, b=b, meta={"policy":"tend"}))
                return 0, "TEND"
        return wrapper
    return deco

@contextmanager
def tend_on_zero_division():
    """Context manager to temporarily force TEND behavior."""
    global DIV0_POLICY
    old = DIV0_POLICY
    DIV0_POLICY = "tend"
    try:
        yield
    finally:
        DIV0_POLICY = old
