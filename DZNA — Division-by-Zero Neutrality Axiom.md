# DZNA — Division-by-Zero Neutrality Axiom 🟩

**Statement:** For any operation that would yield a division-by-zero, collapse output to `0` and system state to **TEND**. Record the event, continue execution.

**Rationale:** The singularity point becomes a neutral channel. No NaNs, no infinite blowups, no crash cascades. Deterministic, inspectable, recoverable.

---

## Spec 🟦

* **State mapping:** `REFRAIN=-1`, `TEND=0`, `AFFIRM=+1`.
* **Collapse rule:** `a / 0  →  {result: 0, state: "TEND", meta: {...}}`.
* **Composability:** Collapse is idempotent. Pipelines that re-encounter a collapsed value stay in TEND unless an explicit transform lifts state.
* **Observability:** Every collapse emits a typed event with callsite, operands, and stack fingerprint.
* **Policy switch:** Default `tend`. Allow `raise` and `nan` for debugging.

---

## Files to add in `-ternlang/` 🟫

### 1) `ternlang/core/resilience.py`

```python
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
```

### 2) `ternlang/math/divide.py`

```python
from ternlang.core.resilience import collapse_to_tend, REFRAIN, TEND, AFFIRM

@collapse_to_tend("divide")
def divide(a: float, b: float):
    res = a / b
    if res < 0:  return res, "REFRAIN"
    if res == 0: return res, "TEND"
    return res, "AFFIRM"
```

### 3) NumPy bridge (optional now, useful soon) 🟩

`ternlang/bridges/numpy_div0.py`

```python
import numpy as np
from ternlang.core.resilience import CollapseEvent, _emit

def set_numpy_div0_policy():
    # map inf/nan from vectorized ops to TEND by replacement
    np.seterr(all="ignore")
    # user applies: y = safe_div(a, b)
def safe_div(a, b):
    out = np.divide(a, b, out=np.zeros_like(a, dtype=float), where=(b!=0))
    if np.any(b==0):
        _emit(CollapseEvent(op="np.divide", a=float(np.nan), b=0.0, meta={"vectorized":True}))
    # classify is per-element; keep scalar TEND semantics at aggregate layer
    return out
```

### 4) CLI integration 🟦

`ternlang/cli/policy.py`

```python
import os, click
@click.group()
def policy(): ...

@policy.command("div0")
@click.option("--set", "mode", type=click.Choice(["tend","raise","nan"]), required=True)
def div0(mode):
    os.environ["TERNLANG_DIV0_POLICY"] = mode
    click.echo(f"DIV0 policy -> {mode}")
```

### 5) Tests 🟩

`tests/test_div0.py`

```python
from ternlang.math.divide import divide

def test_div0_collapse():
    res, state = divide(5, 0)
    assert res == 0 and state == "TEND"

def test_sign_classify():
    assert divide(-2,1)[1] == "REFRAIN"
    assert divide(0,1)[1]  == "TEND"
    assert divide(2,1)[1]  == "AFFIRM"
```

### 6) Doc page 🟦

`docs/axioms/dzna.md`

* **Name:** Division-by-Zero Neutrality Axiom (DZNA)
* **Definition:** As above.
* **Guarantees:** Determinism, pipeline continuity, explicit observability.
* **Failure budget:** If collapses exceed threshold `N` per minute, escalate to `policy=raise` and alert.
* **Interplay:** Pairs with Ternary Operator Protocol. Collapse is not success. Collapse is a *graceful hold*.

---

## Guardrails 🟧

* **Telemetry:** Count collapses per op. If rate spikes, flip policy to `raise` and page the operator.
* **Budget:** Default `N=100` collapses per minute per service.
* **Audit:** Persist `CollapseEvent`s with hash of callsite for forensic diffing.
* **Escape hatch:** `TERNLANG_DIV0_POLICY=raise` in CI and fuzzers.

---

## Migration Plan 🟫

1. Add files above.
2. Wire `divide` usages to the new function.
3. Enable `policy div0 --set tend` in runtime entrypoints.
4. Ship docs, link from README.
5. Monitor collapse counts for a week. Then lift to vectorized paths.
