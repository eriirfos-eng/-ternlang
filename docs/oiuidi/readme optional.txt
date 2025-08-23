
(optional) add a line in your top-level `README.md` or docs index that points to `docs/oiuidi/`.

---

# 2) commit + push (choose A or B)

## A) using `gh` CLI (device login, avoids broken browser)
```bash
# install gh if needed, then:
gh auth login -h github.com -p https -w

git clone https://github.com/eriirfos-eng/ternlang.git
cd ternlang
git checkout -b feature/oiuidi-rfp-1.1

mkdir -p docs/oiuidi
# create the three files above (JSON, PY, README.md)

git add docs/oiuidi
git commit -m "docs(oiuidi): add Resonant Flow Protocol v1.1 (spec + python + readme)"
git push -u origin feature/oiuidi-rfp-1.1

# open PR
gh pr create -B main -H feature/oiuidi-rfp-1.1 -t "OIUIDI RFP v1.1" -b "Add protocol spec (JSON), Python reference, and readme. Everything can turn prophet. Preserve flow; if you act, return resonance equal or greater."
