"""
FastAPI server for ternkernel.
Run:
  uvicorn ternkernel.api.server:app --reload --port 8000
"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List
from ..kernel.event_bus import BUS
from ..core.resilience import set_event_sink
from ..adapters.numpy_bridge import safe_div
from ..agents.time_crystal.agent import TimeCrystalAgent, CollapseConfig
from ..core.ternary import VALID
from ..kernel.policy import consequence

app = FastAPI(title="ternkernel", version="0.1.0")
agent = TimeCrystalAgent()
set_event_sink(lambda ev: BUS.publish(ev.get("type","event"), ev))

class CollapseIn(BaseModel):
    state: int = Field(..., description="-1, 0, or +1")
    signal: int = Field(..., description="-1, 0, or +1")
    hold_count: int = 0

class CollapseOut(BaseModel):
    next_state: int

class EntailIn(BaseModel):
    a: int
    b: int

class EntailOut(BaseModel):
    entailment: int

class DivIn(BaseModel):
    a: list | int | float
    b: list | int | float

class DivOut(BaseModel):
    result: list | float

def _check(x: int):
    if x not in VALID:
        raise HTTPException(status_code=400, detail="values must be -1, 0, or +1")

@app.post("/collapse", response_model=CollapseOut)
def collapse(inp: CollapseIn):
    _check(inp.state); _check(inp.signal)
    return {"next_state": agent.collapse(inp.state, inp.signal, inp.hold_count)}

@app.post("/entail", response_model=EntailOut)
def entail(inp: EntailIn):
    _check(inp.a); _check(inp.b)
    return {"entailment": consequence(inp.a, inp.b)}

@app.post("/safe_div", response_model=DivOut)
def safe_divide(inp: DivIn):
    return {"result": safe_div(inp.a, inp.b)}
