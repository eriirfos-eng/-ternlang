# examples/example_temperature_spike.py
# Demonstrates a TernAgent experiencing a sudden "temperature spike"
# (like an emotional event or outside trigger) that causes mood/cognition overload,
# potentially bypassing normal decision logic. Agent reflects on "heat regret" or validation.
# [UPDATED]: Now fully utilizes the `MemoryManager` class for all memory operations.

# Assuming ternlang_prototype.py is in the same parent directory
from ternlang_prototype import REFRAIN, TEND, AFFIRM, TernAgent
import random
import time
import datetime
import uuid # Still useful for generating IDs if needed before passing to MemoryManager

# [NEW]: No direct json or os imports needed here, handled by MemoryManager
# [NEW]: No MEMORY_FILE_PATH constant needed here if using default, or pass it to agent init

print("--- Ternlang Example: Temperature Spike Agent ---")

class SpikeAgent(TernAgent):
    """
    A TernAgent that models sudden internal "temperature spikes" caused by
    external triggers. These spikes can lead to mood jumps, cognition overload,
    and a bypass of normal decision logic, forcing immediate AFFIRM or REFRAIN.
    After the action, the agent reflects and logs "heat regret" or validation.
    """
    def __init__(self, name="SpikeResponder", initial_mood=7):
        super().__init__(name, initial_context="calm") # TernAgent now initializes MemoryManager
        self.mood = initial_mood # Re-initialize mood/cognition after super() call if needed
        self.cognition = 500
        self.is_spiking = False
        self.spike_intensity = 0.0
        self.temperature_spike_threshold = 0.7
        self.last_spike_action = None
        
        # [REMOVED]: self.last_save_time is now managed by MemoryManager
        
        print(f"[{self.name}] Initialized with Mood: {self.mood}, Cognition: {self.cognition}")

    def observe(self, input_data, other_agent_actions=None):
        """
        Observes input and checks for triggers that cause a temperature spike.
        """
        print(f"[{self.name}] Observing input: '{input_data}'")
        
        current_context = "neutral_observation"
        relevance_score = 0.5

        if "critical threat" in input_data.lower() or "emergency" in input_data.lower():
            self.is_spiking = True
            self.spike_intensity = random.uniform(0.75, 1.0)
            current_context = "spike_triggered_critical"
            relevance_score = 0.9
            print(f"[{self.name}] --- TEMPERATURE SPIKE TRIGGERED! Intensity: {self.spike_intensity:.2f} ---")
            self.mood = min(13, self.mood + random.randint(3, 5))
            self.cognition = min(1000, self.cognition + random.randint(150, 250))
        elif "insult" in input_data.lower() or "provoke" in input_data.lower():
            self.is_spiking = True
            self.spike_intensity = random.uniform(0.6, 0.8)
            current_context = "spike_triggered_emotional"
            relevance_score = 0.7
            print(f"[{self.name}] --- TEMPERATURE SPIKE TRIGGERED! Intensity: {self.spike_intensity:.2f} ---")
            self.mood = max(1, self.mood - random.randint(3, 5))
            self.cognition = min(1000, self.cognition + random.randint(100, 200))
        else:
            self.is_spiking = False
            self.spike_intensity = 0.0
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
        return self.context, relevance_score

    def decide(self, relevance_score, other_agent_decision=None):
        """
        Decides the action. If in a spike, decision may bypass normal logic.
        """
        print(f"[{self.name}] Deciding based on relevance: {relevance_score:.2f}...")
        
        if self.is_spiking and self.spike_intensity >= self.temperature_spike_threshold:
            print(f"[{self.name}] --- SPIKE OVERRIDE! Bypassing normal logic! ---")
            if "critical" in self.context:
                decision = AFFIRM
                print(f"[{self.name}] Forced AFFIRM due to critical spike.")
            elif "emotional" in self.context:
                decision = random.choice([AFFIRM, REFRAIN])
                print(f"[{self.name}] Forced {self._get_state_name(decision)} due to emotional spike.")
            else:
                decision = random.choice([AFFIRM, REFRAIN])
            
            self.cognition = max(0, self.cognition - 100)
            self.mood = min(13, max(1, self.mood + random.choice([-1, 1])))
            
            return decision

        decision = TEND
        if relevance_score >= 0.7:
            decision = AFFIRM
            print(f"[{self.name}] High relevance. Ready to AFFIRM.")
        elif relevance_score < 0.3:
            decision = REFRAIN
            print(f"[{self.name}] Low relevance. REFRAINING from action.")
        else:
            decision = TEND
            print(f"[{self.name}] Moderate relevance. TENDING for more information.")

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
        super().execute_action(action)
        self.last_spike_action = action

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
        Includes post-action reflection on spike events.
        Memory logging now uses a generic, broadly applicable structured format.
        Implements 15-minute auto-save for memory.
        """
        print(f"\n--- [{self.name}] Starting New Cycle ---")
        current_context, relevance_score = self.observe(input_data, other_agent_actions)
        decision = self.decide(relevance_score)
        self.execute_action(decision)

        if self.is_spiking and self.spike_intensity >= self.temperature_spike_threshold:
            self._reflect_on_spike_action(decision)
            self.is_spiking = False

        # [UPDATED]: Add entry via MemoryManager
        self.memory_manager.add_entry(
            input_data=input_data,
            context=current_context,
            decision=decision, # Pass the integer value, MemoryManager converts to name
            mood=self.mood,
            cognition=self.cognition,
            impact=random.randint(1, 13), # Generic placeholder for impact
            
            Summary="Agent processed input and made a decision.",
            Flags_Reminders=[],
            Milestone_Events=[],
            Lessons_Learned=[],
            Approach_Adjustments=[],
            Pending_Action_Items=[],
            Timestamp_Notes="", # Use underscore for consistent dictionary keys

            IsSpiking=self.is_spiking,
            SpikeIntensity=round(self.spike_intensity, 2),
            LastSpikeAction=self._get_state_name(self.last_spike_action) if self.last_spike_action else "None"
        )

        # Conditionally populate generic qualitative fields (passed as kwargs to add_entry)
        if "critical" in current_context:
            self.memory_manager.entries[-1]["Summary"] = "Critical event detected. Agent reacted under spike influence."
            self.memory_manager.entries[-1]["Flags_Reminders"].append("Critical event handled.")
        if "emotional" in current_context:
            self.memory_manager.entries[-1]["Summary"] = "Emotional trigger detected. Agent reacted impulsively."
            self.memory_manager.entries[-1]["Flags_Reminders"].append("Emotional response observed.")
        
        if "post_spike_regret" in self.context: 
            self.memory_manager.entries[-1]["Lessons_Learned"].append("Experienced 'heat regret' from impulsive action.")
            self.memory_manager.entries[-1]["Approach_Adjustments"].append("Review impulse control mechanisms.")
        elif "post_spike_validation" in self.context:
            self.memory_manager.entries[-1]["Lessons_Learned"].append("Action during spike was validated.")
            self.memory_manager.entries[-1]["Approach_Adjustments"].append("Validate rapid response protocols.")
        
        if decision == REFRAIN and "ambiguous" in input_data.lower():
            self.memory_manager.entries[-1]["Pending_Action_Items"].append("Seek clarification for ambiguous input.")
            self.memory_manager.entries[-1]["Summary"] = "Agent refrained due to ambiguity, pending clarification."

        # [UPDATED]: Auto-save logic is now handled by MemoryManager's check_and_save
        # self.memory_manager.check_and_save() is called internally by add_entry
        # Or, you can explicitly call it here if you want more control:
        # self.memory_manager.check_and_save()

        print(f"--- [{self.name}] Cycle Complete ---")
        return decision

    def _reflect_on_spike_action(self, action_taken):
        """
        Agent reflects on the action taken during a temperature spike.
        Determines "heat regret" or "validation."
        """
        print(f"[{self.name}]   (Reflection) Reflecting on spike-driven action: {self._get_state_name(action_taken)}...")
        
        regret_or_validation = random.uniform(-1.0, 1.0)

        if "critical" in self.context:
            if action_taken == AFFIRM and regret_or_validation > 0:
                print(f"[{self.name}]     (Reflection) Action was AFFIRM. Outcome positive. Validation! (+{regret_or_validation:.2f})")
                self.mood = min(13, self.mood + 2)
                self.context = "post_spike_validation"
            else:
                print(f"[{self.name}]     (Reflection) Action was {self._get_state_name(action_taken)}. Outcome negative. Heat regret! ({regret_or_validation:.2f})")
                self.mood = max(1, self.mood - 3)
                self.context = "post_spike_regret"
        elif "emotional" in self.context:
            if action_taken == REFRAIN and regret_or_validation > 0:
                print(f"[{self.name}]     (Reflection) Action was REFRAIN. Outcome positive. Validation! (+{regret_or_validation:.2f})")
                self.mood = min(13, self.mood + 1)
                self.context = "post_spike_validation"
            else:
                print(f"[{self.name}]     (Reflection) Action was {self._get_state_name(action_taken)}. Outcome negative. Heat regret! ({regret_or_validation:.2f})")
                self.mood = max(1, self.mood - 2)
                self.context = "post_spike_regret"

        self.cognition = max(0, self.cognition - 50)
        time.sleep(1.0)
        print(f"[{self.name}]   (Reflection) Mood after reflection: {self.mood}, Cognition: {self.cognition}")


# --- Simulation ---
def simulate_temperature_spike_agent(num_cycles=8):
    """
    Runs a simulation of a SpikeAgent, demonstrating temperature spike events.
    Includes loading and saving of persistent memory via MemoryManager.
    """
    print("\n--- Ternlang Temperature Spike Agent Simulation Started ---")
    
    spike_agent = SpikeAgent(name="EmotionalResponder", initial_mood=7)
    # [REMOVED]: load_agent_memory is now called by MemoryManager's __init__
    # load_agent_memory(spike_agent, MEMORY_FILE_PATH) 

    scenarios = [
        "Input: Routine system check. All seems normal.",
        "Input: Ambiguous data, needs clarification.",
        "Input: CRITICAL THREAT DETECTED! IMMEDIATE ACTION REQUIRED!",
        "Input: User feedback: 'Your last action was an INSULT!'",
        "Input: Clear directive: Stand down.",
        "Input: EMERGENCY! SYSTEM OVERLOAD IMMINENT! (Critical spike)",
        "Input: Another vague report, still no clarity.",
        "Input: 'You PROVOKED me with that last response!' (Emotional spike)",
    ]

    for i in range(num_cycles):
        print(f"\n===== SIMULATION CYCLE {i+1}/{len(scenarios)} =====")
        current_input = scenarios[i % len(scenarios)] 
        spike_agent.run_cycle(current_input)
        time.sleep(2)

    print("\n--- Ternlang Temperature Spike Agent Simulation Finished ---")

    # [UPDATED]: Save memory at the end of simulation via MemoryManager
    spike_agent.memory_manager.save_to_file() 

    print("\n--- Sample of Agent Memory (Structured) ---")
    for entry in spike_agent.memory_manager.get_recent_entries(min(5, len(spike_agent.memory_manager.entries))): # Access via memory_manager
        for key, value in entry.items():
            print(f"  {key}: {value}")
        print("  ---")

    print("\n--- Final Agent State ---")
    print(f"[{spike_agent.name}] Final Mood: {spike_agent.mood}, Cognition: {spike_agent.cognition}, Last Action: {spike_agent._get_state_name(spike_agent.last_action)}")
