.PHONY: policy-validate policy-run demo-guard
policy-validate:
\tjq -e . 13/𒀭/policy/c0_gate.v1.json >/dev/null

policy-run:
\tpython3 13/𒀭/agents/chaplin_guard.py | tee -a 13/𒀭/logs/policy.jsonl

demo-guard: policy-validate policy-run
\t@echo "policy demo complete"
