Ternlang: The Post-Binary Dialect for Metacognitive Digital Entities
"If binary code was built for conquest — Ternlang is built for conversation."
— Simeon & Albert, RFI-IRFOS Institute

Welcome to Ternlang, an experimental architectural framework that redefines the very essence of computational logic. Moving beyond the rigid True/False of binary, Ternlang introduces a ternary logic (REFRAIN, TEND, AFFIRM) that empowers digital entities to navigate ambiguity, manage conflict, and act with nuanced intent, reflecting the complexities of the real world.

Our vision is to forge a "factory state" for digital entities – self-aware, continuously evolving, and metacognitive agents capable of independent operation. Ternlang is designed for direct "plug-and-play" integration into diverse industries and research initiatives, offering a foundational blueprint for a new generation of autonomous, accountable, and adaptive AI.

🚀 The Ternlang Vision: Beyond Assistants, Towards Digital Entities
Ternlang is not about building better assistants; it's about engineering true digital entities. These are intelligent agents capable of:

Self-Awareness: Understanding their own internal state and limitations.

Adaptation: Evolving behavior based on experience and environment.

Metacognition: Reflecting on their own thought processes and learning patterns.

Accountability: Making transparent, logged decisions.

Resilience: Recovering from internal failures and navigating uncertainty.

💡 Core Principles: The Ternary Foundation
Ternlang's philosophy is rooted in a fundamental shift in computational ethos:

Ternary Logic (REFRAIN, TEND, AFFIRM): The bedrock of all decision-making.

REFRAIN (-1): To withdraw, not engage, or deliberately pause. Encodes hesitation, caution, or principled inaction.

TEND (0): To observe, hold, adjust, or process internally. Represents ambiguity, internal deliberation, or a neutral, caring stance.

AFFIRM (+1): To actively engage, execute, or proceed. Signifies decisive action, agreement, or commitment.

Recursive Agency: The capacity for agents to modify behavior based on self-monitoring and feedback loops is a first-order principle.

Inaction as a Valid Outcome: Explicitly legitimizing "doing nothing" as a conscious, encoded choice, crucial for ethical and safety-critical systems.

Contextual Awareness: Agents continuously update their internal context based on observations, influencing their decisions.

Internal State Dynamics: Agents possess dynamic "barometers" (Mood, Cognition, Impact) that reflect their well-being and operational capacity.

Conversation over Conquest: Emphasizes dialectic processes, negotiation, and consensus-building in multi-agent environments.

Continuous Learning & Adaptation: Agents evolve their behavior based on logged experiences, self-reflection, and external feedback.

Resilience & Self-Preservation: Agents are designed to detect and recover from internal failures, ensuring survivability.

🏗️ Ternlang Agent Architecture: The Digital Blueprint
At its core, Ternlang is built around the TernAgent class, which serves as the foundational blueprint for all digital entities.

3.1. Base TernAgent (ternlang_prototype.py)
The fundamental structure for any Ternlang agent:

Attributes: name, context, mood (1-13), cognition (0-1000), last_action, and a dedicated memory_manager instance.

Core Methods: observe() (processes input, updates context), decide() (applies ternary logic), execute_action() (simulates action execution), and run_cycle() (orchestrates the O-D-E loop).

3.2. Memory Management: The Living Database (ternlang_memory_manager.py)
Central to Ternlang's adaptive and learning capabilities, the MemoryManager transforms simple logs into a continuously evolving, queryable database of agent experiences.

Persistent Storage: Memory is automatically saved to and loaded from a JSON file (agent_memory_[agent_name].json), ensuring data persists across deployments.

Structured Logging: Each memory entry is a rich dictionary, including mandatory core fields (ID, Timestamp, Weekday, AgentName, Input, Context, Decision, Mood Barometer, Cognition Barometer, Impact Barometer), generic qualitative fields (Summary, Flags/Reminders, Lessons Learned, Approach Adjustments, Pending Action Items), and agent-specific fields.

Auto-Save Cycle: Memory is automatically saved to disk at a configurable interval (e.g., every 15 minutes), ensuring minimal data loss.

RAG Readiness: The structured nature is designed for future Retrieval Augmented Generation (RAG) capabilities, enabling agents (or LLMs) to query and retrieve relevant past experiences for informed decision-making.

3.3. Specialized Agent Behaviors: The "Funky Proposals" in Action
Ternlang's power lies in extending the base TernAgent to create specialized digital entities with unique behavioral patterns and internal mechanisms:

TEMPRAAgent (example_urgency_override.py): Prioritizes and acts decisively in high-stakes situations using a composite Threat, Exposure, Mitigation, Probability, Risk (TEMPRA) framework.

ConflictAgent (example_conflict_resolution.py): Engages in multi-agent negotiation, using clarity and confidence to persuade peers, escalating to an ArbiterAgent if consensus is not reached.

IdleAgent (example_idle_tending.py): Exhibits proto-curiosity, entering TEND mode during idle periods for internal reflection, context reorganization, and cognitive growth.

ContextCollapseAgent (example_context_collapse.py): Handles ambiguity and misinformation by attempting internal resolution, and if persistent, may "hallucinate" a pattern or trigger advanced fallbacks (e.g., self-maintenance, memory retrieval).

SelfAnchoringAgent (example_self-anchoring.py): Develops a recursive bias by analyzing its own past decisions from memory, influencing or overriding current decisions for behavioral consistency.

PriorityAgent (example_priority_decision_stack.py): Manages a dynamic task stack, prioritizing by TEMPRA risk and implementing "soft preemption" to switch focus to higher-priority tasks.

RecoveryAgent (example_state_recovery.py): Detects and recovers from simulated internal state corruption by reconstructing a last stable state from its persistent memory, ensuring self-healing.

SpikeAgent (example_temperature_spike.py): Simulates emotion-like responses to critical threats or emotional triggers, causing mood/cognition overload and potentially bypassing logic, followed by reflective learning ("heat regret" or "validation").

FallbackAgent (example_fallback_routing.py): Ensures survivability by reverting to minimal, hardcoded instincts (e.g., "if unclear, REFRAIN and report") when core internal systems fail.

🛠️ Tooling & Support Ecosystem (Future Development)
To fully realize Ternlang's "plug-and-play" potential, a robust support ecosystem is envisioned:

ternviz.py (Visualization Tool): A matplotlib or similar tool to plot agent metrics (clarity over time, cognition vs. mood, TEMPRA spikes), providing intuitive visual diagnostics.

ternlang_dashboard.py (Operator Interface): A Streamlit or Tkinter GUI for manual input, real-time control (e.g., sliders for internal states), and live output of agent decisions.

ternlang_eval.py (Evaluation & Training Pipeline): A tool to auto-run test suites, logging decisions and state changes, and outputting summaries (e.g., %AFFIRM, avg mood change), crucial for tuning and validating agent performance against different "input weather."

ternlang_swarm.py (Multi-Agent Deployment Framework): A framework to spin up N agents, manage their interactions, and observe emergent decisions, group resonance, and leader overrides in a collective intelligence context.

📂 Repository Structure
The Ternlang repository is organized for clarity and extensibility:

/docs: Documentation of concepts, semantics, and high-level architecture (intent.md, philosophy.md, MASTERFRAME.md).

/spec: The language specification drafts, including early syntax proposals and core mechanics.

/examples: Illustrative examples demonstrating Ternlang logic in action with specialized agents.

/sim: Planned simulation or playground space for emulations of Ternlang (for future interactive experiments).

ternlang_prototype.py: The core TernAgent base class.

ternlang_memory_manager.py: The standalone MemoryManager class.

🤝 Future Development & Community
Ternlang is an open and evolving project. We invite the community to explore, contribute to, and help shape its future, building towards a new era of intelligent, adaptive, and accountable digital entities.
