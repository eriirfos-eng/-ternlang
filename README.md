## README.md – Project Overview and Structure

The **Ternlang** repository’s README introduces the project as *“an experimental architecture for a post-binary programming dialect”* rooted in **ternary logic** (using values `-1`, `0`, `+1`), **recursive agency**, and the RFI-IRFOS Institute’s philosophical framework. In essence, Ternlang is a speculative programming model exploring non-binary logic and aiming to encode notions of **tending**, **observing**, and **acting** in software. Uniquely, it aspires to incorporate **hesitation** and **care** into programming constructs via *contextual recursion*, reflecting a shift in ethos – *“If binary code was built for conquest — Ternlang is built for conversation.”* This motto from the creators (Simeon & Albert of RFI-IRFOS) underscores the language’s emphasis on dialogue and restraint rather than the traditional decisive action of binary logic systems.

This README outlines the repository layout, which is organized into several top-level directories for different aspects of the project:

* **`/docs`:** Documentation of concepts, semantics, and architecture (high-level ideas and design philosophies).
* **`/spec`:** The language specification drafts, including early syntax proposals, pseudocode, and core mechanics.
* **`/examples`:** Sample Ternlang logic in action (illustrative examples demonstrating how one might write code or logical constructs in Ternlang).
* **`/sim`:** Planned simulation or playground space for emulations of Ternlang (for future interactive experiments).

## docs/intent.md – Purpose and Vision

The **Intent** document lays out the motivation and high-level purpose behind Ternlang. It explicitly states the goal: to explore the **possibility of a programming dialect beyond binary logic**. In Ternlang’s envisioned system:

* Decisions are **not limited to** Boolean **true/false**. Instead, outcomes can be **“refrain”, “tend”, or “act”** – introducing a third option beyond yes/no for decision-making. This means a piece of code can explicitly choose to *do nothing (refrain)*, to *observe/adjust (tend)*, or to *take action (act)*, depending on context.
* **Recursion and observation are fundamental operations**. The language is designed so that functions/agents can call themselves or monitor their own behavior in a feedback loop. This recursive agency implies programs that continually adjust based on their state or environment, rather than executing a fixed linear sequence of instructions.
* **Agency within code is intended to yield emergent behavior by design**. In other words, Ternlang’s constructs are meant to allow programs to develop complex, adaptive behaviors on purpose, rather than such complexity arising only unintentionally (as *side effects*). This hints at code structures that can evolve or change their behavior in runtime through self-referential logic.

Finally, *Intent* emphasizes that **Ternlang is a research scaffold, not a finalized product**. The document notes that this is *“not a finished language, but rather a conceptual and architectural scaffold”* – a starting framework to test ideas. It refers to Ternlang as a *“research vector — not a final product”*, reinforcing that the project’s value lies in exploration of concepts (like multi-valued logic and inbuilt agency) rather than immediate practical utility.

## docs/philosophy.md – Foundational Principles

The **Philosophy** document provides the theoretical foundation and reasoning behind Ternlang’s design, expressed as three key premises:

1. **Beyond Binary Logic:** *“Computational logic need not remain binary.”* Real-world phenomena (especially in domains like cognition, social dynamics, or ethics) often cannot be reduced to simple true/false decisions. There is value in a logic system that explicitly allows for **inaction**, **ambiguity**, or open-ended **observation** without immediate conclusion. This premise justifies Ternlang’s three-valued logic: it mirrors scenarios where the correct choice might be to hold back or gather more information rather than binary go/no-go decisions. In short, the language seeks to reflect the nuanced decision-making of complex systems.

2. **Agency Requires Recursion:** *“The capacity to modify behavior based on self-monitoring is essential for adaptive, reflective systems.”* In Ternlang’s philosophy, truly autonomous or *agentive* code must be able to observe and adjust itself, which inherently implies a recursive structure. By treating **recursion as a first-order principle**, Ternlang allows functions or agents to continually re-enter their own logic with updated context. This premise underlies the design choice that recursion (self-referential calls, feedback loops) is a built-in feature of the language’s model of computation, enabling programs to be **self-reflective and adaptive** by design.

3. **Inaction as a Valid Outcome:** *“Not all code should produce an outcome.”* In some situations, *“the most appropriate action is no action.”* Therefore, Ternlang makes **refrain (no-operation)** a first-class outcome in the logic. This principle is central to the language’s philosophy: it legitimizes deliberate inaction. By encoding *“refrain”* as a computational result, the language acknowledges scenarios where a program deciding to **do nothing** is not an error or absence of decision, but a conscious, encoded choice. This is especially relevant in ethical or safety-critical systems where doing nothing can be preferable to doing the wrong something.

Beyond these premises, the Philosophy document concludes that **Ternlang’s goal is not to replace existing programming paradigms but to expand them**. The language is positioned as an augmentation of the programmer’s toolkit, adding new expressive power. As stated, *“Ternlang does not seek to replace existing paradigms, but to expand the space of what programmable systems may express.”*. This frames Ternlang as an exploratory addition to computing, enriching the logical and conceptual vocabulary available to developers rather than directly competing with traditional binary-logic languages.

## docs/spec/core.md – Core Specification Draft (v0.1.0)

The **Core Specification** is a draft detailing Ternlang’s fundamental logic and illustrating how the language might work in practice. It defines the **ternary logic framework** that forms the basis of all computation in Ternlang:

* **`-1` – Refrain:** Represents a decision to withdraw or not engage in an action.
* **`0` – Tend:** Represents a state of observation, holding, or adjustment (a neutral, waiting stance).
* **`+1` – Act:** Represents an instruction to actively engage or execute an operation.

These three symbolic values are the **core truth values/state outcomes** in Ternlang, replacing the conventional boolean *true/false*. The spec notes that this logic is designed for **“recursive flow, not imperative execution”**. In other words, instead of a one-off linear execution path, Ternlang’s semantics encourage a flowing, feedback-loop style of operation. The program’s state and decisions can feed back into itself (recursively), aligning with the idea of continuous observation and adjustment, rather than a straight-line sequence of commands. This is a direct implementation of the *recursive agency* principle at the language mechanics level.

Following the definition of the logic values, the core spec provides a **sample structural flow** (in pseudocode) to demonstrate how ternary logic operates in context. In this example, an `agent` observes some `input` and then makes a decision based on its **state**:

```ternlang
agent.state = observe(input)

if (agent.state == resonance):
    return +1  // act
elif (agent.state == null):
    return 0   // tend
else:
    return -1  // refrain
```

In prose, the snippet shows: the agent first uses an `observe` function to evaluate input and update its internal state (`agent.state`). Then, using a conditional structure, it chooses one of the three outcomes: if the state reflects a **“resonance”** with the input (perhaps meaning a strong positive condition or alignment), the agent returns `+1` – an instruction to **Act**. If the state is **“null”** (indeterminate or no strong signal), it returns `0` – to **Tend** (i.e. continue observing or adjusting without fully acting). Otherwise (for any other state outside a clear resonance or null), it returns `-1` – to **Refrain** from acting. This example illustrates how Ternlang’s syntax might look and how the **ternary decision logic** is embedded into control flow. Notably, it demonstrates an explicit *no-op path* (`return -1`) and a *middle-state path* (`return 0`) in addition to the conventional action path, which is a distinctive feature of this language’s design. The control flow still uses familiar constructs (`if/elif/else`), indicating that the surface syntax of Ternlang may resemble existing languages, but the **semantics** of the outcomes (`+1, 0, -1`) are what fundamentally diverge, enabling more nuanced program behavior.
