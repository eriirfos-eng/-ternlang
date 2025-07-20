
This file serves as the initial executable prototype for Ternlang,
an experimental architecture for a post-binary programming dialect.

It demonstrates the core ternary logic (-1, 0, +1) and the concept
of a 'TernAgent' that can observe, decide, and perform actions
based on these states.

The goal is to provide a tangible, runnable foundation for the
GitHub community to explore, contribute to, and build upon,
especially for applications involving AI agents, LLMs, or API integrations.
"""

import time
import random

# --- 1. Ternlang Core States ---
# These constants define the fundamental ternary logic values.
# They replace traditional binary (True/False or 0/1) outcomes.
REFRAIN = -1    # Represents a decision to withdraw, not engage, or do nothing.
                # Conveys "Not now, not me" or deliberate inaction.
TEND    = 0     # Represents a state of observation, holding, or adjustment.
                # Conveys "Hold, observe, adjust" or a neutral, waiting stance.
AFFIRM  = +1    # Represents an instruction to actively engage, execute, or proceed.
                # Conveys "Ready, engage, act" or decisive action.

# --- 2. TernAgent Class ---
# This class models a basic Ternlang agent, embodying the principles
# of observation, decision-making based on ternary logic, and action.
class TernAgent:
    def __init__(self, name="UnnamedAgent", initial_context="neutral"):
        """
        Initializes a new TernAgent.

        Args:
            name (str): A unique name for the agent.
            initial_context (str): The initial context or internal state of the agent.
                                   This can be anything relevant to the agent's domain.
        """
        self.name = name
        self.context = initial_context  # The agent's internal understanding/state
        self.last_action = TEND         # Start with a tending state
        print(f"[{self.name}] Initialized with context: '{self.context}'")

    def observe(self, input_data):
        """
        Simulates the agent observing external input.
        This is a placeholder for more complex observation logic.

        In a real-world scenario, this could involve:
        - Processing sensor data
        - Analyzing text from an LLM
        - Receiving API responses
        - Monitoring system metrics

        For this prototype, it will simply update the agent's context
        based on a simplified interpretation of the input.

        Args:
            input_data (str): The external data or event the agent observes.

        Returns:
            str: The updated internal context of the agent after observation.
        """
        print(f"[{self.name}] Observing: '{input_data}'...")

        # Simple logic to update context based on keywords in input_data
        if "problem" in input_data.lower() or "error" in input_data.lower():
            self.context = "conflict"
        elif "opportunity" in input_data.lower() or "ready" in input_data.lower():
            self.context = "resonance"
        elif "wait" in input_data.lower() or "pause" in input_data.lower():
            self.context = "ambiguity"
        else:
            self.context = "neutral" # Default or no strong signal

        print(f"[{self.name}] Internal context updated to: '{self.context}'")
        return self.context

    def decide(self):
        """
        Applies Ternlang's ternary logic to the agent's current context
        to determine the next action (REFRAIN, TEND, or AFFIRM).

        This is the core decision-making function.

        Returns:
            int: One of the Ternlang core states (REFRAIN, TEND, AFFIRM).
        """
        print(f"[{self.name}] Deciding based on context: '{self.context}'...")

        # This is a simplified decision tree.
        # In a more advanced Ternlang, this could involve:
        # - Complex recursive evaluations
        # - Probabilistic models
        # - Learning algorithms
        # - Ethical constraints

        if self.context == "resonance":
            decision = AFFIRM
        elif self.context == "ambiguity" or self.context == "neutral":
            decision = TEND
        elif self.context == "conflict":
            decision = REFRAIN
        else:
            # Fallback for unexpected contexts, default to TEND
            decision = TEND

        print(f"[{self.name}] Decision made: {decision} ({self._get_state_name(decision)})")
        return decision

    def execute_action(self, action):
        """
        Executes the action determined by the agent's decision.
        This function demonstrates what happens for each Ternlang state.

        Args:
            action (int): The Ternlang core state (REFRAIN, TEND, AFFIRM)
                          to be executed.
        """
        self.last_action = action # Store the last action for potential recursive use

        if action == AFFIRM:
            print(f"[{self.name}] ACTION: Engaging and proceeding!")
            # Placeholder for actual "act" behavior:
            # e.g., send API request, execute a task, modify a system state.
        elif action == TEND:
            print(f"[{self.name}] TENDING: Observing further, adjusting, or waiting.")
            # Placeholder for actual "tend" behavior:
            # e.g., gather more data, re-evaluate, sleep, run a sub-routine.
        elif action == REFRAIN:
            print(f"[{self.name}] REFRAIN: Withdrawing, not engaging, or pausing.")
            # Placeholder for actual "refrain" behavior:
            # e.g., log a warning, notify human, prevent an operation.
        else:
            print(f"[{self.name}] WARNING: Unknown action state received: {action}")

    def run_cycle(self, input_data):
        """
        Performs a full Ternlang cycle: Observe -> Decide -> Execute.
        This method can be called recursively or iteratively to simulate
        continuous agent behavior.

        Args:
            input_data (str): The external data or event to process in this cycle.

        Returns:
            int: The action taken in this cycle.
        """
        print(f"\n--- [{self.name}] Starting New Cycle ---")
        self.observe(input_data)
        decision = self.decide()
        self.execute_action(decision)
        print(f"--- [{self.name}] Cycle Complete ---")
        return decision

    def _get_state_name(self, state_value):
        """Helper to get the name of a state for better readability."""
        if state_value == REFRAIN:
            return "REFRAIN"
        elif state_value == TEND:
            return "TEND"
        elif state_value == AFFIRM:
            return "AFFIRM"
        else:
            return "UNKNOWN"

# --- 3. Simulation / Example Usage ---
# This section demonstrates how to use the TernAgent.
# It simulates a series of observations and agent responses.

def simulate_ternlang_agent(num_cycles=5):
    """
    Runs a simple simulation of a TernAgent over multiple cycles.
    """
    print("\n--- Ternlang Agent Simulation Started ---")
    my_agent = TernAgent(name="TernBot")

    # Example inputs to simulate different scenarios
    example_inputs = [
        "System status: All green. Opportunity for deployment.",
        "Warning: Database connection unstable. Please wait.",
        "Critical error: Unauthorized access attempt detected!",
        "Data stream looks good. Ready for processing.",
        "Network latency increasing. Observe and adjust.",
        "All systems nominal. Proceed with operation.",
        "Unexpected input received. Pause for re-evaluation.",
        "Resource contention detected. Refrain from new tasks."
    ]

    for i in range(num_cycles):
        print(f"\n===== SIMULATION CYCLE {i+1}/{num_cycles} =====")
        # Randomly pick an input for variety
        current_input = random.choice(example_inputs)
        my_agent.run_cycle(current_input)
        time.sleep(1) # Pause for readability in console output

    print("\n--- Ternlang Agent Simulation Finished ---")

# --- Main Execution Block ---
# This ensures that simulate_ternlang_agent() is called only when
# the script is executed directly (not when imported as a module).
if __name__ == "__main__":
    simulate_ternlang_agent(num_cycles=8) # Run for 8 cycles
