# examples/example_state_recovery.py
# Demonstrates a TernAgent simulating state corruption and attempting recovery
# by reconstructing its last stable state from its persistent memory.
# It either successfully recovers (AFFIRM) or pings a human/supervisor (REFRAIN).

# Assuming ternlang_prototype.py is in the same parent directory
from ternlang_prototype import REFRAIN, TEND, AFFIRM, TernAgent
import random
import time
import datetime
import uuid
# MemoryManager is now automatically imported via TernAgent's super().__init__()

print("--- Ternlang Example: State Recovery Agent ---")

class RecoveryAgent(TernAgent):
    """
    A TernAgent designed to detect and recover from simulated internal state corruption.
    It attempts to reconstruct a stable state by retrieving its own past memory entries.
    """
    def __init__(self, name="RecoveryBot", initial_mood=7):
        super().__init__(name, initial_context="stable") # TernAgent now initializes MemoryManager
        self.mood = initial_mood
        self.cognition = 500
        self.is_corrupted = False # Flag to simulate state corruption
        self.recovery_attempts = 0
        self.max_recovery_attempts = 2 # Max tries to reconstruct from memory
        self.last_stable_state = None # To store a snapshot of a known good state

        print(f"[{self.name}] Initialized. Current state: Mood={self.mood}, Cognition={self.cognition}")
        # Capture initial state as the first "stable" state
        self._capture_current_state_as_stable()

    def _capture_current_state_as_stable(self):
        """Captures the agent's current critical internal state as a 'stable' snapshot."""
        self.last_stable_state = {
            "mood": self.mood,
            "cognition": self.cognition,
            "context": self.context,
            # Add other critical internal states here as needed
        }
        print(f"[{self.name}]   (Recovery) Captured current state as stable.")

    def _corrupt_state(self):
        """Simulates internal state corruption."""
        print(f"[{self.name}] !!! SIMULATING STATE CORRUPTION !!!")
        self.mood = random.randint(1, 3) # Drastically lower mood
        self.cognition = random.randint(100, 300) # Drastically lower cognition
        self.context = "corrupted_state"
        self.is_corrupted = True
        print(f"[{self.name}]   State now: Mood={self.mood}, Cognition={self.cognition}, Context='{self.context}'")

    def _attempt_state_reconstruction(self):
        """
        Attempts to reconstruct a stable state from recent memory.
        This is a simplified RAG-like process, pulling from its own history.
        """
        print(f"[{self.name}]   (Recovery) Attempting state reconstruction (Attempt {self.recovery_attempts + 1}/{self.max_recovery_attempts})...")
        
        # Retrieve recent memory entries
        recent_memories = self.memory_manager.get_recent_entries(5) # Look at last 5 entries
        
        if not recent_memories:
            print(f"[{self.name}]     No recent memory entries to reconstruct from.")
            return False

        # Find the most recent 'stable' or 'coherent' state in memory
        reconstructed_mood = None
        reconstructed_cognition = None
        reconstructed_context = None
        
        for entry in reversed(recent_memories): # Iterate backwards from most recent
            if entry.get("Context") not in ["corrupted_state", "recovery_phase", "highly_fragmented"]:
                # Found a potentially stable past state
                reconstructed_mood = entry.get("Mood Barometer (1–13)")
                reconstructed_cognition = entry.get("Cognition Barometer (0-1000)")
                reconstructed_context = entry.get("Context")
                print(f"[{self.name}]     Found potential stable state in memory (ID: {entry.get('ID')}).")
                break
        
        if reconstructed_mood is not None:
            # Apply reconstructed state
            self.mood = reconstructed_mood
            self.cognition = reconstructed_cognition
            self.context = reconstructed_context
            self.is_corrupted = False # State recovered
            self._capture_current_state_as_stable() # Update last_stable_state
            print(f"[{self.name}]     State successfully reconstructed! New state: Mood={self.mood}, Cognition={self.cognition}, Context='{self.context}'")
            return True
        else:
            print(f"[{self.name}]     Could not find a sufficiently stable state in recent memory.")
            return False


    def observe(self, input_data, other_agent_actions=None):
        """
        Observes input. If corrupted, it prioritizes recovery.
        """
        print(f"[{self.name}] Observing input: '{input_data}'")
        
        current_context = self.context # Start with current context
        relevance_score = 0.5

        if self.is_corrupted:
            current_context = "recovery_phase"
            relevance_score = 0.9 # High relevance for recovery task
            print(f"[{self.name}]   (Recovery) Agent is corrupted. Focusing on self-recovery.")
        elif "unclear input" in input_data.lower() or "fragmented data" in input_data.lower():
            # Simulate a trigger for corruption if input is bad and agent is already stressed
            if random.random() < 0.3 and self.mood < 5: # 30% chance if mood is low
                self._corrupt_state()
                current_context = "corrupted_state_triggered"
                relevance_score = 0.95
            else:
                current_context = "ambiguous_input"
                relevance_score = 0.4
        else:
            current_context = "normal_operation"
            relevance_score = 0.7

        self.context = current_context
        print(f"[{self.name}] Context: '{self.context}', Mood: {self.mood}, Cognition: {self.cognition}")
        return self.context, relevance_score

    def decide(self, relevance_score, other_agent_decision=None):
        """
        Decides the action. Prioritizes recovery if corrupted.
        """
        print(f"[{self.name}] Deciding based on relevance: {relevance_score:.2f}...")
        
        if self.is_corrupted:
            self.recovery_attempts += 1
            if self.recovery_attempts <= self.max_recovery_attempts:
                print(f"[{self.name}]   (Recovery) Deciding to TEND for state reconstruction.")
                decision = TEND # TEND to attempt reconstruction
            else:
                print(f"[{self.name}]   (Recovery) Max recovery attempts reached. Cannot reconstruct.")
                decision = REFRAIN # Cannot recover, must refrain and ping human
                self.context = "recovery_failed_ping_human"
                self.mood = max(1, self.mood - 4) # Significant mood drop
                self.cognition = max(0, self.cognition - 100) # Exhausted cognition
            return decision

        # Normal decision logic (if not corrupted)
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
        Executes the action. Special handling for recovery.
        """
        super().execute_action(action)

        if self.is_corrupted and action == TEND:
            print(f"[{self.name}] ACTION: Attempting internal state reconstruction...")
            if self._attempt_state_reconstruction():
                print(f"[{self.name}]   (Recovery) State successfully restored!")
                self.recovery_attempts = 0 # Reset attempts on success
                self.mood = min(13, self.mood + 3) # Mood boost from recovery
                self.cognition = min(1000, self.cognition + 100) # Cognitive boost
                self.context = "recovered_stable"
            else:
                print(f"[{self.name}]   (Recovery) Reconstruction failed for this attempt.")
        elif self.context == "recovery_failed_ping_human" and action == REFRAIN:
            print(f"[{self.name}] ACTION: REFRAINING. Pinging human/supervisor for intervention due to unrecoverable state.")
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
        Performs a full Ternlang cycle for a RecoveryAgent.
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

            IsCorrupted=self.is_corrupted,
            RecoveryAttempts=self.recovery_attempts,
            LastStableMood=self.last_stable_state.get("mood") if self.last_stable_state else "N/A",
            LastStableCognition=self.last_stable_state.get("cognition") if self.last_stable_state else "N/A",
        )

        print(f"--- [{self.name}] Cycle Complete ---")
        return decision

# --- Simulation ---
def simulate_state_recovery_agent(num_cycles=10):
    """
    Runs a simulation of a RecoveryAgent, demonstrating state corruption and recovery.
    """
    print("\n--- Ternlang State Recovery Agent Simulation Started ---")
    
    recovery_agent = RecoveryAgent(name="ResilientBot", initial_mood=8)
    # MemoryManager is initialized in RecoveryAgent.__init__ and loads automatically

    scenarios = [
        "Input: Routine system check. All seems normal.", # Stable
        "Input: Processing data stream. (Normal operation)", # Stable
        "Input: Unclear input received. Fragmented data detected.", # Could trigger corruption
        "Input: Continuing with task.", # If corrupted, should TEND for recovery
        "Input: System status update.", # If still corrupted, TEND again or REFRAIN
        "Input: External signal: 'All systems go!'", # Could be a new input after recovery
        "Input: Another routine check.", # Stable
        "Input: Fragmented data detected. (Attempting to trigger corruption again)",
        "Input: Processing data stream.",
        "Input: Final check. All good."
    ]

    for i in range(num_cycles):
        print(f"\n===== SIMULATION CYCLE {i+1}/{len(scenarios)} =====")
        current_input = scenarios[i % len(scenarios)] 
        recovery_agent.run_cycle(current_input)
        time.sleep(1.5)

    print("\n--- Ternlang State Recovery Agent Simulation Finished ---")

    # Save memory at the end of simulation via MemoryManager
    recovery_agent.memory_manager.save_to_file() 

    print("\n--- Sample of Agent Memory (Structured) ---")
    for entry in recovery_agent.memory_manager.get_recent_entries(min(5, len(recovery_agent.memory_manager.entries))):
        for key, value in entry.items():
            print(f"  {key}: {value}")
        print("  ---")

    print("\n--- Final Agent State ---")
    print(f"[{recovery_agent.name}] Final Mood: {recovery_agent.mood}, Cognition: {recovery_agent.cognition}, Last Action: {recovery_agent._get_state_name(recovery_agent.last_action)}")
    print(f"[{recovery_agent.name}] Is Corrupted: {recovery_agent.is_corrupted}, Recovery Attempts: {recovery_agent.recovery_attempts}")
