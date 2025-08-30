# 13/𒀯/make/policy.mk

.PHONY: policy-preflight policy-validate policy-run demo-guard policy-peek

policy-preflight:
	@test -d '13/𒀯' || (echo "rune mismatch: expected 13/𒀯"; exit 1)

policy-validate: policy-preflight
	jq -e . '13/𒀯/policy/c0_gate.v1.json' >/dev/null

policy-run: policy-preflight
	mkdir -p '13/𒀯/logs'
	python3 '13/𒀯/agents/chaplin_guard.py' | tee -a '13/𒀯/logs/policy.jsonl'

demo-guard: policy-validate policy-run
	@echo "policy demo complete"

# Show the latest decision per stage in the terminal
policy-peek:
	@python3 - <<'PY'
import json, pathlib
p = pathlib.Path('13/𒀯/logs/policy.jsonl')
if not p.exists():
    print('no policy.jsonl yet. run: make demo-guard')
    exit(1)
latest = {}
for line in p.read_text(encoding='utf-8').splitlines():
    try:
        j = json.loads(line)
        latest[j.get('stage','?')] = j
    except Exception:
        pass
for i in range(1,14):
    s = f's{i:02d}'
    r = latest.get(s)
    if not r:
        print(f'{s}: —')
    else:
        flags = ' '.join(r.get('flags', []))
        reason = r.get('reason', '')
        print(f'{s}: {r["decision"]} {flags}  {reason}')
PY
