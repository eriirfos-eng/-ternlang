.PHONY: install dev run api test matrix validate

PY ?= python3
PIP ?= pip3

install:
	$(PIP) install -r requirements.txt

dev: install
	$(PY) -m pmp_agent --help || true

run:
	uvicorn pmp_agent.service:app --port 8080 --reload

api: run

test:
	pytest -q

matrix:
	$(PY) -m pmp_agent run-matrix --matrix examples/matrix.json --summary matrix.md
	@echo 'wrote matrix.md'

validate:
	$(PY) -m pmp_agent validate --schema pmp_agent/schemas/test_matrix.schema.json --data-glob 'examples/*.json' --strict
