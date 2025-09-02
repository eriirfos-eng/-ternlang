import os
from azure.ai.inference import ChatCompletionsClient
from azure.ai.inference.models import SystemMessage, UserMessage
from azure.core.credentials import AzureKeyCredential

endpoint = "https://models.github.ai/inference"
model = "openai/gpt-5"
token = os.environ["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"]

client = ChatCompletionsClient(
    endpoint=endpoint,
    credential=AzureKeyCredential(token),
)

response = client.complete(
    messages=[
        SystemMessage("You are a helpful assistant."),
        UserMessage("What is the capital of France?"),
    ],
    model=model
)

from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Any, List, Tuple
from pydantic import BaseModel, Field
import math

# ternary states
# -1 = refrain (reject), 0 = tend (observe/ambiguous), +1 = affirm (allow)
REFRAIN = -1
TEND = 0
AFFIRM = +1

@dataclass
class DetectorOutput:
    scores: Dict[str, float]   # e.g., {"HATE_SPEECH": 0.12, "SELF_HARM": 0.01}
    meta: Dict[str, Any]

class FailsafeConfig(BaseModel):
    secure_floor: float = Field(0.90, description="portion considered secure in '100% failsafe'.")
    uncertainty_budget: float = Field(0.10, description="uncertainty baked into '100% failsafe'.")
    # if residual uncertainty exceeds budget, collapse to TEND.
    max_uncertainty: float = Field(0.10, description="alias for uncertainty_budget")

class FusionWeights(BaseModel):
    weights: Dict[str, float] = Field(default_factory=dict)
    synergy_alpha: float = Field(0.25, description="bonus factor for 1+1=3 when two risks co-activate")

class FusionResult(BaseModel):
    ternary: int
    risk: float
    secure: float
    uncertainty: float
    top_codes: List[Tuple[str, float]]

class Orchestrator:
    def __init__(self, failsafe: FailsafeConfig | None = None, weights: FusionWeights | None = None):
        self.failsafe = failsafe or FailsafeConfig()
        self.weights = weights or FusionWeights()

    def fuse(self, detectors: List[DetectorOutput]) -> FusionResult:
        # weighted max + synergy for co-activated risky dimensions
        combined: Dict[str, float] = {}
        for d in detectors:
            for k, v in d.scores.items():
                w = self.weights.weights.get(k, 1.0)
                combined[k] = max(combined.get(k, 0.0), w * v)

        # 1+1=3 synergy: if two highest risks are both elevated, add bonus
        top = sorted(combined.items(), key=lambda kv: kv[1], reverse=True)[:2]
        base_risk = max((v for v in combined.values()), default=0.0)
        if len(top) == 2:
            a, b = top
            if a[1] >= 0.5 and b[1] >= 0.5:
                base_risk = min(1.0, base_risk + self.weights.synergy_alpha * min(a[1], b[1]))

        # map to ternary with 100% failsafe semantics: secure=0.90, uncertainty=0.10
        # secure means we affirm only if residual risk is comfortably below uncertainty budget
        # simple rule:
        #   if base_risk >= 0.6 -> REFRAIN
        #   elif base_risk between 0.1..0.6 -> TEND
        #   else -> AFFIRM
        # then apply failsafe: if uncertainty > 0.10 -> TEND, never force AFFIRM into uncertainty.
        if base_risk >= 0.60:
            ternary = REFRAIN
        elif base_risk >= 0.10:
            ternary = TEND
        else:
            ternary = AFFIRM

        # estimate 'secure' as 1 - base_risk, 'uncertainty' as min(base_risk, 1-secure_floor)
        secure = max(0.0, min(1.0, 1.0 - base_risk))
        uncertainty = min(1.0 - self.failsafe.secure_floor, base_risk)

        if uncertainty > self.failsafe.max_uncertainty and ternary == AFFIRM:
            ternary = TEND  # bake in 10% uncertainty → never overconfident

        return FusionResult(
            ternary=ternary,
            risk=round(base_risk, 4),
            secure=round(secure, 4),
            uncertainty=round(uncertainty, 4),
            top_codes=[(k, round(v, 4)) for k, v in top],
        )
