🟩 locked and live. your **time\_crystal\_agent** spine is in place, wired to Gödel residuum, and allergic to divide-by-zero.

[download the zip](sandbox:/mnt/data/time_crystal_agent.zip)

### quickstart

```bash
# unpack and enter
unzip time_crystal_agent.zip && cd time_crystal_agent

# demo runs
python -m time_crystal_agent.cli demo

# collapse: state=0, signal=+1, hold=0  → promotes to +1
python -m time_crystal_agent.cli collapse 0 1 0
```

### embed in your driver

```python
from time_crystal_agent.agent import TimeCrystalAgent, CollapseConfig

ag = TimeCrystalAgent(CollapseConfig(affirm_threshold=1, max_hold_steps=2))

# collapse a neutral read with a mild positive signal
state = 0
signal = 1
next_state = ag.collapse(state, signal, hold_count=0)   # -> +1

# algebraic entailment with policy constraint
y = ag.entail(+1, 0)    # Gödel residuum ∧ policy → 0

# iterate feedback loops
traj1 = ag.nand_feedback(x0=0, b=1, steps=8)     # bounded oscillation or fixpoint
traj2 = ag.modus_ponens_loop(x0=-1, b=0, steps=8)  # converges safely
print(traj1, traj2)
```

### guarantees 🛡️

* inputs hard-clamped to `{−1, 0, +1}`
* `AND=min`, `OR=max`, `NOT a = −a`
* implication = **Gödel residuum** `a→b = +1 if a ≤ b else b`
* policy layer `⇒` only tightens outputs via `Consequence = min(→, ⇒)`
* no division anywhere. zero cannot explode. ever.

### sanity tests

```bash
pip install pytest
pytest -q
```

### fast knobs you can tune

* `affirm_threshold`: raise it if you want 0 to resist collapsing into +1
* `max_hold_steps`: set to 0 if you want instant decisions from 0 when any positive signal arrives
* `allow_recovery_from_minus`: flip to `False` to keep −1 sticky until a manual lift

🟦 want me to wire a skinny REST shim around `entail`, `collapse`, and the two loop ops so your API can ping the agent with `{state, signal}` and get a safe next state in JSON? Or you can do it yourself, or just keep the info in the back of your mind on hold so you dont forget .. ;)
