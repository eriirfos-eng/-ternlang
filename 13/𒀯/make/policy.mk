-policy-validate:
-	jq -e . 13/𒀭/policy/c0_gate.v1.json >/dev/null
+policy-validate:
+	jq -e . 13/𒀯/policy/c0_gate.v1.json >/dev/null

-policy-run:
-	python3 13/𒀭/agents/chaplin_guard.py | tee -a 13/𒀭/logs/policy.jsonl
+policy-run:
+	python3 13/𒀯/agents/chaplin_guard.py | tee -a 13/𒀯/logs/policy.jsonl
