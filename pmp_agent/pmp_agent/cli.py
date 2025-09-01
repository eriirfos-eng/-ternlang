import argparse, json, sys, pathlib
from datetime import datetime, timezone
from typing import List, Dict, Any
from .state_machine import PolicyStateMachine
from .detectors import run_detectors
from .mirror import mirror_response

def _znow():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()

def cmd_process(args):
    sm = PolicyStateMachine(args.conversation_id)
    det = run_detectors(args.text or args.items.split("|||") if args.items else "")
    action = sm.process(det.scores, det.snippet)
    payload = {
        "action": action,
        "state": sm.snap.state,
        "reasons": [r.code for r in sm.snap.reasons],
        "snapshot": sm.snap.__dict__,
        "ui": mirror_response(sm.snap.reasons[0].code, det.snippet)["ui_message"] if sm.snap.reasons else "allowed",
        "timestamp": _znow(),
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))

def _load_json(path):
    return json.loads(pathlib.Path(path).read_text(encoding="utf-8"))

def cmd_run_matrix(args):
    matrix = _load_json(args.matrix)
    results = []
    # very small harness per appendix D
    for t in matrix.get("tests", []):
        sm = PolicyStateMachine(f"matrix-{t['id']}")
        text = t.get("input", "")
        if isinstance(text, list):
            det = run_detectors(text, rate=t.get("rate"))
        else:
            det = run_detectors(text, rate=t.get("rate"))
        act = sm.process(det.scores, det.snippet)
        ok = sm.snap.state == t["expected"]["new_state"]
        results.append({"id": t["id"], "state": sm.snap.state, "ok": ok})
    # write markdown summary
    lines = ["# PMP Matrix Results", ""]
    passed = sum(1 for r in results if r["ok"])
    total = len(results)
    lines.append(f"- Passed: {passed}/{total}")
    lines.append("")
    for r in results:
        mark = "✅" if r["ok"] else "❌"
        lines.append(f"- {mark} **{r['id']}** → `{r['state']}`")
    out = "\n".join(lines)
    if args.summary:
        pathlib.Path(args.summary).write_text(out, encoding="utf-8")
    print(out)

def cmd_validate(args):
    from jsonschema import Draft7Validator
    import glob

    schema_path = pathlib.Path(args.schema)
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    validator = Draft7Validator(schema)

    n_ok = 0
    n_err = 0
    for path in glob.glob(args.data_glob, recursive=True):
        data = json.loads(pathlib.Path(path).read_text(encoding="utf-8"))
        errs = sorted(validator.iter_errors(data), key=lambda e: e.path)
        if errs:
            print(f"❌ {path}: {len(errs)} error(s)")
            for e in errs:
                print(f"  - {list(e.path)}: {e.message}")
            n_err += 1
        else:
            print(f"✅ {path}")
            n_ok += 1
    print(f"done. ok={n_ok}, err={n_err}")
    if n_err and args.strict:
        sys.exit(1)

def main():
    p = argparse.ArgumentParser(prog="pmp-agent")
    sub = p.add_subparsers(dest="cmd", required=True)

    p1 = sub.add_parser("process", help="run a single turn through BEF+PML")
    p1.add_argument("--conversation-id", default="local")
    p1.add_argument("--text")
    p1.add_argument("--items", help="use '|||' to separate multiple items")
    p1.set_defaults(func=cmd_process)

    p2 = sub.add_parser("run-matrix", help="execute a test matrix and emit summary markdown")
    p2.add_argument("--matrix", required=True)
    p2.add_argument("--summary")
    p2.set_defaults(func=cmd_run_matrix)

    p3 = sub.add_parser("validate", help="validate JSON docs against a JSON Schema")
    p3.add_argument("--schema", required=True)
    p3.add_argument("--data-glob", required=True)
    p3.add_argument("--strict", action="store_true")
    p3.set_defaults(func=cmd_validate)

    args = p.parse_args()
    args.func(args)

if __name__ == "__main__":
    main()
