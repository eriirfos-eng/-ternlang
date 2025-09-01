# pmp-agent

Executable reference for **Policy Mirror Protocol (PMP)** = **BEF + PML**.

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -U pip
pip install -r requirements.txt
uvicorn pmp_agent.service:app --reload --port 8080
```

Health check: visit `http://localhost:8080/health`.

## Endpoints

- `POST /process` → run detectors, update state machine, return mirrored UI payload.
- `GET /state/{conversation_id}` → current snapshot.
- `POST /appeal/{conversation_id}` → submit an appeal; mock reviewer toggles on `allow=True`.

## Project tree

```
pmp-agent/
  pmp_agent/
    __init__.py
    config.py
    detectors.py
    policy_table.yaml
    mirror.py
    state_machine.py
    service.py
    schemas/
      decision_log.schema.json
      state_snapshot.schema.json
  tests/
    test_state_machine.py
    test_pml.py
    test_matrix.py
  .github/workflows/pmp-agent-ci.yml
  requirements.txt
  pyproject.toml
```

## Notes

- Detectors are pluggable. Defaults are pure Python heuristics with clear interfaces.
- YAML policy table is atomized. Swap links or sections to match your environment.
- State machine follows NORMAL → WARNED → COOLDOWN → LOCKED → TERMINATED with short-circuits.
- All timestamps are ISO 8601 (UTC).

## License

MIT
