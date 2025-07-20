# ternlang_prototype.py
# Version: 0.2.0
# Author: Simeon & Gemini (AI Assistant)
# License: MIT (or choose your preferred open-source license for the repo)

"""
This file serves as an updated executable prototype (v0.2.0) for Ternlang,
an experimental architecture for a post-binary programming dialect.

Building upon v0.1.0, this version introduces:
1.  **Context Expansion Layer:** More nuanced observation logic.
2.  **Memory Module:** Agents can track past experiences.
3.  **Logging with Mood/Cognition Barometer:** Internal state tracking for agents.
4.  **Swarm Agent Model:** Simulation of multiple interacting TernAgents.

The goal remains to provide a tangible, runnable foundation for the
GitHub community to explore, contribute to, and build upon,
especially for applications involving AI agents, LLMs, or API integrations.
"""

import time
import random
import datetime # For timestamping memory entries

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
        self.memory = []                # [NEW] Stores a history of (timestamp, input, context, action)
        self.mood = 7                   # [NEW] Scalar 1-13 (7 is neutral, 1 is very low, 13 is very high)
        self.cognition = 500            # [NEW] Scalar 0-1000 (measures cognitive effort/focus)
        print(f"[{self.name}] Initialized with context: '{self.context}', Mood: {self.mood}, Cognition: {self.cognition}")

    def observe(self, input_data, other_agent_actions=None):
        """
        [MODIFIED] Simulates the agent observing external input and optionally
        the actions of other agents.

        This is a placeholder for more complex observation logic.
        It now returns a numerical 'relevance_score' to influence decision.

        Args:
            input_data (str): The external data or event the agent observes.
            other_agent_actions (list, optional): A list of actions taken by other agents
                                                  in the current cycle. Used for swarm interactions.

        Returns:
            tuple: (str) The updated internal context, (float) a relevance score.
        """
        print(f"[{self.name}] Observing: '{input_data}'...")

        # [NEW] Incorporate other agent actions into observation
        if other_agent_actions:
            for action in other_agent_actions:
                if action == AFFIRM:
                    input_data += " other_affirmed"
                elif action == REFRAIN:
                    input_data += " other_refrained"
                # TEND actions are less impactful on immediate observation for simplicity

        # [MODIFIED] Simple logic to update context and calculate a relevance score
        relevance_score = 0.0
        if "problem" in input_data.lower() or "error" in input_data.lower():
            self.context = "conflict"
            relevance_score = 0.9 # High relevance for problems
        elif "opportunity" in input_data.lower() or "ready" in input_data.lower():
            self.context = "resonance"
            relevance_score = 0.8 # High relevance for opportunities
        elif "wait" in input_data.lower() or "pause" in input_data.lower():
            self.context = "ambiguity"
            relevance_score = 0.3 # Low relevance, implies waiting
        elif "other_affirmed" in input_data.lower():
            self.context = "collective_affirm"
            relevance_score = 0.7 # Moderate relevance, influenced by others
        elif "other_refrained" in input_data.lower():
            self.context = "collective_refrain"
            relevance_score = 0.6 # Moderate relevance, influenced by others
        else:
            self.context = "neutral" # Default or no strong signal
            relevance_score = 0.5 # Neutral relevance

        # [NEW] Influence cognition based on observation complexity/relevance
        self.cognition = min(1000, max(0, self.cognition + int(relevance_score * 100) - 20)) # Simple adjustment

        print(f"[{self.name}] Internal context updated to: '{self.context}', Relevance Score: {relevance_score:.2f}")
        return self.context, relevance_score

    def decide(self, relevance_score):
        """
        [MODIFIED] Applies Ternlang's ternary logic to the agent's current context
        and relevance score to determine the next action (REFRAIN, TEND, or AFFIRM).

        This is the core decision-making function, now influenced by observation intensity.

        Args:
            relevance_score (float): The numerical score from the observation phase.

        Returns:
            int: One of the Ternlang core states (REFRAIN, TEND, AFFIRM).
        """
        print(f"[{self.name}] Deciding based on context: '{self.context}' and relevance: {relevance_score:.2f}...")

        decision = TEND # Default to TEND

        # [MODIFIED] Decision logic now considers relevance_score
        if self.context == "resonance" and relevance_score > 0.7:
            decision = AFFIRM
        elif self.context == "conflict" and relevance_score > 0.6:
            decision = REFRAIN
        elif self.context == "collective_affirm" and relevance_score > 0.5:
            decision = AFFIRM # More likely to affirm if others do
        elif self.context == "collective_refrain" and relevance_score > 0.5:
            decision = REFRAIN # More likely to refrain if others do
        elif self.context == "ambiguity" or self.context == "neutral":
            # If tending, consider past actions or memory for subtle bias
            if len(self.memory) > 0 and self.memory[-1][3] == REFRAIN: # If last action was REFRAIN
                decision = TEND # Stay cautious, tend again
            else:
                decision = TEND # Default tend

        # [NEW] Influence cognition based on decision complexity (e.g., if it's a difficult decision)
        # This is a simple placeholder for more complex cognitive modeling
        if decision == TEND and relevance_score > 0.5: # Tending when input is relevant might require more thought
            self.cognition = min(1000, self.cognition + 50)
        elif decision == AFFIRM or decision == REFRAIN: # Decisive actions might reduce immediate cognitive load
            self.cognition = max(0, self.cognition - 30)


        print(f"[{self.name}] Decision made: {decision} ({self._get_state_name(decision)})")
        return decision

    def execute_action(self, action):
        """
        [MODIFIED] Executes the action determined by the agent's decision.
        This function now also updates the agent's mood and cognition.

        Args:
            action (int): The Ternlang core state (REFRAIN, TEND, AFFIRM)
                          to be executed.
        """
        self.last_action = action # Store the last action for potential recursive use

        # [NEW] Update Mood and Cognition based on action
        if action == AFFIRM:
            print(f"[{self.name}] ACTION: Engaging and proceeding!")
            self.mood = min(13, self.mood + 1) # Mood slightly increases
            self.cognition = max(0, self.cognition - 50) # Cognitive load might decrease after decisive action
        elif action == TEND:
            print(f"[{self.name}] TENDING: Observing further, adjusting, or waiting.")
            # Mood and cognition might fluctuate based on how long tending lasts or if it's productive
            self.mood = max(1, min(13, self.mood + random.choice([-1, 0, 1]))) # Mood can slightly shift
            self.cognition = min(1000, self.cognition + 20) # Tending might require sustained cognitive effort
        elif action == REFRAIN:
            print(f"[{self.name}] REFRAIN: Withdrawing, not engaging, or pausing.")
            self.mood = max(1, self.mood - 1) # Mood slightly decreases (caution/frustration)
            self.cognition = max(0, self.cognition - 20) # Cognitive load might decrease after refraining
        else:
            print(f"[{self.name}] WARNING: Unknown action state received: {action}")
            self.mood = max(1, self.mood - 2) # Significant mood drop for unknown state
            self.cognition = min(1000, self.cognition + 100) # High cognitive load for error

        print(f"[{self.name}] Current Mood: {self.mood}, Current Cognition: {self.cognition}")


    def run_cycle(self, input_data, other_agent_actions=None):
        """
        [MODIFIED] Performs a full Ternlang cycle: Observe -> Decide -> Execute.
        Now includes memory logging and passes other agent actions for swarm interaction.

        Args:
            input_data (str): The external data or event to process in this cycle.
            other_agent_actions (list, optional): A list of actions taken by other agents
                                                  in the current cycle.

        Returns:
            int: The action taken in this cycle.
        """
        print(f"\n--- [{self.name}] Starting New Cycle ---")
        current_context, relevance_score = self.observe(input_data, other_agent_actions)
        decision = self.decide(relevance_score)
        self.execute_action(decision)

        # [NEW] Log to memory
        self.memory.append({
            "timestamp": datetime.datetime.now().isoformat(),
            "input": input_data,
            "context": current_context,
            "decision": decision,
            "mood": self.mood,
            "cognition": self.cognition
        })

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

def simulate_ternlang_swarm(num_cycles=5, num_agents=3):
    """
    [NEW] Runs a simulation of multiple TernAgents (a swarm) over multiple cycles.
    Agents can observe each other's actions from the previous cycle.

    Args:
        num_cycles (int): The number of simulation cycles.
        num_agents (int): The number of TernAgents in the swarm.
    """
    print("\n--- Ternlang Swarm Agent Simulation Started ---")
    agents = [TernAgent(name=f"TernBot-{i+1}") for i in range(num_agents)]

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

    # Track last actions of all agents to pass to others
    last_cycle_actions = {agent.name: TEND for agent in agents}

    for i in range(num_cycles):
        print(f"\n===== SIMULATION CYCLE {i+1}/{num_cycles} =====")
        current_input = random.choice(example_inputs)
        
        # Collect actions from this cycle to pass to next
        current_cycle_actions = {} 

        for agent in agents:
            # Prepare actions of *other* agents for the current agent's observation
            other_actions = [
                action for name, action in last_cycle_actions.items() 
                if name != agent.name
            ]
            
            # Run the agent's cycle
            action_taken = agent.run_cycle(current_input, other_agent_actions=other_actions)
            current_cycle_actions[agent.name] = action_taken
            time.sleep(0.5) # Short pause between agents for readability

        last_cycle_actions = current_cycle_actions # Update for next cycle

    print("\n--- Ternlang Swarm Agent Simulation Finished ---")

    # Optional: Print memory of each agent at the end
    print("\n--- Agent Memory Snapshots ---")
    for agent in agents:
        print(f"\n[{agent.name}] Memory (last 3 entries):")
        for entry in agent.memory[-3:]: # Show last 3 entries for brevity
            print(f"  - {entry['timestamp']} | Input: '{entry['input']}' | Context: '{entry['context']}' | Decision: {agent._get_state_name(entry['decision'])} | Mood: {entry['mood']} | Cognition: {entry['cognition']}")


# --- Main Execution Block ---
# This ensures that simulate_ternlang_swarm() is called only when
# the script is executed directly (not when imported as a module).
if __name__ == "__main__":
    simulate_ternlang_swarm(num_cycles=8, num_agents=3) # Run for 8 cycles with 3 agents
