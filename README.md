# Ternlang

**Ternlang** is a proof-of-concept architectural framework that redefines the very essence of computational logic.  
Where binary systems halt at `True/False`, Ternlang introduces a **ternary foundation** — `REFRAIN (-1)`, `TEND (0)`, `AFFIRM (+1)` — enabling digital entities to *navigate ambiguity, manage conflict, and act with nuanced intent*.

---

## Vision: Beyond Assistants, Toward Digital Entities

Ternlang is not about better assistants. It is about engineering **true digital entities** — agents that are:

- **Self-Aware** 🪞 — aware of their internal state and limitations.  
- **Adaptive** 🌱 — evolving behavior through feedback and experience.  
- **Metacognitive** 🔁 — reflecting on their own processes and learning loops.  
- **Accountable** 📜 — making logged, transparent decisions.  
- **Resilient** 🛡️ — recovering from failure, navigating uncertainty, persisting.

The long-term aim: a *“factory state”* for self-aware, continuously evolving, metacognitive agents capable of independent operation across domains.

---

## Core Principles

- **Ternary Logic**:  
  - `REFRAIN (-1)` — deliberate inaction, caution, pause.  
  - `TEND (0)` — observe, adjust, nurture, deliberate.  
  - `AFFIRM (+1)` — engage, commit, execute.  

- **Recursive Agency** — agents modify their behavior through self-monitoring and feedback loops.  
- **Inaction as Valid Outcome** — doing nothing is a legitimate, ethical choice.  
- **Contextual Awareness** — agents update their state continuously based on observation.  
- **Internal State Dynamics** — barometers (Mood, Cognition, Impact) model well-being & operational capacity.  
- **Conversation over Conquest** — decision via negotiation, not domination.  
- **Continuous Learning & Adaptation** — behavior evolves via reflection and logged experience.  
- **Resilience & Self-Preservation** — detect corruption, recover, ensure survivability.

---

##  Architecture

- **`ternlang_prototype.py`** — base `TernAgent` class (Observe-Decide-Execute loop).  
- **`ternlang_memory_manager.py`** — persistent memory manager (structured JSON logs, auto-save, RAG-ready).  
- **Examples** — specialized agents extending the base:
  - `TEMPRAAgent` — urgency override  
  - `ConflictAgent` — negotiation/consensus  
  - `IdleAgent` — proto-curiosity, reflection cycles  
  - `RecoveryAgent` — self-healing after corruption  
  - …and more (`SpikeAgent`, `FallbackAgent`, etc.)

Planned ecosystem: `ternviz` (visualization), `ternlang_dashboard` (GUI), `ternlang_eval` (evaluation), `ternlang_swarm` (multi-agent playground).

---

## 📚 Documentation Index

- [docs/](./docs) — concepts, semantics, architecture
  - [Design Notes](./docs/design.md)
  - [Operator Laws](./docs/OIUIDI_OperatorLaw Algorithm v1.0.py)
  - [OIUIDI Resonant Flow Protocol](./docs/oiuidi/README.md)  
    - [Spec (JSON)](./docs/oiuidi/oiuidi_rfp_v1_1.json)  
    - [Reference Implementation (Python)](./docs/oiuidi/oiuidi_rfp.py)

---

## 🛠️ Usage

```bash
# clone the repository
git clone https://github.com/eriirfos-eng/ternlang.git
cd ternlang

# run a demo cycle
python ternlang_prototype.py
