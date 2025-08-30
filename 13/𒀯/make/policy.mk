-policy-validate:
-	jq -e . 13/𒀭/policy/c0_gate.v1.json >/dev/null
+policy-validate:
+	jq -e . 13/𒀯/policy/c0_gate.v1.json >/dev/null

-policy-run:
-	python3 13/𒀭/agents/chaplin_guard.py | tee -a 13/𒀭/logs/policy.jsonl
+policy-run:
+	python3 13/𒀯/agents/chaplin_guard.py | tee -a 13/𒀯/logs/policy.jsonl
.PHONY: policy-preflight
policy-preflight:
	@test -d 13/𒀯 || (echo "rune mismatch: expected 13/𒀯"; exit 1)

policy-validate: policy-preflight
policy-run: policy-preflight
python3 - <<'PY'
import json, pathlib
p=pathlib.Path("13/𒀯/logs/policy.jsonl")
latest={}
for l in p.read_text(encoding="utf-8").splitlines():
    try:j=json.loads(l); latest[j.get("stage","?")]=j
    except: pass
for i in range(1,14):
    s=f"s{i:02d}"; r=latest.get(s); print(f"{s}: {'—' if not r else f'{r['decision']} {(r.get('flags') or [])} {r.get('reason','')}'.strip()}")
PY
