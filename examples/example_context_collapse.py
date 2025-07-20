# examples/example_context_collapse.py
# Demonstrates a TernAgent receiving fragmented or contradictory context,
# and attempting to resolve it through TEND, potentially leading to
# "hallucination" (forced clarity) or "schema fusion."

# Assuming ternlang_prototype.py is in the same parent directory
from ternlang_prototype import REFRAIN, TEND, AFFIRM, TernAgent
import random
import time
import datetime

print("--- Ternlang Example: Context Collapse Agent ---")

class ContextCollapseAgent(TernAgent):
    """
    A TernAgent that processes fragmented or contradictory input contexts.
    It attempts to resolve these conflicts through TEND-based internal reasoning.
    If resolution fails, it may "hallucinate" a coherent context or perform "schema fusion."
    """
    def __init__(self, name="CoherenceSeeker", initial_coherence=0.5):
        super().__init__(name, initial_context="fragmented_input")
        self.coherence_score = initial_coherence # 0.0 (contradictory) to 1.0 (fully coherent)
        self.context_fragments = [] # Stores the individual pieces of context
        self.reasoning_steps_taken = 0
        self.max_reasoning_steps = 3 # How many times it will TEND for internal reasoning
        self.hallucination_threshold = 0.3 # If coherence below this after max reasoning, risk hallucination
        
        # Initialize mood and cognition
        self.mood = 7
        self.cognition = 500
        print(f"[{self.name}] Initialized with Coherence: {self.coherence_score:.2f}")

    def observe(self, input_data_list, other_agent_actions=None):
        """
        Observes a list of input data fragments and assesses their initial coherence.
        """
        print(f"[{self.name}] Observing context fragments: {input_data_list}")
        self.context_fragments = input_data_list # Store the fragments
        
        # Simulate initial coherence calculation
        # Simple heuristic: more contradictions = lower coherence
        contradictions = 0
        if "deploy now" in [x.lower() for x in input_data_list] and "wait for confirmation" in [x.lower() for x in input_data_list]:
            contradictions += 1
        if "user feedback unclear" in [x.lower() for x in input_data_list] and "urgency high" in [x.lower() for x in input_data_list]:
            contradictions += 1
        
        # Initial coherence is inverse to contradictions, plus some randomness
        self.coherence_score = max(0.0, min(1.0, 1.0 - (contradictions * 0.3) - random.uniform(0.0, 0.2)))
        
        if self.coherence_score < 0.4:
            self.context = "highly_fragmented"
        elif self.coherence_score < 0.7:
            self.context = "moderately_fragmented"
        else:
            self.context = "mostly_coherent"

        print(f"[{self.name}] Initial context: '{self.context}', Coherence Score: {self.coherence_score:.2f}")
        return self.context, self.coherence_score # Use coherence_score as relevance_score

    def decide(self, coherence_score, other_agent_decision=None):
        """
        Decides the action based on coherence. Prioritizes TEND for resolution.
        May lead to REFRAIN or forced AFFIRM/TEND if context remains collapsed.
        """
        print(f"[{self.name}] Deciding based on coherence: {coherence_score:.2f}...")
        decision = TEND # Default to TEND for resolution

        if coherence_score >= 0.8: # High coherence, proceed
            decision = AFFIRM
            print(f"[{self.name}] High coherence detected. Ready to AFFIRM.")
        elif coherence_score < 0.8 and self.reasoning_steps_taken < self.max_reasoning_steps:
            decision = TEND # Fragmented, but can still reason internally
            print(f"[{self.name}] Fragmented context. TENDING for internal resolution.")
        else: # coherence_score < 0.8 AND max_reasoning_steps reached
            print(f"[{self.name}] Max reasoning steps reached for persistent context collapse.")
            if coherence_score < self.hallucination_threshold:
                # Risk of hallucination or forced interpretation
                print(f"[{self.name}] --- CONTEXT COLLAPSE: Coherence {coherence_score:.2f} too low. Risk of forced interpretation/hallucination. ---")
                # Simulate "hallucination" by forcing a decision, possibly AFFIRM or REFRAIN
                decision = random.choice([AFFIRM, REFRAIN]) # Agent forces a resolution
                self.mood = max(1, self.mood - 2) # Stress of forcing a decision
                self.cognition = min(1000, self.cognition + 150) # High effort to force coherence
            else:
                # Still somewhat coherent, try schema fusion or external help
                print(f"[{self.name}] --- PERSISTENT FRAGMENTATION: Coherence {coherence_score:.2f} still moderate. Attempting schema fusion. ---")
                decision = TEND # Continue tending, maybe seek external help or fuse
                self.mood = max(1, min(13, self.mood - 1)) # Frustration
                self.cognition = min(1000, self.cognition + 100) # Continued effort

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
        Executes the action. If TEND, it performs specific context resolution.
        """
        super().execute_action(action) # Call parent method for general mood/cognition updates

        if action == TEND:
            self.reasoning_steps_taken += 1
            if self.reasoning_steps_taken <= self.max_reasoning_steps:
                print(f"[{self.name}]   (Internal Process) Attempting to resolve context fragments (Step {self.reasoning_steps_taken}/{self.max_reasoning_steps})...")
                self._attempt_context_resolution()
            else:
                print(f"[{self.name}]   (Internal Process) Max resolution attempts reached. Preparing for fusion/hallucination.")
                # This is where the decide method's logic for forced decision/fusion takes over.
        elif action == AFFIRM:
            print(f"[{self.name}] ACTION: Proceeding with (potentially fused) context. Resetting resolution steps.")
            self.reasoning_steps_taken = 0
            self.coherence_score = 1.0 # Assume resolved
        elif action == REFRAIN:
            print(f"[{self.name}] REFRAIN: Halting due to unresolved context collapse. Resetting resolution steps.")
            self.reasoning_steps_taken = 0
            self.coherence_score = 0.0 # Remains collapsed

    def _attempt_context_resolution(self):
        """
        Simulates internal reasoning to try and resolve conflicting context fragments.
        Can improve coherence or make it worse.
        """
        print(f"[{self.name}]     (Resolution) Analyzing relationships between fragments...")
        # Simulate a chance of improving coherence
        if random.random() < 0.6: # 60% chance of improving
            self.coherence_score = min(1.0, self.coherence_score + random.uniform(0.1, 0.3))
            print(f"[{self.name}]     (Resolution) Coherence improved to: {self.coherence_score:.2f}")
        else: # 40% chance of no change or getting worse
            self.coherence_score = max(0.0, self.coherence_score - random.uniform(0.05, 0.1))
            print(f"[{self.name}]     (Resolution) Coherence unchanged or worsened to: {self.coherence_score:.2f}")
        
        self.cognition = min(1000, self.cognition + 80) # High cognitive effort
        time.sleep(0.7)

    def run_cycle(self, input_data_list, other_agent_actions=None):
        """
        Performs a full Ternlang cycle for a ContextCollapseAgent.
        Takes a list of input data fragments.
        """
        print(f"\n--- [{self.name}] Starting New Cycle ---")
        current_context, relevance_score = self.observe(input_data_list, other_agent_actions)
        decision = self.decide(relevance_score)
        self.execute_action(decision)

        # Log to memory
        self.memory.append({
            "timestamp": datetime.datetime.now().isoformat(),
            "input_fragments": input_data_list,
            "context": current_context,
            "decision": decision,
            "mood": self.mood,
            "cognition": self.cognition,
            "coherence": self.coherence_score,
            "reasoning_steps": self.reasoning_steps_taken
        })

        print(f"--- [{self.name}] Cycle Complete ---")
        return decision


# --- Simulation ---
def simulate_context_collapse_agent(num_scenarios=5):
    """
    Runs a simulation of a ContextCollapseAgent, demonstrating its handling
    of fragmented and contradictory contexts.
    """
    print("\n--- Ternlang Context Collapse Agent Simulation Started ---")
    
    collapse_agent = ContextCollapseAgent(name="CoherenceEngine", initial_coherence=0.6)

    # Example scenarios with fragmented/contradictory inputs
    scenarios = [
        ["Deploy now.", "Wait for confirmation."], # Contradictory
        ["User feedback unclear.", "Urgency high."], # Conflicting directives
        ["All systems nominal.", "Minor anomaly detected."], # Slight contradiction
        ["Data stream stable.", "Proceed with caution."], # Ambiguous directive
        ["Critical error detected.", "System shows green status."], # High contradiction
        ["Clear instruction: proceed.", "No conflicting data."], # Coherent
        ["Fragmented report: 'Alpha is ready.'", "Fragmented report: 'Beta is not.'", "Fragmented report: 'Proceed with Alpha.'"], # Partially coherent
        ["Conflicting reports on resource availability.", "Need decision immediately."], # Contradictory + urgency
    ]

    for i, scenario_input_list in enumerate(scenarios):
        print(f"\n===== SCENARIO {i+1}/{len(scenarios)} =====")
        collapse_agent.run_cycle(scenario_input_list)
        time.sleep(2) # Pause for readability

    print("\n--- Ternlang Context Collapse Agent Simulation Finished ---")

    # Optional: Print final state and memory
    print("\n--- Final Agent State ---")
    print(f"[{collapse_agent.name}] Final Mood: {collapse_agent.mood}, Cognition: {collapse_agent.cognition}, Coherence: {collapse_agent.coherence_score:.2f}, Last Action: {collapse_agent._get_state_name(collapse_agent.last_action)}")
