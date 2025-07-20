# examples/example_idle_tending.py
# Demonstrates a TernAgent entering TEND mode due to idle time,
# simulating a "proto-curiosity" or "reflection loop" where it
# reorganizes context and potentially grows cognition.

# Assuming ternlang_prototype.py is in the same parent directory
from ternlang_prototype import REFRAIN, TEND, AFFIRM, TernAgent
import random
import time
import datetime

print("--- Ternlang Example: Idle Tending Agent (Proto-Curiosity) ---")

class IdleAgent(TernAgent):
    """
    A TernAgent that models behavior during periods of inactivity.
    If no significant external input is received for a certain duration,
    it automatically enters a TEND state to perform internal reflection,
    reorganize its context, or generate spontaneous thoughts.
    """
    def __init__(self, name="IdleThinker", initial_clarity=0.6):
        super().__init__(name, initial_context="awaiting_input")
        self.clarity_score = initial_clarity
        self.idle_ticks = 0 # Counter for consecutive idle cycles
        self.idle_threshold = 3 # Number of idle ticks before auto-TEND
        self.last_active_input_time = datetime.datetime.now() # To track real idle time
        
        # Initialize mood and cognition
        self.mood = 8 # Slightly positive, open to reflection
        self.cognition = 600
        print(f"[{self.name}] Initialized with Clarity: {self.clarity_score:.2f}, Idle Ticks: {self.idle_ticks}")

    def observe(self, input_data, other_agent_actions=None):
        """
        Observes input. If input is 'no_input_signal', it increments idle_ticks.
        Otherwise, it resets idle_ticks and updates last_active_input_time.
        """
        print(f"[{self.name}] Observing input: '{input_data}'")
        
        current_context = "neutral_observation"
        
        # Check for active input vs. idle signal
        if input_data.lower() == "no_input_signal":
            self.idle_ticks += 1
            print(f"[{self.name}]   (Idle Monitor) No active input. Idle ticks: {self.idle_ticks}")
            # Clarity might slightly decrease if no new info, or stay stable
            self.clarity_score = max(0.0, self.clarity_score - random.uniform(0.01, 0.05))
            current_context = "idle_awaiting_input"
        else:
            self.idle_ticks = 0 # Reset idle counter on active input
            self.last_active_input_time = datetime.datetime.now()
            print(f"[{self.name}]   (Idle Monitor) Active input received. Idle ticks reset.")
            # Simulate clarity calculation based on keywords for active input
            if "unclear" in input_data.lower() or "vague" in input_data.lower():
                self.clarity_score = random.uniform(0.0, 0.3)
                current_context = "highly_ambiguous"
            elif "clear" in input_data.lower() or "understood" in input_data.lower():
                self.clarity_score = random.uniform(0.7, 1.0)
                current_context = "very_clear"
            else:
                self.clarity_score = random.uniform(0.4, 0.7)
                current_context = "evaluating_situation"

        self.context = current_context
        print(f"[{self.name}] Context: '{self.context}', Clarity: {self.clarity_score:.2f}")
        return self.context, self.clarity_score

    def decide(self, clarity_score, other_agent_decision=None):
        """
        Decides the action. If idle for too long, it forces a TEND for reflection.
        """
        print(f"[{self.name}] Deciding based on clarity: {clarity_score:.2f} and idle ticks: {self.idle_ticks}...")
        
        # [NEW]: Auto-TEND for Idle Time
        if self.idle_ticks >= self.idle_threshold:
            print(f"[{self.name}] --- IDLE THRESHOLD REACHED! Auto-TENDING for reflection. ---")
            # Force TEND, as this is the purpose of idle time
            decision = TEND
            self.mood = min(13, self.mood + 1) # Mood might improve from productive reflection
            self.cognition = min(1000, self.cognition + 100) # Cognitive effort for reflection
            print(f"[{self.name}] Forced decision: {self._get_state_name(decision)}")
            return decision

        # Normal decision logic (if not forced into idle TEND)
        if clarity_score >= 0.7:
            decision = AFFIRM
            print(f"[{self.name}] High clarity detected. Ready to AFFIRM.")
        elif clarity_score < 0.3:
            decision = REFRAIN
            print(f"[{self.name}] Low clarity. REFRAINING from action.")
        else:
            decision = TEND
            print(f"[{self.name}] Moderate clarity. TENDING for more information.")

        # Adjust mood and cognition based on decision
        if decision == TEND:
            self.cognition = min(1000, self.cognition + 50)
            self.mood = max(1, min(13, self.mood - 1))
        elif decision == REFRAIN:
            self.cognition = max(0, self.cognition - 30)
            self.mood = max(1, self.mood - 2)
        elif decision == AFFIRM:
            self.cognition = max(0, self.cognition - 20)
            self.mood = min(13, self.mood + 1)

        print(f"[{self.name}] Decision: {self._get_state_name(decision)}")
        return decision

    def execute_action(self, action):
        """
        Executes the action. If TEND due to idle, it performs specific reflection.
        """
        super().execute_action(action) # Call parent method for general mood/cognition updates

        if action == TEND and self.idle_ticks > 0: # Check if TEND was due to idle
            print(f"[{self.name}] TENDING: Performing idle reflection/reorganization...")
            self._perform_idle_reflection()
        elif action == AFFIRM:
            print(f"[{self.name}] ACTION: Proceeding. Idle state reset.")
            self.idle_ticks = 0 # Reset idle counter on active decision
        elif action == REFRAIN:
            print(f"[{self.name}] REFRAIN: Halting. Idle state reset.")
            self.idle_ticks = 0 # Reset idle counter on active decision
        else:
            print(f"[{self.name}] TENDING: Observing further, adjusting, or waiting (not idle-triggered).")

    def _perform_idle_reflection(self):
        """
        Simulates the agent's internal reflection or context reorganization during idle time.
        This is the "WALL·E watering his shoe-plant" moment.
        """
        print(f"[{self.name}]   (Internal Reflection) Reorganizing internal context and surfacing spontaneous thoughts...")
        # Simulate slight clarity increase from internal thought
        self.clarity_score = min(1.0, self.clarity_score + random.uniform(0.02, 0.1))
        # Cognition might grow from new insights or connections
        self.cognition = min(1000, self.cognition + random.randint(30, 80))
        # Mood might slightly improve from productive reflection
        self.mood = min(13, self.mood + 1)
        time.sleep(0.8) # Simulate time taken for reflection
        print(f"[{self.name}]   (Internal Reflection) Context reorganized. New clarity: {self.clarity_score:.2f}, Mood: {self.mood}, Cognition: {self.cognition}")

    def run_cycle(self, input_data, other_agent_actions=None):
        """
        Performs a full Ternlang cycle for an IdleAgent.
        """
        print(f"\n--- [{self.name}] Starting New Cycle ---")
        current_context, relevance_score = self.observe(input_data, other_agent_actions)
        decision = self.decide(relevance_score)
        self.execute_action(decision)

        # Log to memory
        self.memory.append({
            "timestamp": datetime.datetime.now().isoformat(),
            "input": input_data,
            "context": current_context,
            "decision": decision,
            "mood": self.mood,
            "cognition": self.cognition,
            "clarity": self.clarity_score,
            "idle_ticks": self.idle_ticks
        })

        print(f"--- [{self.name}] Cycle Complete ---")
        return decision


# --- Simulation ---
def simulate_idle_tending_agent(num_cycles=10):
    """
    Runs a simulation of an IdleAgent, demonstrating idle-triggered TEND.
    """
    print("\n--- Ternlang Idle Tending Agent Simulation Started ---")
    
    idle_agent = IdleAgent(name="WALL-E_Bot", initial_clarity=0.6)

    # Example inputs: mix of active inputs and "no_input_signal" to simulate idle periods
    scenarios = [
        "Input: Analyze recent sensor data. (Active)",
        "Input: no_input_signal", # Idle tick 1
        "Input: no_input_signal", # Idle tick 2
        "Input: no_input_signal", # Idle tick 3 -> Auto-TEND
        "Input: no_input_signal", # Idle tick 4 -> Continues TEND
        "Input: Urgent message received! (Active, resets idle)",
        "Input: no_input_signal", # Idle tick 1
        "Input: no_input_signal", # Idle tick 2
        "Input: New directive: Clean up debris. (Active)",
        "Input: no_input_signal", # Idle tick 1
        "Input: no_input_signal", # Idle tick 2
        "Input: no_input_signal", # Idle tick 3 -> Auto-TEND
    ]

    for i, scenario_input in enumerate(scenarios):
        print(f"\n===== SIMULATION CYCLE {i+1}/{len(scenarios)} =====")
        idle_agent.run_cycle(scenario_input)
        time.sleep(1.5) # Pause for readability

    print("\n--- Ternlang Idle Tending Agent Simulation Finished ---")

    # Optional: Print final state and memory
    print("\n--- Final Agent State ---")
    print(f"[{idle_agent.name}] Final Mood: {idle_agent.mood}, Cognition: {idle_agent.cognition}, Clarity: {idle_agent.clarity_score:.2f}, Idle Ticks: {idle_agent.idle_ticks}, Last Action: {idle_agent._get_state_name(idle_agent.last_action)}")
