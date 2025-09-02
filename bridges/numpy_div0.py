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
# Build a fuller, runnable version of time_crystal_agent with a REST API and richer CLI.
import os, zipfile, json, textwrap, pathlib

base = "/mnt/data/time_crystal_agent_full"
pkg = os.path.join(base, "time_crystal_agent")
tests = os.path.join(base, "tests")
os.makedirs(pkg, exist_ok=True)
os.makedirs(tests, exist_ok=True)

# __init__.py
open(os.path.join(pkg, "__init__.py"), "w").write("from .agent import TimeCrystalAgent, CollapseConfig\n")

# ternary.py
ternary_py = r'''"""
time_crystal_agent.ternary
Core ternary algebra over the chain {-1 < 0 < +1}.

Operators:
- AND = meet = min(a,b)
- OR  = join = max(a,b)
- NOT a = -a  (involutive; fixes 0)
- Gödel residuum (implication): a -> b = +1 if a <= b else b
- Equivalence via residuum: a <-> b = min(a->b, b->a)
- XOR* (differentiator): 
    - if a == b: 0
    - elif 0 in {a,b}: the other input
    - elif a == -b: -1
No division used anywhere.
"""
from typing import Tuple

T = int  # restricted to -1, 0, +1
VALID: Tuple[int, int, int] = (-1, 0, +1)

def _check(x: T) -> None:
    if x not in VALID:
        raise ValueError(f"invalid ternary value: {x}")

def meet(a: T, b: T) -> T:
    _check(a); _check(b);  return a if a <= b else b

def join(a: T, b: T) -> T:
    _check(a); _check(b);  return a if a >= b else b

def neg(a: T) -> T:
    _check(a);  return -a

def imp_godel(a: T, b: T) -> T:
    _check(a); _check(b);  return 1 if a <= b else b

def equiv_godel(a: T, b: T) -> T:
    _check(a); _check(b);  return meet(imp_godel(a,b), imp_godel(b,a))

def xor_star(a: T, b: T) -> T:
    _check(a); _check(b)
    if a == b: return 0
    if a == 0: return b
    if b == 0: return a
    return -1  # remaining case is a == -b

def nand(a: T, b: T) -> T:
    _check(a); _check(b);  return neg(meet(a,b))

def de_morgan_left(a: T, b: T) -> bool:
    return neg(meet(a,b)) == join(neg(a), neg(b))

def de_morgan_right(a: T, b: T) -> bool:
    return neg(join(a,b)) == meet(neg(a), neg(b))
'''
open(os.path.join(pkg, "ternary.py"), "w").write(ternary_py)

# policy.py
policy_py = r'''"""
time_crystal_agent.policy
Ethical overlay operator distinct from algebraic implication.

- Policy operator (⇒) encodes "tend/refuse implies no harm" stance.
- Consequence(a,b) = min( a -> b , a ⇒ b ) so ethics can constrain,
  never inflate, algebraic entailment.
"""
from .ternary import T, VALID, meet, imp_godel

def policy_implies(a: T, b: T) -> T:
    """
    Ethical 'implies' (⇒) table:
    - if a == +1: return b (pass-through)
    - if a in {0, -1}: return +1 (no-harm stance)
    """
    if a not in VALID or b not in VALID:
        raise ValueError("invalid ternary value")
    if a == 1:
        return b
    return 1

def consequence(a: T, b: T) -> T:
    """Consequence = meet( Gödel residuum, policy operator )."""
    return meet(imp_godel(a,b), policy_implies(a,b))
'''
open(os.path.join(pkg, "policy.py"), "w").write(policy_py)

# dynamics.py
dynamics_py = r'''"""
time_crystal_agent.dynamics
Temporal update rules and simple circuits.

- NAND feedback: x_{t+1} = NOT( x_t AND b )
- Iterated Modus Ponens: x_{t+1} = min( x_t, x_t -> b )

No division, finite trajectories on {-1,0,+1}.
"""
from typing import List
from .ternary import T, VALID, meet, neg, imp_godel

def step_nand_feedback(x: T, b: T) -> T:
    if x not in VALID or b not in VALID:
        raise ValueError("invalid ternary value")
    return neg(meet(x,b))

def step_modus_ponens(x: T, b: T) -> T:
    if x not in VALID or b not in VALID:
        raise ValueError("invalid ternary value")
    return meet(x, imp_godel(x,b))

def trajectory(step_fn, x0: T, b: T, steps: int = 12) -> List[T]:
    if x0 not in VALID or b not in VALID:
        raise ValueError("invalid ternary value")
    out = [x0]
    x = x0
    for _ in range(steps):
        x = step_fn(x, b)
        out.append(x)
    return out
'''
open(os.path.join(pkg, "dynamics.py"), "w").write(dynamics_py)

# agent.py
agent_py = r'''"""
time_crystal_agent.agent

TimeCrystalAgent drives state collapse and decision flow over the ternary lattice.
"""
from dataclasses import dataclass
from typing import Optional, List
from .ternary import T, VALID, meet, join, neg, imp_godel, equiv_godel, xor_star, nand
from .dynamics import step_modus_ponens, step_nand_feedback, trajectory
from .policy import policy_implies, consequence

@dataclass
class CollapseConfig:
    affirm_threshold: int = 1   # minimal signal s in {-1,0,+1} to promote 0 -> +1
    allow_recovery_from_minus: bool = True  # -1 may climb to 0 when signals justify
    max_hold_steps: int = 2     # how many 0 repeats before forcing a decision

class TimeCrystalAgent:
    def __init__(self, config: Optional[CollapseConfig] = None, use_policy: bool = True):
        self.config = config or CollapseConfig()
        self.use_policy = use_policy

    def _score_signal(self, s: T) -> int:
        if s not in VALID:
            raise ValueError("invalid signal")
        return s

    def collapse(self, state: T, signal: T, hold_count: int = 0) -> T:
        if state not in VALID or signal not in VALID:
            raise ValueError("invalid ternary value")
        if state == 1:
            return 1
        if state == 0:
            promote = (self._score_signal(signal) >= self.config.affirm_threshold) or (hold_count >= self.config.max_hold_steps)
            return 1 if promote else 0
        # state == -1
        if self.config.allow_recovery_from_minus and self._score_signal(signal) >= 0:
            return 0
        return -1

    def entail(self, a: T, b: T) -> T:
        core = imp_godel(a,b)
        if not self.use_policy:
            return core
        return consequence(a,b)

    def nand_feedback(self, x0: T, b: T, steps: int = 8) -> List[T]:
        return trajectory(step_nand_feedback, x0, b, steps)

    def modus_ponens_loop(self, x0: T, b: T, steps: int = 8) -> List[T]:
        return trajectory(step_modus_ponens, x0, b, steps)

    def decide(self, a: T, b: T, gate: str = "AND") -> T:
        gate = gate.upper()
        if gate == "AND": return meet(a,b)
        if gate == "OR":  return join(a,b)
        if gate == "NOT": return neg(a)
        if gate == "IMP": return imp_godel(a,b)
        if gate == "EQUIV": return equiv_godel(a,b)
        if gate == "XOR*": return xor_star(a,b)
        if gate == "NAND": return nand(a,b)
        raise ValueError(f"unknown gate: {gate}")
'''
open(os.path.join(pkg, "agent.py"), "w").write(agent_py)

# cli.py
cli_py = r'''"""
CLI for TimeCrystalAgent.
"""
import sys, json
from .agent import TimeCrystalAgent, CollapseConfig
from .ternary import VALID

def _parse_t(x: str) -> int:
    v = int(x)
    if v not in VALID:
        raise SystemExit("values must be -1, 0, or 1")
    return v

def demo():
    ag = TimeCrystalAgent()
    print("demo: NAND feedback with b=+1")
    for x0 in (-1,0,1):
        print({"x0": x0, "traj": ag.nand_feedback(x0, 1, steps=6)})
    print("demo: iterated modus ponens with b=0")
    for x0 in (-1,0,1):
        print({"x0": x0, "traj": ag.modus_ponens_loop(x0, 0, steps=6)})

def collapse_cmd(args):
    if len(args) < 3:
        raise SystemExit("usage: collapse <state> <signal> <hold_count>")
    state = _parse_t(args[0]); signal = _parse_t(args[1]); hold = int(args[2])
    ag = TimeCrystalAgent()
    print(ag.collapse(state, signal, hold))

def entail_cmd(args):
    if len(args) < 2:
        raise SystemExit("usage: entail <a> <b>")
    a = _parse_t(args[0]); b = _parse_t(args[1])
    ag = TimeCrystalAgent()
    print(ag.entail(a,b))

def main():
    if len(sys.argv) < 2:
        raise SystemExit("usage: python -m time_crystal_agent.cli <demo|collapse|entail> ...")
    cmd = sys.argv[1].lower()
    if cmd == "demo": return demo()
    if cmd == "collapse": return collapse_cmd(sys.argv[2:])
    if cmd == "entail": return entail_cmd(sys.argv[2:])
    raise SystemExit(f"unknown command: {cmd}")

if __name__ == "__main__":
    main()
'''
open(os.path.join(pkg, "cli.py"), "w").write(cli_py)

# server.py (FastAPI)
server_py = r'''"""
FastAPI server for TimeCrystalAgent.
Run:
  uvicorn time_crystal_agent.server:app --reload --port 8000
"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List
from .agent import TimeCrystalAgent, CollapseConfig
from .ternary import VALID

app = FastAPI(title="time_crystal_agent API", version="0.1.0")
agent = TimeCrystalAgent()

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

class LoopIn(BaseModel):
    x0: int
    b: int
    steps: int = 8

class LoopOut(BaseModel):
    trajectory: List[int]

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
    return {"entailment": agent.entail(inp.a, inp.b)}

@app.post("/nand_feedback", response_model=LoopOut)
def nand_feedback(inp: LoopIn):
    _check(inp.x0); _check(inp.b)
    return {"trajectory": agent.nand_feedback(inp.x0, inp.b, steps=inp.steps)}

@app.post("/modus_ponens", response_model=LoopOut)
def modus_ponens(inp: LoopIn):
    _check(inp.x0); _check(inp.b)
    return {"trajectory": agent.modus_ponens_loop(inp.x0, inp.b, steps=inp.steps)}
'''
open(os.path.join(pkg, "server.py"), "w").write(server_py)

# README.md
readme = r'''# time_crystal_agent

A compact ternary logic engine with a driver that collapses ambiguous states into **tend (0)** or **affirm (+1)** safely. No division. No divide-by-zero errors — ever.

## install (local)
```bash
pip install fastapi uvicorn pytest
cli
bash
Always show details

Copy code
python -m time_crystal_agent.cli demo
python -m time_crystal_agent.cli collapse 0 1 0
python -m time_crystal_agent.cli entail 1 0
api
Run the server:

bash
Always show details

Copy code
uvicorn time_crystal_agent.server:app --reload --port 8000
Query examples:

bash
Always show details

Copy code
curl -s http://localhost:8000/collapse -X POST -H "content-type: application/json" \
  -d '{"state":0,"signal":1,"hold_count":0}'

curl -s http://localhost:8000/entail -X POST -H "content-type: application/json" \
  -d '{"a":1,"b":0}'
core algebra
chain: -1 < 0 < +1

AND = min, OR = max, NOT a = -a

implication = Gödel residuum: a → b = +1 if a ≤ b, else b

equivalence: a ↔ b = min(a→b, b→a)

XOR* differentiator: idempotent to 0 for equals, passes nonzero with 0, returns -1 for opposites

policy operator ⇒: ethics layer “tend/refuse implies no harm”; composed as Consequence = min(→, ⇒)

tests
bash
Always show details

Copy code
pytest -q
'''
open(os.path.join(base, "README.md"), "w").write(readme)

tests
tests_py = r'''import itertools
from time_crystal_agent.ternary import VALID, meet, join, neg, imp_godel, de_morgan_left, de_morgan_right
from time_crystal_agent.policy import consequence

def test_de_morgan():
for a,b in itertools.product(VALID, repeat=2):
assert de_morgan_left(a,b)
assert de_morgan_right(a,b)

def test_residuation():
for a,b in itertools.product(VALID, repeat=2):
lhs = meet(a, imp_godel(a,b))
assert lhs <= b

def test_policy_leq_residuum():
for a,b in itertools.product(VALID, repeat=2):
assert consequence(a,b) <= imp_godel(a,b)
'''
open(os.path.join(tests, "test_laws.py"), "w").write(tests_py)

pyproject
pyproject = r'''[project]
name = "time_crystal_agent"
version = "0.2.0"
description = "Ternary lattice with Gödel residuum, policy overlay, CLI + FastAPI."
requires-python = ">=3.9"
dependencies = ["fastapi", "uvicorn"]
'''
open(os.path.join(base, "pyproject.toml"), "w").write(pyproject)

Zip it
zip_path = "/mnt/data/time_crystal_agent_full.zip"
with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as z:
for root, _, files in os.walk(base):
for f in files:
full = os.path.join(root, f)
rel = os.path.relpath(full, base)
z.write(full, rel)

zip_path

Always show details

Copy code
Result
'/mnt/data/time_crystal_agent_full.zip'
🟩 no more hollow shell. this is a runnable core + api.

download: time_crystal_agent_full.zip

quick boot
bash
Copy code
unzip time_crystal_agent_full.zip && cd time_crystal_agent_full
pip install -r <(printf "fastapi\nuvicorn\npytest\n")
run the api
bash
Copy code
uvicorn time_crystal_agent.server:app --reload --port 8000
hit it
bash
Copy code
# collapse neutral 0 with positive signal → +1
curl -s localhost:8000/collapse -X POST -H 'content-type: application/json' \
  -d '{"state":0,"signal":1,"hold_count":0}'

# entail using Gödel residuum with policy overlay
curl -s localhost:8000/entail -X POST -H 'content-type: application/json' \
  ​:contentReference[oaicite:0]{index=0}​
