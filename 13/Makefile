# simple ops for ternlang/13
PY ?= python3
PIP ?= pip3

CONFIG_DIR := ternlang/13/master_docs

.PHONY: help install validate run-demo lint seal

help:
	@echo "targets:"
	@echo "  install   -> install minimal deps"
	@echo "  validate  -> load and validate stage_01..13.json, print 𒀭 seal"
	@echo "  run-demo  -> run a quick demo packet through the host"
	@echo "  seal      -> print the 𒀭 seal message alone"
	@echo "  lint      -> no-op placeholder (add your linter of choice)"

install:
	$(PIP) install -r ternlang/13/requirements.txt

validate:
	@PYTHONPATH=ternlang/13 $(PY) - << 'PYCODE'
import os
from config_io import load_master_docs, ConfigError
from utils.seal import print_seal
try:
    docs = load_master_docs(os.path.join("ternlang","13","master_docs"))
    print_seal("validated config set")
except ConfigError as e:
    raise SystemExit(f"[config] {e}")
PYCODE

run-demo:
	@PYTHONPATH=ternlang/13 $(PY) - << 'PYCODE'
import os
from config_io import load_master_docs, ConfigError
from utils.seal import print_seal
from ternary_host import TernaryLogicAgent  # assumes agent class is defined in host

try:
    master_docs = load_master_docs(os.path.join("ternlang","13","master_docs"))
    print_seal("validated config set")
except ConfigError as e:
    raise SystemExit(f"[config] {e}")

agent = TernaryLogicAgent(master_docs)
packet = {"sensor_readings": {"temp": 25, "pressure": "stable"},
          "source": "natural fractal",
          "notes": "bird flock coherence"}
agent.process_data_stream(packet)
PYCODE

seal:
	@PYTHONPATH=ternlang/13 $(PY) - << 'PYCODE'
from utils.seal import print_seal
print_seal("manual seal print")
PYCODE

lint:
	@echo "lint placeholder. wire ruff or flake8 when you like."

# ternlang/13/ternary_host.py
from config_io import load_master_docs, ConfigError
from utils.seal import print_seal

def bootstrap_agent():
    import os
    CONFIG_DIR = os.path.join(os.path.dirname(__file__), "master_docs")
    try:
        master_docs = load_master_docs(CONFIG_DIR)
    except ConfigError as e:
        raise SystemExit(f"[config] {e}")
    print_seal("validated config set")
    return TernaryLogicAgent(master_docs)
.PHONY: run-demo-logs tail-logs clean-logs

run-demo-logs:
	@PYTHONPATH=ternlang/13 $(PY) - << 'PYCODE'
import os, glob
from config_io import load_master_docs, ConfigError
from utils.seal import print_seal
from utils.jsonl_logger import JSONLLogger
from ternary_host import TernaryLogicAgent

CONFIG_DIR = os.path.join("ternlang","13","master_docs")
LOG_DIR = os.path.join("ternlang","13","logs")

try:
    md = load_master_docs(CONFIG_DIR)
    print_seal("validated config set")
except ConfigError as e:
    raise SystemExit(f"[config] {e}")

logger = JSONLLogger(LOG_DIR)
agent = TernaryLogicAgent(md, logger=logger)
packet = {"sensor_readings": {"temp": 25, "pressure": "stable"},
          "source": "natural fractal",
          "notes": "bird flock coherence"}
agent.process_data_stream(packet)
print(f"[logs] wrote to: {logger.path}")
PYCODE

tail-logs:
	@python3 - << 'PYCODE'
import os, glob
paths = sorted(glob.glob("ternlang/13/logs/run_*.jsonl"))
if not paths:
    raise SystemExit("no log files yet")
print(paths[-1])
with open(paths[-1], "r", encoding="utf-8") as f:
    for i, line in enumerate(f):
        if i > 50: break
        print(line.rstrip())
PYCODE

clean-logs:
	rm -f ternlang/13/logs/run_*.jsonl


