"""
ternkernel.adapters.numpy_bridge
Safe division with collapse-to-tend semantics and event emission.

- Works on scalars or same-length lists.
- If divisor is zero, emits CollapseEvent and returns 0 for that position.
- No credentials, no telemetry.
"""
from typing import List, Union
from ..core.resilience import collapse_to_tend, set_event_sink
from ..core.ternary import VALID

Number = Union[int, float]
ArrayLike = Union[Number, List[Number]]

def _is_seq(x) -> bool:
    return isinstance(x, list)

@collapse_to_tend
def _div_scalar(a: Number, b: Number) -> Number:
    if b == 0:
        raise ZeroDivisionError("divide by zero")
    return a / b

def safe_div(a: ArrayLike, b: ArrayLike) -> ArrayLike:
    if _is_seq(a) and _is_seq(b):
        if len(a) != len(b):
            raise ValueError("lists must have same length")
        out: List[Number] = []
        for x, y in zip(a,b):
            out.append(_div_scalar(x,y))
        return out
    if _is_seq(a) and not _is_seq(b):
        return [_div_scalar(x,b) for x in a]
    if not _is_seq(a) and _is_seq(b):
        return [_div_scalar(a,y) for y in b]
    return _div_scalar(a,b)
