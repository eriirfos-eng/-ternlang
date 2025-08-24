# 𒀭 ternlang/13 — quick cheat sheet

minimal brain map for the ternary lattice. keep it near the code, keep it honest.

## color flags
- 🟜 refrain = disconfirm / abort
- 🟫 tend = observe / neutral
- ⬛ affirm = act / execute
- 🟦 anchor = calm reference
- 🟩 flow = good momentum
- 🟧 tension = rising priority
- 🟥 critical = immediate action

## stage map (13)
1) s01 ingress 🟦 — raw intake. no judgment.  
2) s02 triage 🟦 — tag signal, noise, ambiguous.  
3) s03 eco-weights 🟩 — biodiversity, atmosphere, geology.  
4) s04 intent 🟫 — sentient, natural, random, synthetic, artifact.  
5) s05 ambiguity 🟧 — too fuzzy → collapse to tend.  
6) s06 refrain 🟥 — harm taxonomy → abort path.  
7) s07 affirm ⬛ — alignment score gates the green light.  
8) s08 veto 🟧 — ecocentric red lines override any green.  
9) s09 resolve 🟫 — collapse to {refrain|tend|affirm}.  
10) s10 action 🟩 — execute, do nothing, abort.  
11) s11 outcome 🟦 — match, surprises, impact, trust.  
12) s12 feedback 🟫 — reinforce, attenuate, neutralize.  
13) s13 reset 🟦 — soft or hard return to base tend.

## where stuff lives
- configs: `master_docs/stage_*.json`  
- schema: `master_docs/schema.json`  
- host: `ternary_host.py`  
- loader: `config_io.py`  
- utils: `utils/seal.py`, `utils/flags.py`, `utils/jsonl_logger.py`  
- logs: `logs/run_<id>_NNN.jsonl`

## runbook
```bash
make install        # deps
make validate       # load + schema check → prints 𒀭 seal
make run-demo       # quick console demo
make run-demo-logs  # demo + jsonl file
make tail-logs      # show head of latest jsonl
make clean-logs     # purge logs
