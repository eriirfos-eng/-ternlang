# examples/example_recursive_meta_reflection.py
# Demonstrates a TernAgent that detects when it is "loop-locked" (e.g., keeps TENDING
# due to unclear inputs). It then enters a "meta-reflection mode" to evaluate
# if the current loop is productive and potentially triggers context_collapse
# or asks for a schema update.

# Assuming ternlang_prototype.py is in the same parent directory
from ternlang_prototype import REFRAIN, TEND, AFFIRM, TernAgent
import random
import time
import datetime
import uuid
# MemoryManager is automatically imported via TernAgent's super().__init__()

print("--- Ternlang Example: Recursive Meta-Reflection Agent ---")

class MetaReflectionAgent(TernAgent):
    """
    A TernAgent capable of recursive meta-reflection. It monitors its own
    progress, detects unproductive loops (e.g., repeated TENDs without clarity change),
    and can then enter a meta-reflection mode to analyze its internal state
    and potentially adjust its approach or seek external help.
    """
    def __init__(self, name="MetaThinker", initial_mood=7):
        super().__init__(name, initial_context="observing_environment")
        self.mood = initial_mood
        self.cognition = 500
        self.clarity_score = 0.5 # 0.0 (uncertain) to 1.0 (clear)
        self.reasoning_steps_taken = 0 # Counter for internal reasoning within a TEND loop
        self.max_reasoning_steps = 4 # Max TENDs before considering meta-reflection

        self.last_clarity_for_progress_check = self.clarity_score
        self.stale_progress_threshold = 0.05 # Min clarity change to count as progress
        self.consecutive_stale_cycles = 0 # Counter for cycles with no significant progress
        self.stuck_loop_threshold = 2 # Number of stale cycles to trigger meta-reflection

        self.is_meta_reflecting = False # Flag for meta-reflection mode
        self.meta_reflection_rounds = 0
        self.max_meta_reflection_rounds = 1 # Max rounds of meta-reflection before escalation

        print(f"[{self.name}] Initialized. Mood={self.mood}, Cognition={self.cognition}")

    def observe(self, input_data, other_agent_actions=None):
        """
        Observes input and calculates initial clarity.
        Also monitors for signs of being stuck in a loop.
        """
        print(f"[{self.name}] Observing input: '{input_data}'")
        
        current_context = "neutral_observation"
        
        # Simulate clarity calculation based on keywords
        previous_clarity = self.clarity_score # Store for progress check
        if "unclear" in input_data.lower() or "vague" in input_data.lower():
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

        # [NEW]: Check for progress stagnation
        if self.last_action == TEND:
            clarity_delta = abs(self.clarity_score - previous_clarity)
            if clarity_delta < self.stale_progress_threshold:
                self.consecutive_stale_cycles += 1
                print(f"[{self.name}]   (Progress Check) Low clarity delta ({clarity_delta:.2f}). Consecutive stale cycles: {self.consecutive_stale_cycles}")
            else:
                self.consecutive_stale_cycles = 0 # Reset if progress made
        else:
            self.consecutive_stale_cycles = 0 # Reset on non-TEND action

        self.context = current_context
        print(f"[{self.name}] Context: '{self.context}', Clarity: {self.clarity_score:.2f}")
        return self.context, self.clarity_score # clarity_score as relevance for decide

    def decide(self, relevance_score, other_agent_decision=None):
        """
        Decides the action. Prioritizes meta-reflection if stuck in a loop.
        """
        print(f"[{self.name}] Deciding based on clarity: {relevance_score:.2f}...")
        
        # [NEW]: Meta-reflection trigger
        if self.consecutive_stale_cycles >= self.stuck_loop_threshold and not self.is_meta_reflecting:
            print(f"[{self.name}] --- LOOP-LOCKED DETECTED! Triggering Meta-Reflection! ---")
            self.is_meta_reflecting = True
            self.meta_reflection_rounds = 0 # Reset meta-reflection counter
            self.context = "meta_reflection_phase"
            # Force TEND to perform meta-reflection
            decision = TEND
            self.mood = max(1, min(13, self.mood - 1)) # Stress of realizing stagnation
            self.cognition = min(1000, self.cognition + 150) # High cognitive load for meta-analysis
            return decision
        
        if self.is_meta_reflecting:
            self.meta_reflection_rounds += 1
            if self.meta_reflection_rounds <= self.max_meta_reflection_rounds:
                print(f"[{self.name}]   (Meta-Reflection) Deciding to TEND for deeper meta-analysis.")
                decision = TEND
            else:
                print(f"[{self.name}]   (Meta-Reflection) Max meta-reflection rounds reached. Escalating or forcing action.")
                # After exhausting meta-reflection, agent must decide to REFRAIN (escalate) or AFFIRM (force a path)
                if self.clarity_score < 0.5: # If still unclear, REFRAIN and ask for help
                    decision = REFRAIN
                    self.context = "escalate_for_schema_update"
                    print(f"[{self.name}]   Meta-reflection exhausted. REFRAINING: Requesting schema update/human intervention.")
                else: # If some clarity gained, AFFIRM a path
                    decision = AFFIRM
                    self.context = "forced_path_after_reflection"
                    print(f"[{self.name}]   Meta-reflection exhausted. AFFIRMING: Forcing a path based on best available understanding.")
                self.is_meta_reflecting = False # Exit meta-reflection
            return decision

        # Normal decision logic (if not in meta-reflection)
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
        Executes the action. Special handling for meta-reflection.
        """
        super().execute_action(action)

        if self.context == "meta_reflection_phase" and action == TEND:
            print(f"[{self.name}] ACTION: Performing deep meta-analysis of internal loops...")
            self._perform_meta_reflection()
        elif action == AFFIRM:
            print(f"[{self.name}] ACTION: Proceeding with task.")
            self.reasoning_steps_taken = 0
            self.consecutive_stale_cycles = 0
        elif action == TEND:
            print(f"[{self.name}] TENDING: Observing further, adjusting, or waiting.")
            self.reasoning_steps_taken += 1 # Increment for normal TEND
        elif action == REFRAIN:
            print(f"[{self.name}] REFRAIN: Halting due to uncertainty or escalation.")
            self.reasoning_steps_taken = 0
            self.consecutive_stale_cycles = 0
        else:
            print(f"[{self.name}] WARNING: Unknown action state received: {action}")

    def _perform_meta_reflection(self):
        """
        Simulates the agent's internal meta-reflection process.
        It analyzes its own state and potentially gains new clarity or
        identifies a need for external input/schema update.
        """
        print(f"[{self.name}]     (Meta-Reflection) Analyzing past decisions, cognitive load, mood trends...")
        # Simulate potential outcome of meta-reflection
        if random.random() < 0.4: # 40% chance of gaining some clarity
            self.clarity_score = min(1.0, self.clarity_score + random.uniform(0.1, 0.2))
            print(f"[{self.name}]     (Meta-Reflection) Gained some clarity through self-analysis: {self.clarity_score:.2f}")
            self.mood = min(13, self.mood + 1) # Mood boost from insight
        else:
            print(f"[{self.name}]     (Meta-Reflection) Self-analysis did not yield significant new clarity.")
            self.clarity_score = max(0.0, self.clarity_score - random.uniform(0.02, 0.05)) # Might even drop slightly
            self.mood = max(1, self.mood - 1) # Mood dip from frustration
        
        self.cognition = min(1000, self.cognition + 50) # Continued cognitive effort
        time.sleep(1.0)
        print(f"[{self.name}]     (Meta-Reflection) Current Mood: {self.mood}, Cognition: {self.cognition}")

    def run_cycle(self, input_data, other_agent_actions=None):
        """
        Performs a full Ternlang cycle for a MetaReflectionAgent.
        """
        print(f"\n--- [{self.name}] Starting New Cycle ---")
        current_context, relevance_score = self.observe(input_data, other_agent_actions)
        decision = self.decide(relevance_score)
        self.execute_action(decision)

        # Add entry via MemoryManager
        self.memory_manager.add_entry(
            input_data=input_data,
            context=current_context,
            decision=decision,
            mood=self.mood,
            cognition=self.cognition,
            impact=random.randint(1, 13),
            
            Summary="Agent completed cycle.",
            Flags_Reminders=[],
            Milestone_Events=[],
            Lessons_Learned=[],
            Approach_Adjustments=[],
            Pending_Action_Items=[],
            Timestamp_Notes="",

            ClarityScore=round(self.clarity_score, 2),
            ReasoningStepsTaken=self.reasoning_steps_taken,
            ConsecutiveStaleCycles=self.consecutive_stale_cycles,
            IsMetaReflecting=self.is_meta_reflecting,
            MetaReflectionRounds=self.meta_reflection_rounds
        )

        print(f"--- [{self.name}] Cycle Complete ---")
        return decision

# --- Simulation ---
def simulate_meta_reflection_agent(num_cycles=15):
    """
    Runs a simulation of a MetaReflectionAgent, demonstrating loop detection and meta-reflection.
    """
    print("\n--- Ternlang Recursive Meta-Reflection Agent Simulation Started ---")
    
    meta_agent = MetaReflectionAgent(name="SelfAwareBot", initial_mood=7)
    meta_agent.memory_manager.load_from_file() # Load memory at start

    # Scenarios designed to trigger normal behavior, then a stuck loop, then meta-reflection
    scenarios = [
        "Input: Clear directive to proceed.", # AFFIRM
        "Input: Ambiguous data, needs clarification.", # TEND
        "Input: Still vague, no new info.", # TEND, 1 stale
        "Input: Extremely unclear input. Cannot resolve.", # TEND, 2 stale -> Trigger meta-reflection
        "Input: Continuing to analyze internal state.", # TEND (meta-reflection)
        "Input: Still stuck after internal review.", # TEND (meta-reflection, max rounds reached -> REFRAIN/AFFIRM)
        "Input: New, very clear instructions provided.", # After reflection, should act normally
        "Input: Another ambiguous task.", # TEND
        "Input: Vague, but I have a strong feeling.", # TEND, 1 stale
        "Input: Still no progress. Stuck again.", # TEND, 2 stale -> Trigger meta-reflection
        "Input: Deep internal thought process.", # TEND (meta-reflection)
        "Input: Fresh perspective gained. Proceeding.", # AFFIRM (after reflection)
        "Input: Final task, all clear." # AFFIRM
    ]

    for i in range(num_cycles):
        print(f"\n===== SIMULATION CYCLE {i+1}/{num_cycles} =====")
        current_input = scenarios[i % len(scenarios)] 
        meta_agent.run_cycle(current_input)
        time.sleep(1.5)

    print("\n--- Ternlang Recursive Meta-Reflection Agent Simulation Finished ---")

    meta_agent.memory_manager.save_to_file() # Save memory at end

    print("\n--- Sample of Agent Memory (Structured) ---")
    for entry in meta_agent.memory_manager.get_recent_entries(min(5, len(meta_agent.memory_manager.entries))):
        for key, value in entry.items():
            print(f"  {key}: {value}")
        print("  ---")

    print("\n--- Final Agent State ---")
    print(f"[{meta_agent.name}] Final Mood: {meta_agent.mood}, Cognition: {meta_agent.cognition}, Last Action: {meta_agent._get_state_name(meta_agent.last_action)}")
    print(f"[{meta_agent.name}] Final Clarity: {meta_agent.clarity_score:.2f}, Stale Cycles: {meta_agent.consecutive_stale_cycles}, Is Meta-Reflecting: {meta_agent.is_meta_reflecting}")
