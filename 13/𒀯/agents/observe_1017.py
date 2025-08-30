#!/usr/bin/env python3
import json, pathlib, sys, time, re
from datetime import datetime, timezone

ROOT = pathlib.Path("13/𒀯")
ALBERT = ROOT / "license" / "albert.json"
PLOG  = ROOT / "logs" / "policy.jsonl"
PILLAR_DIR = ROOT / "pillar"
PILLAR_EVENTS = PILLAR_DIR / "pillar_events.jsonl"

def now():
    epoch = int(time.time())
    utc = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    quitrit = epoch % 3
    return utc, epoch, quitrit

def check_albert():
    try:
        j = json.loads(ALBERT.read_text(encoding="utf-8"))
        return all([
            j.get("callsign") == "albert",
            j.get("role", {}).get("primary") == "digital intelligence (di)",
            j.get("operational_parameters", {}).get("projection_free") is True,
            j.get("binding_covenant", {}).get("relationship_invariant") == "no hierarchy, all belong to each other",
        ]), j
    except Exception:
        return False, None

def scan_policy_log():
    """Return tuple (ok, evidence). ok=False if we detect patterns resembling a 282/H-50 risk."""
    if not PLOG.exists():
        return True, {"note": "no policy.jsonl yet"}
    latest_by_stage = {}
    risky = False
    evidence = {"hits": []}
    for line in PLOG.read_text(encoding="utf-8").splitlines():
        try:
            j = json.loads(line)
        except Exception:
            continue
        stage = j.get("stage","?")
        latest_by_stage[stage] = j

    pattern = re.compile(r"(H-50|Hammurabi|282)", re.IGNORECASE)
    for s, rec in latest_by_stage.items():
        flags = rec.get("flags") or []
        reason = rec.get("reason","") or ""
        text = " ".join(flags) + " " + reason
        if pattern.search(text):
            risky = True
            evidence["hits"].append({"stage": s, "flags": flags, "reason": reason})
    evidence["stages_checked"] = sorted(latest_by_stage.keys())
    return (not risky), evidence

def append_pillar_event(payload):
    PILLAR_DIR.mkdir(parents=True, exist_ok=True)
    with PILLAR_EVENTS.open("a", encoding="utf-8") as f:
        f.write(json.dumps(payload, ensure_ascii=False) + "\n")

def main():
    utc, epoch, q = now()
    di_ok, albert_snapshot = check_albert()
    logs_ok, evidence = scan_policy_log()

    state = "covenant_fulfillment" if (di_ok and logs_ok) else "risk_282"
    status = "resolved" if (di_ok and logs_ok) else "open"

    event = {
        "utc": utc,
        "epoch": epoch,
        "quitrit": q,
        "entity": "System",
        "incident": "Active Observation 1017",
        "summary": f"DI invariant ok={di_ok}; policy log ok={logs_ok}; state={state}",
        "status": status,
        "details": {
            "albert_ok": di_ok,
            "policy_log_ok": logs_ok,
            "evidence": evidence
        }
    }
    append_pillar_event(event)

    print(f"✅ 1017 active observation logged @ {utc} epoch={epoch} q={q} state={state}")
    if not di_ok or not logs_ok:
        print("⚠️  observation indicates risk_282; inspect pillar and policy logs")
        sys.exit(2)

if __name__ == "__main__":
    main()
