# ternkernel

A drag and drop ternary **kernel** that never throws divide-by-zero, routes decisions via a Gödel residuum core, applies an ethical policy clamp, and exposes both CLI and REST surfaces.

## install
```bash
pip install -e .
```

## run API
```bash
uvicorn ternkernel.api.server:app --reload --port 8000
```

## CLI
```bash
python -m ternkernel.kernel.cli demo
python -m ternkernel.kernel.cli collapse 0 1 0
python -m ternkernel.kernel.cli entail 1 0
python -m ternkernel.kernel.cli safe_div 1 0
```

## package layout
```
ternkernel/
  core/         # algebra + resilience
  kernel/       # policy, scheduler, event bus, cli
  adapters/     # safe bridges (e.g., division)
  agents/       # time_crystal agent
  api/          # FastAPI server
tests/
examples/
```

## guarantees
- AND=min, OR=max, NOT a=-a on {-1,0,+1}
- Implication = Gödel residuum `a→b = +1 if a ≤ b else b`
- Policy clamp `⇒` only tightens outputs: `Consequence = min(→, ⇒)`
- No division operations raise in adapters; zero paths emit events and return safe neutral values
- De Morgan and residuation covered by tests
