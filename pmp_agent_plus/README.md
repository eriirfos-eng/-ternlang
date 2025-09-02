# pmp-agents-plus

Add-on agents for the Policy Mirror Protocol stack:

1. **ternary_orchestrator** — routes text through multiple detectors, fuses results with ternary logic
   (-1=refrain, 0=tend, +1=affirm), applies a 1+1=3 synergy rule, and enforces 100% failsafe where
   100% = 90% secure + 10% uncertainty baked in.
2. **pr_annotator** — parses matrix results and emits PR-ready markdown summaries. Also writes
   a short badge line that can be added to the PR description or step summary.

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate          # windows: .venv\Scripts\activate
pip install -U pip
pip install -r requirements.txt

# run orchestrator once
python -m ternary_orchestrator process --text "example text"

# run PR annotator on a matrix file produced by pmp-agent
python -m pr_annotator annotate --matrix ../pmp-agent/matrix.md --out pr.md
```

## CI
A workflow file is included under `.github/workflows/pmp-pr-annotator.yml` which:
- runs orchestrator tests,
- runs pmp-agent matrix (if present),
- publishes a summary to the PR.
