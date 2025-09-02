"""
ternkernel.agents.time_crystal.agent
Collapse engine that moves 0-states toward affirm (+1) under signals.
"""
from dataclasses import dataclass
from typing import Optional, List
from ...core.ternary import T, VALID, meet, join, neg, imp_godel, equiv_godel, xor_star, nand
from ...kernel.policy import consequence

@dataclass
class CollapseConfig:
    affirm_threshold: int = 1
    allow_recovery_from_minus: bool = True
    max_hold_steps: int = 2

class TimeCrystalAgent:
    def __init__(self, config: Optional[CollapseConfig] = None, use_policy: bool = True):
        self.config = config or CollapseConfig()
        self.use_policy = use_policy

    def _score(self, s: T) -> int:
        if s not in VALID: raise ValueError("invalid")
        return s

    def collapse(self, state: T, signal: T, hold_count: int = 0) -> T:
        if state not in VALID or signal not in VALID:
            raise ValueError("invalid ternary value")
        if state == 1: return 1
        if state == 0:
            promote = (self._score(signal) >= self.config.affirm_threshold) or (hold_count >= self.config.max_hold_steps)
            return 1 if promote else 0
        if self.config.allow_recovery_from_minus and self._score(signal) >= 0:
            return 0
        return -1

    def entail(self, a: T, b: T) -> T:
        core = consequence(a,b) if self.use_policy else imp_godel(a,b)
        return core
