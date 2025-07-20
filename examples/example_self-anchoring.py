# examples/example_self-anchoring.py
# Demonstrates a TernAgent using its prior decisions stored in memory
# to guide its current one, creating a "recursive bias" or "self-anchoring" effect.
# This represents a first true recursive loop in decision-making based on self-history.

# Assuming ternlang_prototype.py is in the same parent directory
from ternlang_prototype import REFRAIN, TEND, AFFIRM, TernAgent
import random
import time
import datetime
import uuid
# Import memory manager for persistent memory access
from ternlang_memory_manager import save_agent_memory, load_agent_memory, DEFAULT_MEMORY_FILE_PATH

print("--- Ternlang Example: Self-Anchoring Agent ---")

class SelfAnchoringAgent(TernAgent):
    """
    A TernAgent that develops a "self-anchoring bias" by analyzing its own
    past decisions stored in memory. This bias can influence or even override
    current decisions, creating a recursive feedback loop based on its history.
    """
    def __init__(self, name="AnchorBot", initial_mood=7):
        super().__init__(name, initial_context="observing")
        self.mood = initial_mood
        self.cognition = 500
        self.clarity_score = 0.5 # General clarity for current input
        
        # [NEW]: Self-anchoring bias attributes
        self.anchoring_bias = TEND # Default bias if no strong pattern found
        self.anchoring_strength = 0.0 # 0.0 to 1.0, how strong the bias is
        self.history_window_size = 5 # Number of recent memory entries to analyze
        self.bias_threshold = 0.6 # Percentage of dominant decisions to form a strong bias

        # Memory will be loaded from persistent storage
        self.memory = [] 
        
        print(f"[{self.name}] Initialized with Mood: {self.mood}, Cognition: {self.cognition}")

    def _analyze_decision_history(self):
        """
        Analyzes the agent's recent decision history to determine a self-anchoring bias.
        Calculates the dominant decision and its strength.
        """
        recent_decisions = [
            entry["Decision"] for entry in self.memory[-self.history_window_size:]
            if "Decision" in entry # Ensure 'Decision' key exists
        ]
        
        if not recent_decisions:
            self.anchoring_bias = TEND
            self.anchoring_strength = 0.0
            return

        decision_counts = {REFRAIN: 0, TEND: 0, AFFIRM: 0}
        for decision_name in recent_decisions:
            # Convert decision name back to integer value for counting
            if decision_name == self._get_state_name(REFRAIN):
                decision_counts[REFRAIN] += 1
            elif decision_name == self._get_state_name(TEND):
                decision_counts[TEND] += 1
            elif decision_name == self._get_state_name(AFFIRM):
                decision_counts[AFFIRM] += 1
        
        total_decisions = len(recent_decisions)
        if total_decisions == 0:
            self.anchoring_bias = TEND
            self.anchoring_strength = 0.0
            return

        dominant_decision_value = TEND
        max_count = 0
        
        # Determine the most frequent decision
        for decision_val, count in decision_counts.items():
            if count > max_count:
                max_count = count
                dominant_decision_value = decision_val
            # Tie-breaking: prefer AFFIRM > TEND > REFRAIN if counts are equal (arbitrary)
            elif count == max_count:
                if dominant_decision_value == REFRAIN and decision_val != REFRAIN:
                    dominant_decision_value = decision_val
                elif dominant_decision_value == TEND and decision_val == AFFIRM:
                    dominant_decision_value = decision_val

        self.anchoring_bias = dominant_decision_value
        self.anchoring_strength = max_count / total_decisions

        print(f"[{self.name}]   (Self-Anchoring) Analyzed history: Dominant bias is {self._get_state_name(self.anchoring_bias)} with strength {self.anchoring_strength:.2f}")


    def observe(self, input_data, other_agent_actions=None):
        """
        Observes input and sets initial clarity.
        """
        print(f"[{self.name}] Observing input: '{input_data}'")
        
        current_context = "neutral_observation"
        
        # Simulate clarity calculation
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

    def decide(self, relevance_score, other_agent_decision=None):
        """
        Decides the action, incorporating self-anchoring bias.
        The bias can override clarity if strong enough and pattern matches.
        """
        print(f"[{self.name}] Deciding based on clarity: {relevance_score:.2f}...")
        
        # First, analyze history to get current bias
        self._analyze_decision_history()

        # Determine initial decision based on current clarity
        if relevance_score >= 0.7:
            initial_decision = AFFIRM
        elif relevance_score < 0.3:
            initial_decision = REFRAIN
        else:
            initial_decision = TEND
        
        print(f"[{self.name}]   Initial decision based on clarity: {self._get_state_name(initial_decision)}")

        # [NEW]: Apply self-anchoring bias
        final_decision = initial_decision
        if self.anchoring_strength >= self.bias_threshold:
            if self.anchoring_bias == AFFIRM and initial_decision != AFFIRM:
                # If strong AFFIRM bias, and not already AFFIRMING, try to override
                if relevance_score > 0.4: # Don't override if extremely unclear
                    final_decision = AFFIRM
                    print(f"[{self.name}]   Self-anchoring (AFFIRM) overrides to AFFIRM.")
                    self.mood = min(13, self.mood + 1) # Mood boost from consistent action
                    self.cognition = max(0, self.cognition - 30) # Reduced cognitive load
            elif self.anchoring_bias == REFRAIN and initial_decision != REFRAIN:
                # If strong REFRAIN bias, and not already REFRAINING, try to override
                if relevance_score < 0.6: # Don't override if extremely clear
                    final_decision = REFRAIN
                    print(f"[{self.name}]   Self-anchoring (REFRAIN) overrides to REFRAIN.")
                    self.mood = max(1, self.mood - 1) # Mood dip from caution
                    self.cognition = min(1000, self.cognition + 30) # Increased cognitive load for override
            elif self.anchoring_bias == TEND and initial_decision != TEND:
                # If strong TEND bias, and not already TENDING, try to override
                final_decision = TEND
                print(f"[{self.name}]   Self-anchoring (TEND) overrides to TEND.")
                self.mood = max(1, min(13, self.mood + random.choice([-1, 0, 1])))
                self.cognition = min(1000, self.cognition + 20)
        
        # Adjust mood and cognition based on final decision (if not already adjusted by bias override)
        if final_decision == TEND and initial_decision != TEND and self.anchoring_bias != TEND: # Avoid double adjustment
            self.cognition = min(1000, self.cognition + 50)
            self.mood = max(1, min(13, self.mood - 1))
        elif final_decision == REFRAIN and initial_decision != REFRAIN and self.anchoring_bias != REFRAIN:
            self.cognition = max(0, self.cognition - 30)
            self.mood = max(1, self.mood - 2)
        elif final_decision == AFFIRM and initial_decision != AFFIRM and self.anchoring_bias != AFFIRM:
            self.cognition = max(0, self.cognition - 20)
            self.mood = min(13, self.mood + 1)

        print(f"[{self.name}] Final decision: {self._get_state_name(final_decision)}")
        return final_decision

    def execute_action(self, action):
        """
        Executes the action.
        """
        super().execute_action(action)

        if action == AFFIRM:
            print(f"[{self.name}] ACTION: Proceeding with task.")
        elif action == TEND:
            print(f"[{self.name}] TENDING: Observing further, adjusting, or waiting.")
        elif action == REFRAIN:
            print(f"[{self.name}] REFRAIN: Halting due to uncertainty.")
        else:
            print(f"[{self.name}] WARNING: Unknown action state received: {action}")

    def run_cycle(self, input_data, other_agent_actions=None):
        """
        Performs a full Ternlang cycle for a SelfAnchoringAgent.
        Includes memory logging and auto-save.
        """
        print(f"\n--- [{self.name}] Starting New Cycle ---")
        current_context, relevance_score = self.observe(input_data, other_agent_actions)
        decision = self.decide(relevance_score)
        self.execute_action(decision)

        now = datetime.datetime.now()
        
        memory_entry = {
            "ID": str(uuid.uuid4()),
            "Timestamp": now.isoformat(),
            "Weekday": now.strftime("%A"),
            "AgentName": self.name,
            "Input": input_data,
            "Context": current_context,
            "Decision": self._get_state_name(decision),
            "Mood Barometer (1–13)": self.mood,
            "Cognition Barometer (0-1000)": self.cognition,
            "Impact Barometer (1–13)": random.randint(1, 13),
            
            "Summary": "Agent processed input and made a decision.",
            "Flags/Reminders": [],
            "Milestone Events": [],
            "Lessons Learned": [],
            "Approach Adjustments": [],
            "Pending Action Items": [],
            "Timestamp Notes": "",

            # Self-anchoring specific fields
            "AnchoringBias": self._get_state_name(self.anchoring_bias),
            "AnchoringStrength": round(self.anchoring_strength, 2)
        }

        # Conditionally populate generic qualitative fields
        if "critical" in current_context:
            memory_entry["Summary"] = "Critical event detected."
        if "emotional" in current_context:
            memory_entry["Summary"] = "Emotional trigger detected."
        
        if decision == AFFIRM:
            memory_entry["Summary"] = f"Agent affirmed: {input_data[:30]}..."
        elif decision == REFRAIN:
            memory_entry["Summary"] = f"Agent refrained: {input_data[:30]}..."
        elif decision == TEND:
            memory_entry["Summary"] = f"Agent tended: {input_data[:30]}..."

        self.memory.append(memory_entry)

        # Auto-save memory every 15 minutes (or more frequently for simulation)
        # For simulation, we might save more often to see persistence in action
        if (datetime.datetime.now() - self.last_save_time).total_seconds() >= (1 * 60): # Save every 1 minute for demo
            save_agent_memory(self, MEMORY_FILE_PATH)
            self.last_save_time = datetime.datetime.now()

        print(f"--- [{self.name}] Cycle Complete ---")
        return decision

# --- Simulation ---
def simulate_self_anchoring_agent(num_cycles=15):
    """
    Runs a simulation of a SelfAnchoringAgent, demonstrating recursive bias.
    """
    print("\n--- Ternlang Self-Anchoring Agent Simulation Started ---")
    
    anchoring_agent = SelfAnchoringAgent(name="ConsistentBot", initial_mood=7)
    load_agent_memory(anchoring_agent, MEMORY_FILE_PATH) # Load memory at start

    # Scenarios designed to build a bias and then test it
    scenarios = [
        "Input: Clear directive to proceed.", # Should lead to AFFIRM
        "Input: Another clear task, affirm.", # Should lead to AFFIRM
        "Input: Ambiguous situation, but lean towards action.", # Try to build AFFIRM bias
        "Input: Very clear instruction: AFFIRM!", # Reinforce AFFIRM
        "Input: Unclear data, consider waiting.", # Might be TEND, testing bias
        "Input: Highly ambiguous, but historically I AFFIRM.", # Test if bias overrides
        "Input: Clear instruction to REFRAIN.", # Test if bias can be overridden
        "Input: Another clear instruction to REFRAIN.", # Try to build REFRAIN bias
        "Input: Ambiguous situation, but historically I REFRAIN.", # Test if bias overrides
        "Input: Very clear instruction: REFRAIN!", # Reinforce REFRAIN
        "Input: Unclear data, consider waiting.", # Might be TEND, testing bias
        "Input: Highly ambiguous, but historically I REFRAIN.", # Test if bias overrides
        "Input: Routine task, proceed.", # Test if bias still holds or adapts
        "Input: Ambiguous, but I've been tending a lot.", # Test TEND bias
        "Input: Very clear instruction: AFFIRM!", # Final test
    ]

    for i in range(num_cycles):
        print(f"\n===== SIMULATION CYCLE {i+1}/{num_cycles} =====")
        current_input = scenarios[i % len(scenarios)] 
        anchoring_agent.run_cycle(current_input)
        time.sleep(1.5) # Pause for readability

    print("\n--- Ternlang Self-Anchoring Agent Simulation Finished ---")

    save_agent_memory(anchoring_agent, MEMORY_FILE_PATH) # Save memory at end

    print("\n--- Sample of Agent Memory (Structured) ---")
    for entry in anchoring_agent.memory[-min(5, len(anchoring_agent.memory)):]: # Show last 5 entries
        for key, value in entry.items():
            print(f"  {key}: {value}")
        print("  ---")

    print("\n--- Final Agent State ---")
    print(f"[{anchoring_agent.name}] Final Mood: {anchoring_agent.mood}, Cognition: {anchoring_agent.cognition}, Last Action: {anchoring_agent._get_state_name(anchoring_agent.last_action)}")
    print(f"[{anchoring_agent.name}] Final Anchoring Bias: {anchoring_agent._get_state_name(anchoring_agent.anchoring_bias)}, Strength: {anchoring_agent.anchoring_strength:.2f}")
