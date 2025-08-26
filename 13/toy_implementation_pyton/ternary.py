from enum import IntEnum

# Define ternary values
class Ternary(IntEnum):
    NEG = -1   # -1 = negate / object
    HOLD = 0   #  0 = tend / pause
    AFFIRM = 1 # +1 = affirm / go

# Example stage function
def stage_check_hunger(input_stance: Ternary, hungry: bool) -> Ternary:
    """
    Simple ternary stage:
    - If truly hungry, affirm (+1).
    - If not hungry at all, negate (-1).
    - If kind of meh, hold (0).
    """
    if hungry is True:
        return Ternary.AFFIRM
    elif hungry is False:
        return Ternary.NEG
    else:
        return Ternary.HOLD

# Example packet run through stage
packet_stance = Ternary.AFFIRM   # You want the cookie
new_stance = stage_check_hunger(packet_stance, hungry=None)

print("Initial stance:", packet_stance.name)
print("After stage:", new_stance.name)
from __future__ import annotations
from dataclasses import dataclass
from enum import IntEnum
from typing import Callable, Dict, List, Optional, Tuple, Any

# -----------------------------
# /core: ternary primitives
# -----------------------------
class Ternary(IntEnum):
    NEG = -1     # object / negate
    HOLD = 0     # tend / pause / leave-space
    AFFIRM = 1   # affirm / go

    def __str__(self) -> str:
        return {self.NEG: "-1", self.HOLD: "0", self.AFFIRM: "+1"}[self]


def clamp_ternary(value: int) -> Ternary:
    if value <= -1:
        return Ternary.NEG
    if value >= 1:
        return Ternary.AFFIRM
    return Ternary.HOLD


@dataclass
class TraceEntry:
    stage: str
    prior: Ternary
    after: Ternary
    reason: str


# Stage function signature: (ctx, prior) -> Tuple[Ternary, str]
StageFn = Callable[[Dict[str, Any], Ternary], Tuple[Ternary, str]]


@dataclass
class Stage:
    name: str
    fn: StageFn
    non_negotiable: bool = False  # ecocentric safeguards, cannot be skipped


class Pipeline:
    def __init__(self, name: str, stages: List[Stage]):
        # Always sort so non-negotiables run first while preserving relative order otherwise
        nn = [s for s in stages if s.non_negotiable]
        rest = [s for s in stages if not s.non_negotiable]
        self.name = name
        self.stages = nn + rest

    def run(
        self,
        ctx: Dict[str, Any],
        initial: Ternary = Ternary.HOLD,
        narration: bool = True,
        subset: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Run a packet (ctx) through the pipeline.
        - ctx: arbitrary inputs the stages consult.
        - initial: starting stance (-1/0/+1).
        - narration: include textual reasons.
        - subset: optional list of stage names to run (non-negotiables will run regardless).
        Returns dict with final stance and trace (narrated or raw).
        """
        trace: List[TraceEntry] = []

        # Respect dynamic subsetting but ensure non-negotiables are always included
        active: List[Stage] = []
        if subset is not None:
            wanted = set(subset)
            for s in self.stages:
                if s.non_negotiable or s.name in wanted:
                    active.append(s)
        else:
            active = list(self.stages)

        stance = initial
        for stage in active:
            prior = stance
            stance, why = stage.fn(ctx, prior)
            trace.append(TraceEntry(stage=stage.name, prior=prior, after=stance, reason=why))

            # Short-circuit: if a non-negotiable drives NEG hard and ctx forbids override, we can stop
            if stage.non_negotiable and stance == Ternary.NEG and ctx.get("stop_on_guard", True):
                break

        if narration:
            narrated = [
                f"{i+1:02d}. {t.stage}: {t.prior}->{t.after} :: {t.reason}"
                for i, t in enumerate(trace)
            ]
            return {
                "pipeline": self.name,
                "final": int(stance),
                "final_str": str(stance),
                "trace": narrated,
            }
        else:
            raw = [
                {
                    "stage": t.stage,
                    "prior": int(t.prior),
                    "after": int(t.after),
                }
                for t in trace
            ]
            return {
                "pipeline": self.name,
                "final": int(stance),
                "trace": raw,
            }


# ---------------------------------
# /util: tiny helpers for stage fns
# ---------------------------------

def ternary_merge(prior: Ternary, delta: int) -> Ternary:
    """Shift prior stance by delta (-1, 0, +1) and clamp to ternary."""
    return clamp_ternary(int(prior) + int(delta))


def prefer_hold_on_uncertainty(prior: Ternary, certainty: float, threshold: float = 0.6) -> Ternary:
    """If certainty is low, drift toward HOLD regardless of direction."""
    if certainty < threshold:
        if prior == Ternary.AFFIRM:
            return Ternary.HOLD
        if prior == Ternary.NEG:
            return Ternary.HOLD
    return prior


# ---------------------------------
# /stages: reusable stage functions
# ---------------------------------

# Ecocentric safeguard — non-negotiable

def st_guard_biosphere(ctx: Dict[str, Any], prior: Ternary) -> Tuple[Ternary, str]:
    risk = float(ctx.get("bio_risk", 0.0))  # 0..1
    mitigation = float(ctx.get("bio_mitigation", 0.0))  # 0..1
    net = risk - 0.7 * mitigation
    if net >= 0.5:
        return (Ternary.NEG, f"Hard stop: biosphere risk {risk:.2f} outweighs mitigation {mitigation:.2f}.")
    if net > 0.2:
        return (Ternary.HOLD, f"Caution: unresolved biosphere risk {risk:.2f}, partial mitigation {mitigation:.2f}.")
    return (prior, f"Pass: biosphere net risk {net:.2f} acceptable.")


def st_immediate_need(ctx: Dict[str, Any], prior: Ternary) -> Tuple[Ternary, str]:
    need = float(ctx.get("immediate_need", 0.0))  # 0..1
    if need >= 0.7:
        return (ternary_merge(prior, +1), f"Immediate need high ({need:.2f}): nudge up.")
    if need <= 0.2:
        return (ternary_merge(prior, -1), f"Immediate need low ({need:.2f}): nudge down.")
    return (Ternary.HOLD if prior == Ternary.AFFIRM else prior, f"Moderate need ({need:.2f}): lean to HOLD if over-eager.")


def st_social_context(ctx: Dict[str, Any], prior: Ternary) -> Tuple[Ternary, str]:
    last_one = bool(ctx.get("is_last_one", False))
    shared = bool(ctx.get("shared_space", True))
    if last_one and shared:
        return (ternary_merge(prior, -1), "Social courtesy: last one in shared space → nudge toward NEG.")
    return (prior, "Social context acceptable.")


def st_long_term_health(ctx: Dict[str, Any], prior: Ternary) -> Tuple[Ternary, str]:
    impact = float(ctx.get("health_impact", 0.0))  # negative is good, positive is bad
    if impact >= 0.5:
        return (ternary_merge(prior, -1), f"Long-term health burden {impact:.2f}: nudge down.")
    if impact <= -0.3:
        return (ternary_merge(prior, +1), f"Long-term health benefit {impact:.2f}: nudge up.")
    return (prefer_hold_on_uncertainty(prior, certainty=ctx.get("health_certainty", 0.5)), "Health effect ambiguous: favor HOLD under uncertainty.")


def st_timing_window(ctx: Dict[str, Any], prior: Ternary) -> Tuple[Ternary, str]:
    window = float(ctx.get("timing", 0.5))  # 0..1 (0=bad timing, 1=perfect)
    if window >= 0.8:
        return (ternary_merge(prior, +1), f"Timing ripe ({window:.2f}): nudge up.")
    if window <= 0.2:
        return (ternary_merge(prior, -1), f"Timing poor ({window:.2f}): nudge down.")
    return (Ternary.HOLD if prior != Ternary.NEG else prior, f"Timing middling ({window:.2f}): hold unless already NEG.")


def st_regeneration_plan(ctx: Dict[str, Any], prior: Ternary) -> Tuple[Ternary, str]:
    plan = float(ctx.get("regen_strength", 0.0))  # 0..1
    if plan >= 0.7:
        return (ternary_merge(prior, +1), f"Regeneration plan strong ({plan:.2f}).")
    if plan <= 0.2:
        return (ternary_merge(prior, -1), f"Regeneration plan weak ({plan:.2f}).")
    return (prior, "Regeneration plan partial: no stance change.")


def st_commitment_next_day(ctx: Dict[str, Any], prior: Ternary) -> Tuple[Ternary, str]:
    load = float(ctx.get("tomorrow_load", 0.5))  # 0..1
    if load >= 0.7:
        return (ternary_merge(prior, -1), f"High next-day load ({load:.2f}): rest prioritized.")
    if load <= 0.3:
        return (ternary_merge(prior, +1), f"Low next-day load ({load:.2f}): leeway to affirm.")
    return (Ternary.HOLD, "Moderate next-day load: hold.")


def st_creative_flow(ctx: Dict[str, Any], prior: Ternary) -> Tuple[Ternary, str]:
    flow = float(ctx.get("creative_flow", 0.0))  # 0..1
    if flow >= 0.75:
        return (ternary_merge(prior, +1), f"Strong creative flow ({flow:.2f}).")
    if flow <= 0.25:
        return (ternary_merge(prior, -1), f"Low creative flow ({flow:.2f}).")
    return (prior, "Flow moderate: no change.")


def st_sugar_spike(ctx: Dict[str, Any], prior: Ternary) -> Tuple[Ternary, str]:
    spike = float(ctx.get("glycemic_load", 0.5))  # 0..1
    if spike >= 0.7:
        return (ternary_merge(prior, -1), f"Glycemic spike high ({spike:.2f}).")
    if spike <= 0.3:
        return (ternary_merge(prior, +1), f"Glycemic spike low ({spike:.2f}).")
    return (prefer_hold_on_uncertainty(prior, certainty=0.4), "Spike uncertain: prefer HOLD.")


# ---------------------------------------------------
# /pipelines: a handful of named mini pipelines (4x)
# ---------------------------------------------------

# /cookie — "Should I eat this cookie now?"
COOKIE_PIPE = Pipeline(
    name="/cookie",
    stages=[
        Stage("guard_biosphere", st_guard_biosphere, non_negotiable=True),
        Stage("immediate_need", st_immediate_need),
        Stage("social_context", st_social_context),
        Stage("long_term_health", st_long_term_health),
        Stage("timing_window", st_timing_window),
    ],
)

# /forest — "Should we cut down this single tree?"
FOREST_PIPE = Pipeline(
    name="/forest",
    stages=[
        Stage("guard_biosphere", st_guard_biosphere, non_negotiable=True),
        Stage("regeneration_plan", st_regeneration_plan),
        Stage("timing_window", st_timing_window),
        Stage("social_context", st_social_context),  # e.g., shared urban canopy / last shade tree
    ],
)

# /sleep — "Should I stay up late to finish this song?"
SLEEP_PIPE = Pipeline(
    name="/sleep",
    stages=[
        Stage("guard_biosphere", st_guard_biosphere, non_negotiable=True),  # usually passes
        Stage("commitment_next_day", st_commitment_next_day),
        Stage("creative_flow", st_creative_flow),
        Stage("timing_window", st_timing_window),
    ],
)

# /icecream — "Ice cream for breakfast?"
ICECREAM_PIPE = Pipeline(
    name="/icecream",
    stages=[
        Stage("guard_biosphere", st_guard_biosphere, non_negotiable=True),
        Stage("sugar_spike", st_sugar_spike),
        Stage("immediate_need", st_immediate_need),
        Stage("long_term_health", st_long_term_health),
    ],
)


# ---------------------------------
# /demo: quick examples & utilities
# ---------------------------------

def demo_cookie() -> Dict[str, Any]:
    ctx = {
        "bio_risk": 0.1,
        "bio_mitigation": 0.3,
        "immediate_need": 0.4,
        "is_last_one": True,
        "shared_space": True,
        "health_impact": 0.2,  # mild negative
        "health_certainty": 0.5,
        "timing": 0.6,
    }
    return COOKIE_PIPE.run(ctx, initial=Ternary.AFFIRM, narration=True)


def demo_forest(higher_risk: bool = True) -> Dict[str, Any]:
    ctx = {
        "bio_risk": 0.8 if higher_risk else 0.2,
        "bio_mitigation": 0.1,
        "regen_strength": 0.4,
        "timing": 0.5,
        "is_last_one": True,  # last shade tree in a plaza, for example
        "shared_space": True,
        "stop_on_guard": True,
    }
    return FOREST_PIPE.run(ctx, initial=Ternary.HOLD, narration=True)


def demo_sleep() -> Dict[str, Any]:
    ctx = {
        "bio_risk": 0.0,
        "bio_mitigation": 0.0,
        "tomorrow_load": 0.8,  # big day tomorrow
        "creative_flow": 0.9,  # but inspiration is high
        "timing": 0.6,
    }
    return SLEEP_PIPE.run(ctx, initial=Ternary.HOLD, narration=True)


def demo_icecream() -> Dict[str, Any]:
    ctx = {
        "bio_risk": 0.1,
        "bio_mitigation": 0.2,
        "glycemic_load": 0.85,
        "immediate_need": 0.2,
        "health_impact": 0.6,
        "health_certainty": 0.7,
    }
    return ICECREAM_PIPE.run(ctx, initial=Ternary.AFFIRM, narration=True)


if __name__ == "__main__":
    # Example manual runs; in notebooks or REPLs, call these functions directly
    from pprint import pprint

    print("\n=== /cookie ===")
    pprint(demo_cookie())

    print("\n=== /forest (high risk) ===")
    pprint(demo_forest(higher_risk=True))

    print("\n=== /sleep ===")
    pprint(demo_sleep())

    print("\n=== /icecream ===")
    pprint(demo_icecream())
