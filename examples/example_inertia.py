# examples/example_inertia.py
# Demonstrates Ternlang's TEND state leading to inertia and a "torpor mode",
# requiring an external "jolt" to re-engage.

# Assuming ternlang_prototype.py is in the same parent directory
from ternlang_prototype import REFRAIN, TEND, AFFIRM, TernAgent
import random
import time

print("--- Ternlang Example: Agent Inertia and Torpor ---")

class InertiaAgent(TernAgent):
    """
    A TernAgent that models cognitive/behavioral inertia.
    If it repeatedly TENDs without significant clarity improvement,
    it enters a 'torpor mode' and requires an external 'jolt' to re-engage.
    """
    def __init__(self, name="InertiaAgent", initial_clarity=0.5):
        super().__init__(name, initial_context="evaluating_situation")
        self.clarity_score = initial_clarity # 0.0 (uncertain) to 1.0 (clear)
        self.previous_clarity_score = initial_clarity # To track delta
        self.inertia_score = 0 # Increases when stuck in TEND without progress
        self.inertia_threshold = 4 # How many TENDs with low delta before torpor
        self.is_in_torpor = False # Flag for torpor mode
        
        # Initialize mood and cognition (as per previous feedback)
        self.mood = 7
        self.cognition = 500
        print(f"[{self.name}] Initial clarity: {self.clarity_score:.2f}, Inertia: {self.inertia_score}")

    def observe(self, input_data, other_agent_actions=None):
        """
        Observes input, calculates clarity, and updates inertia score.
        [NEW]: Detects "jolt" input to break torpor.
        """
        print(f"[{self.name}] Observing input: '{input_data}'")
        
        # [NEW]: Check for "jolt" input first, regardless of current state
        if "jolt" in input_data.lower() or "wake up" in input_data.lower() or "nudge" in input_data.lower():
            if self.is_in_torpor:
                print(f"[{self.name}] --- JOLT RECEIVED! Waking from torpor! ---")
                self.is_in_torpor = False
                self.inertia_score = 0
                self.mood = min(13, self.mood + 3) # Jolt improves mood
                self.cognition = min(1000, self.cognition + 200) # Jolt improves cognition
                self.context = "re-engaging"
                self.clarity_score = 0.5 # Reset clarity to neutral upon jolt
                return self.context, self.clarity_score # Return immediately after jolt

        # Store current clarity before updating for delta calculation
        current_clarity_at_start = self.clarity_score

        current_context = "neutral_observation"
        
        # Simulate clarity calculation based on keywords (similar to AmbiguityAgent)
        if "unclear" in input_data.lower() or "vague" in input_data.lower() or "misunderstood" in input_data.lower():
            self.clarity_score = random.uniform(0.0, 0.3)
            current_context = "highly_ambiguous"
        elif "partially clear" in input_data.lower() or "some context missing" in input_data.lower():
            self.clarity_score = random.uniform(0.3, 0.6)
            current_context = "moderately_clear"
        elif "very clear" in input_data.lower() or "explicit" in input_data.lower() or "understood" in input_data.lower():
            self.clarity_score = random.uniform(0.7, 1.0)
            current_context = "very_clear"
        else:
            self.clarity_score = random.uniform(0.4, 0.7)
            current_context = "evaluating_situation"

        self.context = current_context

        # [NEW]: Update inertia_score based on previous action and clarity delta
        if self.last_action == TEND:
            clarity_delta = abs(self.clarity_score - current_clarity_at_start)
            if clarity_delta < 0.05: # If clarity didn't change much
                self.inertia_score += 1
                print(f"[{self.name}]   (Inertia) Clarity delta low ({clarity_delta:.2f}). Inertia score increased to {self.inertia_score}.")
            else:
                self.inertia_score = 0 # Progress made, reset inertia
                print(f"[{self.name}]   (Inertia) Clarity delta significant. Inertia score reset.")
        else:
            self.inertia_score = 0 # Non-TEND action, reset inertia

        # [NEW]: Check for torpor transition
        if self.inertia_score >= self.inertia_threshold and not self.is_in_torpor:
            self.is_in_torpor = True
            self.context = "torpor_mode"
            print(f"[{self.name}] --- ENTERING TORPOR MODE! ---")
            self.mood = max(1, self.mood - 5) # Mood drops significantly
            self.cognition = max(0, self.cognition - 300) # Cognition drops significantly

        print(f"[{self.name}] Context: '{self.context}', Clarity Score: {self.clarity_score:.2f}, Inertia Score: {self.inertia_score}")
        return self.context, self.clarity_score # Return clarity_score as relevance_score

    def decide(self, clarity_score):
        """
        Decides the action, heavily influenced by torpor mode.
        """
        print(f"[{self.name}] Deciding based on clarity: {clarity_score:.2f}...")
        
        if self.is_in_torpor:
            print(f"[{self.name}]   (Torpor) Agent is in torpor. Cannot make active decision.")
            # In torpor, the agent primarily REFRAINs or TENDs passively
            return TEND # Stays in TEND (torpor) until jolted

        decision = TEND # Default to TEND if no strong signal

        if clarity_score >= 0.7:
            decision = AFFIRM
            print(f"[{self.name}] High clarity detected. Ready to AFFIRM.")
        elif clarity_score < 0.7:
            decision = TEND
            print(f"[{self.name}] Ambiguity detected. TENDING for internal reasoning/clarification.")
        
        # Adjust mood and cognition based on ambiguity and decision
        if decision == TEND:
            self.cognition = min(1000, self.cognition + 50)
            self.mood = max(1, min(13, self.mood - 1))
        elif decision == REFRAIN:
            self.cognition = max(0, self.cognition - 50)
            self.mood = max(1, self.mood - 2)
        elif decision == AFFIRM:
            self.cognition = max(0, self.cognition - 30)
            self.mood = min(13, self.mood + 1)

        print(f"[{self.name}] Decision: {self._get_state_name(decision)}")
        return decision

    def execute_action(self, action):
        """
        Executes the action. Special handling for torpor mode.
        """
        super().execute_action(action) # Call parent method for general mood/cognition updates

        if self.is_in_torpor:
            print(f"[{self.name}]   (Torpor Action) Agent remains in a passive, unresponsive state.")
        elif action == TEND:
            print(f"[{self.name}] TENDING: Actively observing or seeking clarification.")
        elif action == AFFIRM:
            print(f"[{self.name}] Proceeding with action. Inertia reset.")
            self.inertia_score = 0 # Reset inertia on decisive action
        elif action == REFRAIN:
            print(f"[{self.name}] Refraining from action. Inertia reset.")
            self.inertia_score = 0 # Reset inertia on decisive action

# --- Simulation ---
inertia_agent = InertiaAgent(name="ResilienceBot", initial_clarity=0.4)

scenarios = [
    "Input: Vague instructions, unclear objective.", # Leads to TEND
    "Input: Still no clear guidance, highly ambiguous.", # TEND, inertia increases
    "Input: Persistent uncertainty, can't make sense of it.", # TEND, inertia increases
    "Input: Data is contradictory, very confusing.", # TEND, inertia increases, hits threshold
    "Input: The system is unresponsive. (Agent now in torpor)", # Agent in torpor, this input has no effect
    "Input: Please provide a clear directive. (Agent still in torpor)", # Agent in torpor
    "Input: JOLT! Wake up and re-evaluate the situation!", # Jolt!
    "Input: New, clear instructions provided. Proceed.", # Agent should now AFFIRM
    "Input: Another ambiguous task, but agent is reset." # Agent should TEND normally
]

for i, scenario_input in enumerate(scenarios):
    print(f"\n--- Scenario {i+1}: '{scenario_input}' ---")
    inertia_agent.run_cycle(scenario_input)
    # Simulate a brief pause between scenarios
    time.sleep(1.5)

print("\n--- Agent Inertia and Torpor Example Finished ---")
