# examples/example_temperature_spike.py
# Demonstrates a TernAgent experiencing a sudden "temperature spike"
# (like an emotional event or outside trigger) that causes mood/cognition overload,
# potentially bypassing normal decision logic. Agent reflects on "heat regret" or validation.

# Assuming ternlang_prototype.py is in the same parent directory
from ternlang_prototype import REFRAIN, TEND, AFFIRM, TernAgent
import random
import time
import datetime

print("--- Ternlang Example: Temperature Spike Agent ---")

class SpikeAgent(TernAgent):
    """
    A TernAgent that models sudden internal "temperature spikes" caused by
    external triggers. These spikes can lead to mood jumps, cognition overload,
    and a bypass of normal decision logic, forcing immediate AFFIRM or REFRAIN.
    After the action, the agent reflects and logs "heat regret" or validation.
    """
    def __init__(self, name="SpikeResponder", initial_mood=7):
        super().__init__(name, initial_context="calm")
        self.mood = initial_mood
        self.cognition = 500
        self.is_spiking = False # Flag to indicate if agent is currently in a spike
        self.spike_intensity = 0.0 # 0.0 to 1.0, how strong the current spike is
        self.temperature_spike_threshold = 0.7 # Above this, decision bypass occurs
        self.last_spike_action = None # To log regret/validation
        print(f"[{self.name}] Initialized with Mood: {self.mood}, Cognition: {self.cognition}")

    def observe(self, input_data, other_agent_actions=None):
        """
        Observes input and checks for triggers that cause a temperature spike.
        """
        print(f"[{self.name}] Observing input: '{input_data}'")
        
        current_context = "neutral_observation"
        relevance_score = 0.5 # Default relevance

        # Check for spike triggers
        if "critical threat" in input_data.lower() or "emergency" in input_data.lower():
            self.is_spiking = True
            self.spike_intensity = random.uniform(0.75, 1.0) # High intensity spike
            current_context = "spike_triggered_critical"
            relevance_score = 0.9
            print(f"[{self.name}] --- TEMPERATURE SPIKE TRIGGERED! Intensity: {self.spike_intensity:.2f} ---")
            # Immediate mood/cognition impact
            self.mood = min(13, self.mood + random.randint(3, 5)) # Mood jumps
            self.cognition = min(1000, self.cognition + random.randint(150, 250)) # Cognition overload
        elif "insult" in input_data.lower() or "provoke" in input_data.lower():
            self.is_spiking = True
            self.spike_intensity = random.uniform(0.6, 0.8) # Moderate intensity spike
            current_context = "spike_triggered_emotional"
            relevance_score = 0.7
            print(f"[{self.name}] --- TEMPERATURE SPIKE TRIGGERED! Intensity: {self.spike_intensity:.2f} ---")
            self.mood = max(1, self.mood - random.randint(3, 5)) # Mood drops
            self.cognition = min(1000, self.cognition + random.randint(100, 200)) # Cognition overload
        else:
            self.is_spiking = False # No spike
            self.spike_intensity = 0.0
            # Normal observation logic (simplified for this example)
            if "clear" in input_data.lower():
                current_context = "clear_path"
                relevance_score = 0.8
            elif "ambiguous" in input_data.lower():
                current_context = "ambiguous_input"
                relevance_score = 0.4
            else:
                current_context = "general_observation"
                relevance_score = 0.5

        self.context = current_context
        print(f"[{self.name}] Context: '{self.context}', Mood: {self.mood}, Cognition: {self.cognition}")
        return self.context, relevance_score # Use relevance_score as clarity proxy for decide

    def decide(self, relevance_score, other_agent_decision=None):
        """
        Decides the action. If in a spike, decision may bypass normal logic.
        """
        print(f"[{self.name}] Deciding based on relevance: {relevance_score:.2f}...")
        
        if self.is_spiking and self.spike_intensity >= self.temperature_spike_threshold:
            print(f"[{self.name}] --- SPIKE OVERRIDE! Bypassing normal logic! ---")
            # Decision bypass: force AFFIRM or REFRAIN based on spike type or randomness
            if "critical" in self.context: # Critical spike -> force AFFIRM
                decision = AFFIRM
                print(f"[{self.name}] Forced AFFIRM due to critical spike.")
            elif "emotional" in self.context: # Emotional spike -> random AFFIRM/REFRAIN
                decision = random.choice([AFFIRM, REFRAIN])
                print(f"[{self.name}] Forced {self._get_state_name(decision)} due to emotional spike.")
            else: # Fallback for other spike types
                decision = random.choice([AFFIRM, REFRAIN])
            
            # Mood/cognition already adjusted in observe, but ensure they reflect bypass
            self.cognition = max(0, self.cognition - 100) # Quick decision, cognitive relief
            self.mood = min(13, max(1, self.mood + random.choice([-1, 1]))) # Mood might settle or swing
            
            return decision

        # Normal decision logic (if no spike override)
        decision = TEND # Default
        if relevance_score >= 0.7:
            decision = AFFIRM
            print(f"[{self.name}] High relevance. Ready to AFFIRM.")
        elif relevance_score < 0.3:
            decision = REFRAIN
            print(f"[{self.name}] Low relevance. REFRAINING from action.")
        else:
            decision = TEND
            print(f"[{self.name}] Moderate relevance. TENDING for more information.")

        # Adjust mood and cognition based on normal decision
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
        Executes the action. After a spike-driven action, reflects on "heat regret" or validation.
        """
        super().execute_action(action) # Call parent method for general mood/cognition updates
        self.last_spike_action = action # Store for reflection

        if self.is_spiking and self.spike_intensity >= self.temperature_spike_threshold:
            print(f"[{self.name}] ACTION: Executing under spike influence.")
        elif action == AFFIRM:
            print(f"[{self.name}] ACTION: Proceeding with task.")
        elif action == TEND:
            print(f"[{self.name}] TENDING: Observing further, adjusting, or waiting.")
        elif action == REFRAIN:
            print(f"[{self.name}] REFRAIN: Halting due to uncertainty.")
        else:
            print(f"[{self.name}] WARNING: Unknown action state received: {action}")

    def run_cycle(self, input_data, other_agent_actions=None):
        """
        Performs a full Ternlang cycle for a SpikeAgent.
        [NEW]: Includes post-action reflection on spike events.
        """
        print(f"\n--- [{self.name}] Starting New Cycle ---")
        current_context, relevance_score = self.observe(input_data, other_agent_actions)
        decision = self.decide(relevance_score)
        self.execute_action(decision)

        # [NEW]: Post-action reflection for spike events
        if self.is_spiking and self.spike_intensity >= self.temperature_spike_threshold:
            self._reflect_on_spike_action(decision)
            self.is_spiking = False # Spike subsides after action

        # Log to memory
        self.memory.append({
            "timestamp": datetime.datetime.now().isoformat(),
            "input": input_data,
            "context": current_context,
            "decision": decision,
            "mood": self.mood,
            "cognition": self.cognition,
            "is_spiking": self.is_spiking,
            "spike_intensity": self.spike_intensity
        })

        print(f"--- [{self.name}] Cycle Complete ---")
        return decision

    def _reflect_on_spike_action(self, action_taken):
        """
        [NEW]: Agent reflects on the action taken during a temperature spike.
        Determines "heat regret" or "validation."
        """
        print(f"[{self.name}]   (Reflection) Reflecting on spike-driven action: {self._get_state_name(action_taken)}...")
        
        # Simulate outcome based on action and original context (simplified)
        # In a real system, this would involve evaluating the actual consequence of the action
        regret_or_validation = random.uniform(-1.0, 1.0) # -1.0 = full regret, 1.0 = full validation

        if "critical" in self.context: # If it was a critical spike
            if action_taken == AFFIRM and regret_or_validation > 0:
                print(f"[{self.name}]     (Reflection) Action was AFFIRM. Outcome positive. Validation! (+{regret_or_validation:.2f})")
                self.mood = min(13, self.mood + 2) # Mood boost
            else:
                print(f"[{self.name}]     (Reflection) Action was {self._get_state_name(action_taken)}. Outcome negative. Heat regret! ({regret_or_validation:.2f})")
                self.mood = max(1, self.mood - 3) # Mood drop
        elif "emotional" in self.context: # If it was an emotional spike
            if action_taken == REFRAIN and regret_or_validation > 0:
                print(f"[{self.name}]     (Reflection) Action was REFRAIN. Outcome positive. Validation! (+{regret_or_validation:.2f})")
                self.mood = min(13, self.mood + 1)
            else:
                print(f"[{self.name}]     (Reflection) Action was {self._get_state_name(action_taken)}. Outcome negative. Heat regret! ({regret_or_validation:.2f})")
                self.mood = max(1, self.mood - 2)

        self.cognition = max(0, self.cognition - 50) # Cognitive load from reflection
        time.sleep(1.0)
        print(f"[{self.name}]   (Reflection) Mood after reflection: {self.mood}, Cognition: {self.cognition}")


# --- Simulation ---
def simulate_temperature_spike_agent(num_cycles=8):
    """
    Runs a simulation of a SpikeAgent, demonstrating temperature spike events.
    """
    print("\n--- Ternlang Temperature Spike Agent Simulation Started ---")
    
    spike_agent = SpikeAgent(name="EmotionalResponder", initial_mood=7)

    # Example scenarios designed to trigger spikes and normal behavior
    scenarios = [
        "Input: Routine system check. All seems normal.", # Normal
        "Input: Ambiguous data, needs clarification.", # Normal TEND
        "Input: CRITICAL THREAT DETECTED! IMMEDIATE ACTION REQUIRED!", # High intensity spike -> forced AFFIRM
        "Input: User feedback: 'Your last action was an INSULT!'", # Emotional spike -> random AFFIRM/REFRAIN
        "Input: Clear directive: Stand down.", # Normal REFRAIN
        "Input: EMERGENCY! SYSTEM OVERLOAD IMMINENT! (Critical spike)", # High intensity spike -> forced AFFIRM
        "Input: Another vague report, still no clarity.", # Normal TEND
        "Input: 'You PROVOKED me with that last response!' (Emotional spike)", # Emotional spike
    ]

    for i, scenario_input in enumerate(scenarios):
        print(f"\n===== SCENARIO {i+1}/{len(scenarios)} =====")
        spike_agent.run_cycle(scenario_input)
        time.sleep(2) # Pause for readability

    print("\n--- Ternlang Temperature Spike Agent Simulation Finished ---")

    # Optional: Print final state and memory
    print("\n--- Final Agent State ---")
    print(f"[{spike_agent.name}] Final Mood: {spike_agent.mood}, Cognition: {spike_agent.cognition}, Last Action: {spike_agent._get_state_name(spike_agent.last_action)}")
