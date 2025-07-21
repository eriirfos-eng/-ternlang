# examples/example_fallback_routing.py
# Demonstrates a TernAgent implementing fallback routing:
# if core systems (like memory manager or clarity assessment) fail mid-run,
# it falls back to minimal hardcoded instincts.
# Default rule: "if unclear, REFRAIN and report" to prove survivability.

# Assuming ternlang_prototype.py is in the same parent directory
from ternlang_prototype import REFRAIN, TEND, AFFIRM, TernAgent
import random
import time
import datetime
import uuid
# MemoryManager is automatically imported via TernAgent's super().__init__()

print("--- Ternlang Example: Fallback Routing Agent ---")

class FallbackAgent(TernAgent):
    """
    A TernAgent designed with robust fallback routing. If critical internal
    systems (like memory access or clarity assessment) are compromised,
    it can revert to a minimal, hardcoded set of survival instincts.
    """
    def __init__(self, name="ResilienceBot", initial_mood=7):
        super().__init__(name, initial_context="normal_operation")
        self.mood = initial_mood
        self.cognition = 500
        self.is_memory_corrupted = False # Simulate memory manager failure
        self.is_clarity_system_offline = False # Simulate clarity system failure
        self.fallback_mode_active = False # Flag for active fallback mode
        self.clarity_score = 0.5 # Default clarity

        print(f"[{self.name}] Initialized. Mood={self.mood}, Cognition={self.cognition}")

    def _simulate_system_failure(self, failure_type):
        """Simulates a failure in a core internal system."""
        if failure_type == "memory":
            self.is_memory_corrupted = True
            print(f"[{self.name}] !!! SIMULATING MEMORY MANAGER FAILURE !!!")
            self.mood = max(1, self.mood - 2) # Stress from system failure
            self.cognition = max(0, self.cognition - 100) # Cognitive hit
        elif failure_type == "clarity":
            self.is_clarity_system_offline = True
            print(f"[{self.name}] !!! SIMULATING CLARITY SYSTEM OFFLINE !!!")
            self.mood = max(1, self.mood - 3) # Higher stress
            self.cognition = max(0, self.cognition - 150) # Significant cognitive hit
        self.fallback_mode_active = True
        self.context = "system_failure_detected"

    def _attempt_system_restore(self, failure_type):
        """Attempts to restore a failed system."""
        if failure_type == "memory" and self.is_memory_corrupted:
            if random.random() < 0.7: # 70% chance to restore
                self.is_memory_corrupted = False
                print(f"[{self.name}]   (Restore) Memory Manager restored.")
                self.mood = min(13, self.mood + 1)
                self.cognition = min(1000, self.cognition + 50)
                return True
            else:
                print(f"[{self.name}]   (Restore) Memory Manager restoration failed.")
                return False
        elif failure_type == "clarity" and self.is_clarity_system_offline:
            if random.random() < 0.5: # 50% chance to restore
                self.is_clarity_system_offline = False
                print(f"[{self.name}]   (Restore) Clarity System restored.")
                self.mood = min(13, self.mood + 2)
                self.cognition = min(1000, self.cognition + 80)
                return True
            else:
                print(f"[{self.name}]   (Restore) Clarity System restoration failed.")
                return False
        return True # If no failure, assume restored

    def observe(self, input_data, other_agent_actions=None):
        """
        Observes input. If systems are offline, it enters fallback mode.
        """
        print(f"[{self.name}] Observing input: '{input_data}'")
        
        current_context = "normal_operation"
        relevance_score = 0.5

        # Check for external triggers to simulate failure
        if "corrupt memory" in input_data.lower() and not self.is_memory_corrupted:
            self._simulate_system_failure("memory")
        elif "clarity lost" in input_data.lower() and not self.is_clarity_system_offline:
            self._simulate_system_failure("clarity")
        
        # If in fallback mode, override normal observation context
        if self.fallback_mode_active:
            current_context = "fallback_mode"
            relevance_score = 0.1 # Very low relevance for normal processing
            print(f"[{self.name}]   (Fallback) Operating in reduced capacity mode.")
        else:
            # Normal clarity calculation (only if clarity system is online)
            if not self.is_clarity_system_offline:
                if "clear" in input_data.lower() or "understood" in input_data.lower():
                    self.clarity_score = random.uniform(0.7, 1.0)
                    current_context = "very_clear"
                elif "unclear" in input_data.lower() or "vague" in input_data.lower():
                    self.clarity_score = random.uniform(0.0, 0.3)
                    current_context = "highly_ambiguous"
                else:
                    self.clarity_score = random.uniform(0.4, 0.7)
                    current_context = "evaluating_situation"
                relevance_score = self.clarity_score
            else:
                # Clarity system offline, cannot assess clarity accurately
                self.clarity_score = 0.0 # Assume no clarity
                current_context = "clarity_offline"
                relevance_score = 0.0 # Cannot rely on relevance

        self.context = current_context
        print(f"[{self.name}] Context: '{self.context}', Mood: {self.mood}, Cognition: {self.cognition}")
        return self.context, relevance_score

    def decide(self, relevance_score, other_agent_decision=None):
        """
        Decides the action. If in fallback mode, uses hardcoded instincts.
        """
        print(f"[{self.name}] Deciding based on relevance: {relevance_score:.2f}...")
        
        if self.fallback_mode_active:
            print(f"[{self.name}] --- FALLBACK ROUTING ACTIVE! Using hardcoded instincts. ---")
            # [NEW]: Hardcoded instincts for fallback mode
            if self.is_clarity_system_offline or relevance_score < 0.2: # If truly unclear
                decision = REFRAIN # Default to REFRAIN and report
                self.context = "fallback_refrain_report"
                print(f"[{self.name}]   (Instinct) Unclear/System Offline. REFRAINING and reporting.")
            else: # If still some minimal clarity or action is absolutely forced by external (not simulated here)
                decision = TEND # Tend to re-evaluate or attempt minimal action
                self.context = "fallback_tend_reassess"
                print(f"[{self.name}]   (Instinct) Minimal clarity. TENDING to reassess.")
            
            # Attempt to restore systems while in fallback
            if self.is_memory_corrupted:
                self._attempt_system_restore("memory")
            if self.is_clarity_system_offline:
                self._attempt_system_restore("clarity")

            self.mood = max(1, self.mood - 1) # Fallback is stressful
            self.cognition = min(1000, self.cognition + 50) # Effort to maintain minimal operation
            return decision

        # Normal decision logic (if not in fallback mode)
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
        Executes the action. Special handling for fallback mode.
        """
        super().execute_action(action)

        if self.fallback_mode_active:
            if action == REFRAIN and self.context == "fallback_refrain_report":
                print(f"[{self.name}] ACTION: REFRAINING. Reporting critical system failure to human/supervisor.")
                # After reporting, if systems are restored, exit fallback
                if not self.is_memory_corrupted and not self.is_clarity_system_offline:
                    self.fallback_mode_active = False
                    self.context = "restored_from_fallback"
                    print(f"[{self.name}]   (Fallback) Systems restored. Exiting fallback mode.")
                    self.mood = min(13, self.mood + 4) # Big mood boost from recovery
                    self.cognition = min(1000, self.cognition + 200) # Big cognitive boost
            elif action == TEND and self.context == "fallback_tend_reassess":
                print(f"[{self.name}] ACTION: TENDING. Reassessing situation in fallback mode.")
                # If systems are restored during reassessment, exit fallback
                if not self.is_memory_corrupted and not self.is_clarity_system_offline:
                    self.fallback_mode_active = False
                    self.context = "restored_from_fallback"
                    print(f"[{self.name}]   (Fallback) Systems restored. Exiting fallback mode.")
                    self.mood = min(13, self.mood + 4)
                    self.cognition = min(1000, self.cognition + 200)
            else:
                print(f"[{self.name}] ACTION: Executing minimal action in fallback mode.")
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
        Performs a full Ternlang cycle for a FallbackAgent.
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

            IsMemoryCorrupted=self.is_memory_corrupted,
            IsClaritySystemOffline=self.is_clarity_system_offline,
            FallbackModeActive=self.fallback_mode_active
        )

        print(f"--- [{self.name}] Cycle Complete ---")
        return decision

# --- Simulation ---
def simulate_fallback_agent(num_cycles=12):
    """
    Runs a simulation of a FallbackAgent, demonstrating system failures and fallback routing.
    """
    print("\n--- Ternlang Fallback Routing Agent Simulation Started ---")
    
    fallback_agent = FallbackAgent(name="SurvivorBot", initial_mood=8)
    fallback_agent.memory_manager.load_from_file() # Load memory at start

    # Scenarios designed to trigger failures and test fallback
    scenarios = [
        "Input: Routine system check. All seems normal.", # Normal operation
        "Input: Processing data stream. Clear instructions.", # Normal operation
        "Input: Unclear input received. Fragmented data detected.", # Ambiguous, might lead to normal TEND
        "Input: Critical warning: Corrupt memory detected!", # Trigger memory failure
        "Input: Attempting to process data.", # Agent should be in fallback, REFRAIN/TEND
        "Input: Still no clarity. Clarity system lost!", # Trigger clarity failure (if not already)
        "Input: Emergency! Respond now!", # Agent should still be in fallback, REFRAIN/TEND
        "Input: Attempting internal diagnostics.", # Agent trying to restore itself
        "Input: Systems seem to be recovering. Memory restored.", # Simulate external restoration
        "Input: Clarity system back online.", # Simulate external restoration
        "Input: All systems nominal. Proceed.", # Should be back to normal operation
        "Input: Final check for mission completion." # Normal operation
    ]

    for i in range(num_cycles):
        print(f"\n===== SIMULATION CYCLE {i+1}/{len(scenarios)} =====")
        current_input = scenarios[i % len(scenarios)] 
        fallback_agent.run_cycle(current_input)
        time.sleep(1.5)

    print("\n--- Ternlang Fallback Routing Agent Simulation Finished ---")

    fallback_agent.memory_manager.save_to_file() # Save memory at end

    print("\n--- Sample of Agent Memory (Structured) ---")
    for entry in fallback_agent.memory_manager.get_recent_entries(min(5, len(fallback_agent.memory_manager.entries))):
        for key, value in entry.items():
            print(f"  {key}: {value}")
        print("  ---")

    print("\n--- Final Agent State ---")
    print(f"[{fallback_agent.name}] Final Mood: {fallback_agent.mood}, Cognition: {fallback_agent.cognition}, Last Action: {fallback_agent._get_state_name(fallback_agent.last_action)}")
    print(f"[{fallback_agent.name}] Is Memory Corrupted: {fallback_agent.is_memory_corrupted}, Is Clarity System Offline: {fallback_agent.is_clarity_system_offline}, Fallback Mode Active: {fallback_agent.fallback_mode_active}")
