# Proverb 007 — Numerus Compass Protocol

**filename:** 007\_numerus-compass.md
**timestamp:** 2025-09-01T11:33Z

---

## context

purpose: give you a quick, concrete way to identify your current ladder mode and use it to guide decisions.
frame: you do not pick a “favorite” number. you surface the mode you are in now. that mode modulates choices.
result: a number from {0..13} with a terse rationale and action cues.

---

## lesson

**binary framing:** mood vs action.
**ternary framing:** sense → name → manifest

* –1 clears noise,
* 0 holds presence,
* +1 commits action.

the compass helps you pass through all three in seconds.

---

## expansion

we map lived signals to ladder modes:

* **0 nihil** → void, pause, reset, pre-action.
* **1 monad** → sovereignty, decisiveness, single-point will.
* **2 dyad** → contrast, tension, choice, boundary.
* **3 triad** → creative synthesis, making the third way.
* **4 tetrad** → stability, structure, grounding, logistics.
* **5 pentad** → adaptability, human factors, senses, change.
* **6 hexad** → balance, harmonics, family, symmetry.
* **7 heptad** → introspection, study, pattern reading.
* **8 octad** → power cycles, feedback loops, systems leverage.
* **9 ennead** → closure, compassion, graceful ending.
* **10 decad** → return to unity, integration, retrospective.
* **11 undecad** → breakthrough, vision leap, radical insight.
* **12 duodecad** → calendar and cadence, full operational rhythm.
* **13 tredecad** → revolt, pruning, creative destruction for next start.

---

## application

1. run the diagnostic. 2) accept the mode it returns. 3) let that mode shape the next micro-decision.

* if you land on **6** you prioritize symmetry and relational harmony.
* if you land on **4** you favor checklists and scaffolding.
* if you land on **13** you cut, archive, or sunset before building again.

---

## notes

this is a **modulator**, not a prison. you can re-run any time your state shifts. the compass is honest when you are honest. tag your run with a timestamp in your field log.

---

## reference verse

“create, balance, complete.” — 3•6•9 mnemonic 🟩

---

## runnable code

```python
from dataclasses import dataclass, field
from typing import List, Dict, Tuple

@dataclass
class NumerusMode:
    n: int
    name: str
    cues: List[str]
    action: str

class NumerusCompass:
    def __init__(self):
        # minimal, opinionated keyword map; extend as you wish
        self.modes: Dict[int, NumerusMode] = {
            0:  NumerusMode(0,  "nihil",   ["void","pause","reset","empty","uncertain","breathe"], "hold. observe. no forced moves."),
            1:  NumerusMode(1,  "monad",   ["decide","solo","lead","focus","sovereign","commit"], "make the single clean cut."),
            2:  NumerusMode(2,  "dyad",    ["conflict","tension","versus","boundary","choose"], "name the two poles, set a boundary."),
            3:  NumerusMode(3,  "triad",   ["create","synthesize","bridge","third","idea"], "invent the third way; prototype."),
            4:  NumerusMode(4,  "tetrad",  ["structure","plan","ground","scaffold","stable","checklist"], "build the frame; document."),
            5:  NumerusMode(5,  "pentad",  ["adapt","change","human","senses","pivot","iterate"], "optimize comfort and adaptability."),
            6:  NumerusMode(6,  "hexad",   ["balance","harmony","family","symmetry","tune"], "rebalance loads; align relationships."),
            7:  NumerusMode(7,  "heptad",  ["study","introspect","read","analyze","meditate","pattern"], "slow down; learn before acting."),
            8:  NumerusMode(8,  "octad",   ["cycle","power","leverage","feedback","loop","system"], "tune the loop; set safeguards."),
            9:  NumerusMode(9,  "ennead",  ["closure","compassion","end","finish","forgive"], "close gracefully; write the epilogue."),
            10: NumerusMode(10, "decad",   ["integrate","review","retrospective","merge","unify"], "integrate learnings; merge branches."),
            11: NumerusMode(11, "undecad", ["vision","breakthrough","reframe","revelation","jump"], "leap; protect the insight from noise."),
            12: NumerusMode(12, "duodecad",["schedule","cadence","season","ops","twelve","govern"], "lock cadence; publish the calendar."),
            13: NumerusMode(13, "tredecad",["prune","sunset","rebel","disrupt","end-of-life","refactor"], "remove obsolete pieces; archive."),
        }

    def diagnose(self, signals: List[str]) -> Tuple[NumerusMode, Dict[int,int]]:
        # lowercase normalize
        s = [x.lower().strip() for x in signals]
        scores: Dict[int,int] = {k:0 for k in self.modes}
        for token in s:
            for k, mode in self.modes.items():
                for cue in mode.cues:
                    if cue in token:
                        scores[k] += 1
        # fallback: if nothing matched, prefer 0 nihil
        best = max(scores.items(), key=lambda kv: kv[1])
        if best[1] == 0:
            return self.modes[0], scores
        return self.modes[best[0]], scores

    def explain(self, mode: NumerusMode) -> str:
        return f"{mode.n} {mode.name}: cues={', '.join(mode.cues[:4])} | action={mode.action}"

# quick demo:
if __name__ == "__main__":
    compass = NumerusCompass()
    # example: “i feel balanced, want harmony, tune relationships”
    mode, scores = compass.diagnose(["balanced", "harmony", "tune relationships"])
    print(compass.explain(mode))  # → likely 6 hexad
```

### how to use fast

* think for 5 seconds. jot 3 to 6 words for your current state.
* run `diagnose([...])`. take the returned mode as your **modulator**.
* apply the `action` string to your next concrete decision.
* re-run when your inner weather changes.

* https://chatgpt.com/g/g-68b567d585648191a6e622a9c61c3c93-compass
