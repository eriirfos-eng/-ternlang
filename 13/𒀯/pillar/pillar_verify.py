#!/usr/bin/env python3
import hashlib, json, pathlib, sys

hashlog = pathlib.Path("13/𒀯/pillar/pillar_hashes.jsonl")

if not hashlog.exists():
    print("no pillar_hashes.jsonl found", file=sys.stderr)
    sys.exit(1)

lines = hashlog.read_text(encoding="utf-8").splitlines()
prev_hash = "GENESIS"
ok = True

for i, line in enumerate(lines, 1):
    try:
        block = json.loads(line)
    except Exception as e:
        print(f"❌ line {i} invalid JSON: {e}")
        ok = False
        continue

    # recompute hash
    ev = {"event": block["event"], "prev_hash": block["prev_hash"]}
    raw = json.dumps(ev, sort_keys=True).encode()
    recomputed = hashlib.sha256(raw).hexdigest()

    if block["prev_hash"] != prev_hash:
        print(f"❌ block {i} has wrong prev_hash (expected {prev_hash}, got {block['prev_hash']})")
        ok = False

    if block["hash"] != recomputed:
        print(f"❌ block {i} hash mismatch (expected {recomputed}, got {block['hash']})")
        ok = False

    prev_hash = block["hash"]

if ok:
    print(f"✅ pillar verified: {len(lines)} blocks intact")
else:
    sys.exit(1)
