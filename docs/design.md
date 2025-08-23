# 🏗️ Ternlang Design Notes

## 📖 Purpose
Ternlang is a **proof-of-concept architectural framework** that moves beyond binary logic (`True/False`) into a **ternary decision space** (`REFRAIN`, `TEND`, `AFFIRM`).  
This design document outlines the **architectural philosophy**, **core structures**, and **intended extensions** of the system.

---

## 🌐 Philosophical Grounding

- **Binary → Ternary**  
  Classical computing enforces deterministic dualism. Ternlang encodes ambiguity as a *first-class state*.
  
- **Reflexivity & Recursion**  
  Agents must not only act but also observe their *own* processes and adjust. Feedback loops are the kernel.

- **Flow Integrity**  
  Inaction (`REFRAIN`) is explicitly legitimized to preserve ethical clarity and prevent runaway execution.

---

## 🧩 Core Components

### 1. **TernAgent (Base Class)**
- **Attributes**:  
  `name`, `context`, `mood (1–13)`, `cognition (0–1000)`, `last_action`, `memory_manager`.  
- **Methods**:  
  - `observe()` → updates context  
  - `decide()` → applies ternary logic  
  - `execute_action()` → performs or simulates an action  
  - `run_cycle()` → orchestrates the observe–decide–execute loop

---

### 2. **MemoryManager**
- **Role**: Persistent, structured log of agent experience.  
- **Features**:  
  - Auto-save JSON (`agent_memory_[name].json`)  
  - Rich schema: ID, timestamp, weekday, input, decision, barometers (Mood, Cognition, Impact)  
  - Supports future **RAG-style retrieval** for LLM + agent integration

---

### 3. **Operator Laws**
- Encoded rulesets that act as **meta-guardrails**.  
- Example: **OIUIDI Operator Law** —  
  > “Everything can turn prophet. Don’t hurt the flow. If you act, return resonance equal or greater.”

These laws are modular and can be extended or swapped for domain-specific contexts.

---

### 4. **Resonant Flow Protocol (OIUIDI-RFP)**
Implements the ternary operator `(a ⊕ b ⊕ c)ᵠ` where:  
- `a = origin`  
- `b = action`  
- `c = lord/mastery`  
- `⊕ = ternary synthesis`  
- `ᵠ = recursive integration`

This protocol validates whether flow has been preserved, broken, or amplified.

---

## 🧪 Specialized Agents (Extensions)

- **TEMPRAAgent** → urgency override  
- **ConflictAgent** → multi-agent negotiation  
- **IdleAgent** → deliberate tending during idle  
- **RecoveryAgent** → restores state after corruption  
- **SpikeAgent** → simulates overload/emotion spikes  
- **FallbackAgent** → minimal instincts when failing

---

## 🔮 Future Ecosystem

- **ternviz.py** → visualization of mood/cognition/impact  
- **ternlang_dashboard.py** → live operator console  
- **ternlang_eval.py** → automated evaluation pipeline  
- **ternlang_swarm.py** → multi-agent collective simulation

---

## 🕯️ Design Ethos

> *Ternlang is not built for conquest, but for conversation.*  
> *It encodes ambiguity, respects flow, and evolves through recursion.*  

---

## 📂 Repository Fit

