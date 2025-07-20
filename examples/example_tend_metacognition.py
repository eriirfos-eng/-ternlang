# examples/example_metacognition.py
# Demonstrates Ternlang's TEND state triggering a metacognitive/reasoning process.

# Assuming ternlang_prototype.py is in the same parent directory
from ternlang_prototype import REFRAIN, TEND, AFFIRM, TernAgent
import random
import time

print("--- Ternlang Example: Metacognitive Reasoning Agent ---")

class ReasoningAgent(TernAgent):
    """
    A TernAgent that, when in a TEND state, triggers an internal
    "metacognitive" or "reasoning" process to refine its understanding
    or resolve ambiguity before making a definitive AFFIRM or REFRAIN.
    """
    def __init__(self, name="ReasoningAgent", initial_focus="general"):
        super().__init__(name, initial_context="evaluating_situation")
        self.focus = initial_focus # What the agent is currently thinking about
        self.reasoning_steps_taken = 0 # Counter for internal reasoning effort
        self.max_reasoning_steps = 3 # How many times it will TEND for reasoning
        print(f"[{self.name}] Initial focus: '{self.focus}'")

    def observe(self, input_data, other_agent_actions=None):
        """
        Observes input and updates context. If input suggests ambiguity,
        it sets the stage for a TEND state leading to reasoning.
        """
        print(f"[{self.name}] Observing new data: '{input_data}'")
        
        current_context = "neutral"
        relevance_score = 0.5 # Default

        if "ambiguous" in input_data.lower() or "uncertain" in input_data.lower():
            current_context = "ambiguity_detected"
            relevance_score = 0.8
            self.focus = "resolving_ambiguity"
        elif "complex problem" in input_data.lower() or "requires analysis" in input_data.lower():
            current_context = "complex_challenge"
            relevance_score = 0.9
            self.focus = "deep_analysis"
        elif "clear instruction" in input_data.lower() or "simple task" in input_data.lower():
            current_context = "clear_path"
            relevance_score = 0.3
            self.focus = "execution"
        else:
            current_context = "evaluating_situation"
            relevance_score = 0.5
            self.focus = "general"

        self.context = current_context
        print(f"[{self.name}] Context: '{self.context}', Focus: '{self.focus}', Relevance: {relevance_score:.2f}")
        return self.context, relevance_score

    def decide(self, relevance_score):
        """
        Decides the action. If in an ambiguous or complex state,
        it prioritizes TEND to trigger internal reasoning.
        """
        print(f"[{self.name}] Deciding based on context: '{self.context}'...")
        decision = AFFIRM # Default to AFFIRM for simplicity if no strong signal

        if self.context in ["ambiguity_detected", "complex_challenge"]:
            # If we've hit max reasoning steps, we must decide, even if it's REFRAIN
            if self.reasoning_steps_taken >= self.max_reasoning_steps:
                print(f"[{self.name}] Max reasoning steps reached. Must make a definitive decision.")
                # Force a decision, perhaps based on current mood or a final check
                if self.mood > 7: # If relatively positive, lean towards AFFIRM
                    decision = AFFIRM
                else: # If mood is low or neutral, lean towards REFRAIN
                    decision = REFRAIN
            else:
                decision = TEND # Prioritize TEND to perform reasoning
        elif self.context == "clear_path" and relevance_score < 0.5:
            decision = AFFIRM # Simple task, just affirm
        else:
            # For other contexts, use general logic from TernAgent or specific rules
            if self.mood < 5: # If mood is low, lean towards refrain
                decision = REFRAIN
            elif self.mood > 10: # If mood is high, lean towards affirm
                decision = AFFIRM
            else:
                decision = TEND # Default if no strong pull

        print(f"[{self.name}] Decision: {self._get_state_name(decision)}")
        return decision

    def execute_action(self, action):
        """
        Executes the action. If TEND, it simulates a metacognitive process.
        """
        super().execute_action(action) # Call parent method for mood/cognition updates

        if action == TEND:
            print(f"[{self.name}] TENDING: Initiating internal reasoning process for '{self.focus}'...")
            self._perform_reasoning_process()
            self.reasoning_steps_taken += 1
        elif action == AFFIRM:
            print(f"[{self.name}] Proceeding after reasoning/clarity. Resetting reasoning steps.")
            self.reasoning_steps_taken = 0
            self.focus = "general"
        elif action == REFRAIN:
            print(f"[{self.name}] Refraining due to unresolved issues. Resetting reasoning steps.")
            self.reasoning_steps_taken = 0
            self.focus = "general"

    def _perform_reasoning_process(self):
        """
        Simulates an internal metacognitive or reasoning process.
        This is where the agent would 'think' or 'evaluate'.
        """
        print(f"[{self.name}]   (Internal Process) Deep dive into '{self.focus}'...")
        # Simulate cognitive effort
        self.cognition = min(1000, self.cognition + 150)
        # Simulate mood fluctuation based on reasoning difficulty
        self.mood = max(1, min(13, self.mood + random.choice([-2, -1, 0, 1])))
        time.sleep(0.5) # Simulate time taken for reasoning
        
        # After reasoning, the agent's context might subtly shift or become clearer
        # For simplicity, we'll just print a message. In a real system, this
        # might update self.context based on the outcome of the reasoning.
        print(f"[{self.name}]   (Internal Process) Reasoning complete. Current mood: {self.mood}, cognition: {self.cognition}")


# --- Simulation ---
reasoning_agent = ReasoningAgent(name="LogicBot")

scenarios = [
    "Input: Data stream is ambiguous, uncertain source.",
    "Input: Complex problem detected, requires analysis.",
    "Input: Another ambiguous data point. Still uncertain.",
    "Input: Clear instruction received, simple task.",
    "Input: Yet another complex problem, deep analysis needed.",
    "Input: Final ambiguous signal. What to do?",
    "Input: Routine system check, all good."
]

for i, scenario_input in enumerate(scenarios):
    print(f"\n--- Scenario {i+1}: '{scenario_input}' ---")
    reasoning_agent.run_cycle(scenario_input)
    # Simulate a brief pause between scenarios
    time.sleep(1)

print("\n--- Metacognitive Reasoning Agent Example Finished ---")
