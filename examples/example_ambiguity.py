# examples/example_ambiguity.py
# Demonstrates Ternlang's TEND state for ambiguity resolution,
# including metacognitive reflection and human-in-the-loop potential.

# Assuming ternlang_prototype.py is in the same parent directory
from ternlang_prototype import REFRAIN, TEND, AFFIRM, TernAgent
import random
import time

print("--- Ternlang Example: Ambiguity Resolution Agent ---")

class AmbiguityAgent(TernAgent):
    """
    A TernAgent specialized in handling ambiguous situations.
    It uses the TEND state to trigger internal reasoning or seek clarification,
    and can escalate to human intervention if ambiguity persists.

    Clarity is represented on a scale of 0.0 (absolute uncertainty) to 1.0 (absolute clarity).
    """
    def __init__(self, name="AmbiguityResolver", initial_clarity=0.5):
        super().__init__(name, initial_context="assessing_clarity")
        self.clarity_score = initial_clarity # 0.0 (uncertain) to 1.0 (clear)
        self.reasoning_steps_taken = 0
        self.max_reasoning_steps = 3 # How many times it will TEND for internal reasoning
        self.human_intervention_threshold = 0.2 # If clarity drops below this after max reasoning, ask human
        print(f"[{self.name}] Initial clarity: {self.clarity_score:.2f}")

    def observe(self, input_data, other_agent_actions=None):
        """
        Observes input and calculates an initial clarity score.
        Updates context based on this score.
        """
        print(f"[{self.name}] Observing input for clarity: '{input_data}'")
        
        current_context = "neutral_observation"
        
        # Simulate clarity calculation based on keywords
        # 0.0 = absolute uncertainty, 1.0 = absolute clarity
        if "unclear" in input_data.lower() or "vague" in input_data.lower() or "misunderstood" in input_data.lower():
            self.clarity_score = random.uniform(0.0, 0.3) # High ambiguity
            current_context = "highly_ambiguous"
        elif "partially clear" in input_data.lower() or "some context missing" in input_data.lower():
            self.clarity_score = random.uniform(0.3, 0.6) # Moderate ambiguity
            current_context = "moderately_clear"
        elif "very clear" in input_data.lower() or "explicit" in input_data.lower() or "understood" in input_data.lower():
            self.clarity_score = random.uniform(0.7, 1.0) # High clarity
            current_context = "very_clear"
        else:
            self.clarity_score = random.uniform(0.4, 0.7) # Default/unknown clarity
            current_context = "evaluating_situation"

        self.context = current_context
        # Use clarity_score as relevance_score for decision making
        print(f"[{self.name}] Context: '{self.context}', Clarity Score: {self.clarity_score:.2f}")
        return self.context, self.clarity_score # Return clarity_score as relevance_score

    def decide(self, clarity_score):
        """
        Decides the action based on the current clarity score.
        Prioritizes TEND for clarification, or REFRAIN/Human-in-the-Loop if stuck.
        """
        print(f"[{self.name}] Deciding based on clarity: {clarity_score:.2f}...")
        decision = TEND # Default to TEND if no strong signal

        if clarity_score >= 0.7: # High clarity, proceed
            decision = AFFIRM
            print(f"[{self.name}] High clarity detected. Ready to AFFIRM.")
        elif clarity_score < 0.7 and self.reasoning_steps_taken < self.max_reasoning_steps:
            decision = TEND # Ambiguous, but can still reason internally
            print(f"[{self.name}] Ambiguity detected. TENDING for internal reasoning/clarification.")
        else: # clarity_score < 0.7 AND max_reasoning_steps reached
            print(f"[{self.name}] Max reasoning steps reached for persistent ambiguity.")
            if clarity_score < self.human_intervention_threshold:
                decision = REFRAIN # Too ambiguous, need human
                print(f"[{self.name}] Clarity too low. REFRAINING, human intervention required.")
            else:
                decision = TEND # Still some hope, TEND one more time or with external clarification
                print(f"[{self.name}] Still ambiguous but not critical. TENDING for external clarification.")
        
        # Adjust mood and cognition based on ambiguity and decision
        if decision == TEND:
            self.cognition = min(1000, self.cognition + 100) # High cognitive load for ambiguity
            self.mood = max(1, min(13, self.mood - 1)) # Slight mood drop due to uncertainty
        elif decision == REFRAIN:
            self.cognition = max(0, self.cognition - 80) # Cognitive relief from stopping
            self.mood = max(1, self.mood - 3) # Significant mood drop for failure to resolve
        elif decision == AFFIRM:
            self.cognition = max(0, self.cognition - 50) # Cognitive relief from proceeding
            self.mood = min(13, self.mood + 2) # Mood increase from clarity

        print(f"[{self.name}] Decision: {self._get_state_name(decision)}")
        return decision

    def execute_action(self, action):
        """
        Executes the action. If TEND, it simulates clarification/reasoning.
        If REFRAIN due to ambiguity, it signals human intervention.
        """
        super().execute_action(action) # Call parent method for mood/cognition updates

        if action == TEND:
            self.reasoning_steps_taken += 1
            if self.reasoning_steps_taken <= self.max_reasoning_steps:
                print(f"[{self.name}]   (Internal Process) Reflecting on ambiguity (Step {self.reasoning_steps_taken}/{self.max_reasoning_steps})...")
                self._perform_internal_reflection()
            else:
                print(f"[{self.name}]   (External Process) Seeking clarification from external source (e.g., verbal, API).")
                self._seek_external_clarification()
        elif action == AFFIRM:
            print(f"[{self.name}] Proceeding with confidence after resolving ambiguity. Resetting reasoning steps.")
            self.reasoning_steps_taken = 0
            self.clarity_score = 1.0 # Assume clarity after affirmation
        elif action == REFRAIN:
            print(f"[{self.name}] REFRAINING: Ambiguity unresolved. Escalating for human intervention!")
            self.reasoning_steps_taken = 0
            self.clarity_score = 0.0 # Remains uncertain

    def _perform_internal_reflection(self):
        """
        Simulates an internal metacognitive process to reduce ambiguity.
        """
        print(f"[{self.name}]     (Reflection) Analyzing internal models and past memory...")
        # Simulate a slight increase in clarity through internal thought
        self.clarity_score = min(1.0, self.clarity_score + random.uniform(0.05, 0.2))
        self.cognition = min(1000, self.cognition + 70) # High cognitive effort
        time.sleep(0.7)
        print(f"[{self.name}]     (Reflection) Internal clarity improved to: {self.clarity_score:.2f}")

    def _seek_external_clarification(self):
        """
        Simulates asking for clarification from an external source (e.g., human, another agent, API).
        """
        print(f"[{self.name}]     (External) Querying for more context or rephrasing request...")
        # Simulate a chance of getting clearer or staying ambiguous
        if random.random() < 0.7: # 70% chance of improvement
            self.clarity_score = min(1.0, self.clarity_score + random.uniform(0.1, 0.3))
            print(f"[{self.name}]     (External) Clarification received. Clarity improved to: {self.clarity_score:.2f}")
        else:
            self.clarity_score = max(0.0, self.clarity_score - random.uniform(0.05, 0.1)) # Might even get worse
            print(f"[{self.name}]     (External) Clarification attempt failed. Clarity now: {self.clarity_score:.2f}")
        self.cognition = min(1000, self.cognition + 50) # Cognitive effort for external comms
        time.sleep(1)


# --- Simulation ---
ambiguity_agent = AmbiguityAgent(name="ClaritySeeker", initial_clarity=0.4)

scenarios = [
    "Input: The report is vague, concerning project status.",
    "Input: Can you clarify the 'alpha' directive? It's unclear.",
    "Input: 'Proceed with the next phase, but some context missing.'",
    "Input: 'Please rephrase that. I misunderstood the key phrase.'",
    "Input: 'Very clear instruction: deploy immediately.'",
    "Input: 'The data appears ambiguous, and out of overall context.'",
    "Input: 'Still uncertain about the final objective.'",
    "Input: 'Explicit command: terminate process.'",
    "Input: 'The last feedback was vague. Need more details.'",
    "Input: 'Absolutely understood. Ready to execute.'"
]

for i, scenario_input in enumerate(scenarios):
    print(f"\n--- Scenario {i+1}: '{scenario_input}' ---")
    ambiguity_agent.run_cycle(scenario_input)
    # Simulate a brief pause between scenarios
    time.sleep(1.5)

print("\n--- Ambiguity Resolution Agent Example Finished ---")
