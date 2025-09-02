
# MetaAgent

The MetaAgent fuses three layers of governance:

1. **SupervisorAgent** → external override, high clarity, swarm governor
2. **MetaReflectionAgent** → internal self-check, loop breaker, stagnation monitor
3. **Policy Mirror Protocol (PMP)** → ethical refusal boundary, transparency + traceability

This composite agent acts as the "governor of governors."

- Every decision is routed through ternary logic (-1=REFRAIN, 0=TEND, +1=AFFIRM).
- Swarm outputs + self-reflection scores are fused via 1+1=3 principle (synergy bonus).
- A 100% failsafe is enforced: 90% secure, 10% uncertainty budget. Affirm never survives if uncertainty >0.10.

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -r requirements.txt

# run a meta-agent decision
python -m meta_agent run --context "agents are conflicted, supervisor says REFRAIN, reflection says TEND"
```

## Architecture

```
Swarm Agents → SupervisorAgent ┐
                                ├─> MetaAgent (fuses ternary + PMP)
MetaReflectionAgent ────────────┘

MetaAgent → final ternary decision (REFRAIN/TEND/AFFIRM) + PMP state (NORMAL..TERMINATED)
```

## Files

- `core.py` — MetaAgent implementation
- `cli.py` — command-line runner
- `schemas/` — JSON schemas for config + result
- `tests/` — pytest-based checks
