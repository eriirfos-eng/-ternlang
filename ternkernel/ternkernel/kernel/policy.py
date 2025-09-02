"""
ternkernel.kernel.policy
Algebraic implication and ethical policy clamp.
"""
from ..core.ternary import T, VALID, meet, imp_godel

def policy_implies(a: T, b: T) -> T:
    """
    Ethical 'implies' (⇒) layer:
    - if a == +1: return b
    - if a in {0, -1}: return +1
    """
    if a not in VALID or b not in VALID:
        raise ValueError("invalid ternary value")
    return b if a == 1 else 1

def consequence(a: T, b: T) -> T:
    """Consequence = meet( Gödel residuum, policy operator )."""
    return meet(imp_godel(a,b), policy_implies(a,b))
