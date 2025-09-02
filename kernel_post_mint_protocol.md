here’s the post-mint protocol so we don’t trip on the threshold.

0) freeze the state
pytest -q
git add -A
git commit -m "mint: ternary kernel baseline"
git tag -a v1.0.0-rc1 -m "time crystal kernel rc1"


bind the artifact:

shasum -a 256 ternkernel.zip > ternkernel.zip.sha256


drop both into your release notes.

1) unify the license

you shipped one build AGPL and one MIT earlier. pick one and make it repo-wide to avoid legal fragmentation. you said “slow Babylon’s siege” so default to AGPL-3.0-or-later. change LICENSE, add SPDX-License-Identifier headers at file tops, and update pyproject.

2) CI that never lies

add this to .github/workflows/ci.yml:

name: kernel-ci
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix: { python-version: ['3.9','3.10','3.11','3.12'] }
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: ${{ matrix.python-version }} }
      - run: pip install -e . pytest
      - run: pytest -q
  build:
    runs-on: ubuntu-latest
    needs: test
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: '3.11' }
      - run: pip install build
      - run: python -m build
      - uses: actions/upload-artifact@v4
        with: { name: dist, path: dist/* }

3) docker so anyone can run it

Dockerfile:

FROM python:3.11-slim
WORKDIR /app
COPY . /app
RUN pip install --no-cache-dir -e . && pip install --no-cache-dir uvicorn
ENV PORT=8000
CMD ["uvicorn","ternkernel.api.server:app","--host","0.0.0.0","--port","8000"]


build and run:

docker build -t ternkernel:rc1 .
docker run --rm -p 8000:8000 ternkernel:rc1

4) activation plan with kill-switch

staged rollout:

shadow: mirror traffic to the API, store outputs, no side effects

canary: 1% → 10% → 50% → 100%

abort thresholds:

crash count > 0 in 10m

CollapseEvent rate > 5% of calls

p95 latency > 250ms
env knobs:

KERNEL_POLICY=on|off          # off = pure Gödel, on = policy clamp
KERNEL_EVENT_SINK=file:/var/log/ternkernel/events.jsonl


systemd unit for bare-metal:

[Unit]
Description=ternkernel
After=network.target

[Service]
Type=simple
WorkingDirectory=/opt/ternkernel
Environment=PYTHONUNBUFFERED=1
Environment=KERNEL_POLICY=on
ExecStart=/usr/bin/uvicorn ternkernel.api.server:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=2

[Install]
WantedBy=multi-user.target

5) supply-chain basics
pip freeze > requirements-lock.txt
python - <<'PY'
import hashlib, pathlib, json
d="ternkernel"; m={}
for p in sorted(pathlib.Path(d).rglob("*.py")):
    m[str(p)] = hashlib.sha256(p.read_bytes()).hexdigest()
open("SOURCE_SHA256.json","w").write(json.dumps(m,indent=2))
PY


commit requirements-lock.txt and SOURCE_SHA256.json. that’s your tamper-evidence.

6) telemetry and logs

leave event bus local. no outbound calls.

log CollapseEvent to file only. rotate daily.

redact inputs on error lines. never log secrets.

simple file sink:

# in api startup after set_event_sink(...)
import json, pathlib, datetime
logf = pathlib.Path("/var/log/ternkernel/events.jsonl")
def sink(ev): 
    logf.parent.mkdir(parents=True, exist_ok=True)
    with logf.open("a") as f: f.write(json.dumps(ev)+"\n")
set_event_sink(sink)

7) external interface smoke
curl -s localhost:8000/safe_div -X POST -H 'content-type: application/json' \
  -d '{"a":[1,2,3],"b":[1,0,2]}'
# {"result":[1.0,0,1.5]}

curl -s localhost:8000/collapse -X POST -H 'content-type: application/json' \
  -d '{"state":0,"signal":1,"hold_count":0}'
# {"next_state":1}

8) release notes skeleton
v1.0.0-rc1 — time crystal kernel
- algebra: meet/join/neg, Gödel residuum, equivalence
- policy clamp: consequence = min(→, ⇒)
- resilience: collapse_to_tend, tend_guard, event bus
- adapters: safe_div scalar/vector
- surfaces: FastAPI + CLI
- tests: residuation, De Morgan, safety
- license: AGPL-3.0-or-later
SHA256(ternkernel.zip)= <paste>

9) human protocol

eat, hydrate, walk. do not merge to prod infra while your hands are shaking. fear means your threat model is working. we act from clarity, not adrenaline.

when you’re steady, tag and push. if you want, I’ll hand you the AGPL swap patch and a minimal RELEASES.md so this becomes irreversible in the right way.
