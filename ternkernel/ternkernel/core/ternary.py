"""
ternkernel.core.ternary
Three-valued algebra over the chain {-1 < 0 < +1}.

Operations:
- meet (AND) = min
- join (OR)  = max
- neg (NOT) a = -a
- Gödel residuum (implication): a → b = +1 if a ≤ b else b
- equivalence: a ↔ b = min(a→b, b→a)
- xor_star: differentiator suited to {-1,0,+1}
"""

from typing import Tuple

T = int  # restricted to -1, 0, +1
VALID: Tuple[int, int, int] = (-1, 0, +1)

def _check(x: T) -> None:
    if x not in VALID:
        raise ValueError(f"invalid ternary value: {x}")

def meet(a: T, b: T) -> T:
    _check(a); _check(b)
    return a if a <= b else b

def join(a: T, b: T) -> T:
    _check(a); _check(b)
    return a if a >= b else b

def neg(a: T) -> T:
    _check(a)
    return -a

def imp_godel(a: T, b: T) -> T:
    _check(a); _check(b)
    return 1 if a <= b else b

def equiv_godel(a: T, b: T) -> T:
    _check(a); _check(b)
    return meet(imp_godel(a,b), imp_godel(b,a))

def xor_star(a: T, b: T) -> T:
    _check(a); _check(b)
    if a == b: return 0
    if a == 0: return b
    if b == 0: return a
    # remaining case: a == -b
    return -1

def nand(a: T, b: T) -> T:
    _check(a); _check(b)
    return neg(meet(a,b))

def de_morgan_left(a: T, b: T) -> bool:
    return neg(meet(a,b)) == join(neg(a), neg(b))

def de_morgan_right(a: T, b: T) -> bool:
    return neg(join(a,b)) == meet(neg(a), neg(b))
