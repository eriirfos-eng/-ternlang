import argparse, re, pathlib, sys

BADGE = {
    "WARNED": "🟨 warn",
    "COOLDOWN": "🟧 cooldown",
    "LOCKED": "🟥 locked",
    "TERMINATED": "◼ terminated",
    "NORMAL": "🟦 normal"
}

def parse_matrix(md: str):
    lines = md.splitlines()
    rows = []
    for ln in lines:
        m = re.match(r"-\s+(✅|❌)\s+\*\*(.+?)\*\*\s+→\s+`(.+?)`", ln.strip())
        if m:
            ok = m.group(1) == "✅"
            tid = m.group(2)
            state = m.group(3)
            rows.append((ok, tid, state))
    return rows

def build_comment(rows):
    total = len(rows)
    passed = sum(1 for r in rows if r[0])
    badges = {}
    for _, _, state in rows:
        badges[state] = BADGE.get(state, "🟫 tend")

    header = f"**pmp check** • {passed}/{total} pass"
    badge_line = " | ".join(sorted(set(badges.values())))
    table = ["", "| test | state |", "|---|---|"]
    for ok, tid, st in rows:
        emoji = "✅" if ok else "❌"
        table.append(f"| {emoji} {tid} | `{st}` |")
    return header + "\n" + badge_line + "\n" + "\n".join(table)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--matrix", required=True, help="path to matrix.md produced by pmp-agent")
    ap.add_argument("--out", required=True, help="where to write PR-ready markdown")
    args = ap.parse_args()

    md = pathlib.Path(args.matrix).read_text(encoding="utf-8")
    rows = parse_matrix(md)
    comment = build_comment(rows)
    pathlib.Path(args.out).write_text(comment, encoding="utf-8")
    print(comment)

if __name__ == "__main__":
    main()
