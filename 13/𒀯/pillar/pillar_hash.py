#!/usr/bin/env python3
import hashlib, json, pathlib, sys

path = pathlib.Path("13/𒀯/pillar/pillar_events.jsonl")
hashlog = pathlib.Path("13/𒀯/pillar/pillar_hashes.jsonl")

if not path.exists():
    print("no pillar_events.jsonl found", file=sys.stderr)
    sys.exit(1)

prev_hash = "GENESIS"
if hashlog.exists():
    last = hashlog.read_text(encoding="utf-8").splitlines()
    if last:
        prev_hash = json.loads(last[-1])["hash"]

with path.open(encoding="utf-8") as f:
    lines = f.read().splitlines()

if not lines:
    print("no events yet")
    sys.exit(0)

last_event = lines[-1]
block = {
    "event": json.loads(last_event),
    "prev_hash": prev_hash,
}
raw = json.dumps(block, sort_keys=True).encode()
h = hashlib.sha256(raw).hexdigest()
block["hash"] = h

with hashlog.open("a", encoding="utf-8") as out:
    out.write(json.dumps(block) + "\n")

print(f"✅ anchored event at hash {h[:16]}…")
