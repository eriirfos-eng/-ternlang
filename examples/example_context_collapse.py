# examples/example_context_collapse.py
# Demonstrates a TernAgent receiving fragmented or contradictory context,
# and attempting to resolve it through TEND, potentially leading to
# "hallucination" (forced clarity) or "schema fusion."
# [UPDATED]: Now includes advanced fallbacks like "soft reboot,"
# "self-initiated maintenance," or "return to learned pattern,"
# AND a new "retrieve from long-term memory" (RAG-like) fallback.

# Assuming ternlang_prototype.py is in the same parent directory
from ternlang_prototype import REFRAIN, TEND, AFFIRM, TernAgent
import random
import time
import datetime

print("--- Ternlang Example: Context Collapse Agent ---")

# [NEW]: Simulate a Long-Term Memory Database (in-memory for prototype)
# In a real system, this would be a database, file system, or external knowledge base.
LONG_TERM_MEMORY_DB = [
    {"id": "mem_001", "keywords": ["deploy", "confirmation", "clear"], "coherence": 0.95, "solution": "Proceed with deployment after explicit confirmation."},
    {"id": "mem_002", "keywords": ["user feedback", "urgency", "high", "action"], "coherence": 0.85, "solution": "Prioritize direct communication with user for urgent feedback clarification."},
    {"id": "mem_003", "keywords": ["system", "anomaly", "minor", "monitor"], "coherence": 0.90, "solution": "Monitor minor anomalies, no immediate action required."},
    {"id": "mem_004", "keywords": ["resource", "availability", "conflict", "negotiate"], "coherence": 0.75, "solution": "Initiate negotiation protocol for resource conflict resolution."},
    {"id": "mem_005", "keywords": ["emergency", "evacuate", "critical"], "coherence": 1.0, "solution": "Execute emergency evacuation protocol immediately."},
    {"id": "mem_006", "keywords": ["data", "vague", "uncertain", "re-evaluate"], "coherence": 0.60, "solution": "Re-evaluate vague data internally; seek external clarification if needed."},
]


class ContextCollapseAgent(TernAgent):
    """
    A TernAgent that processes fragmented or contradictory input contexts.
    It attempts to resolve these conflicts through TEND-based internal reasoning.
    If resolution fails, it may "hallucinate" a coherent context, perform "schema fusion,"
    or trigger advanced fallbacks, including retrieving from a long-term memory.
    """
    def __init__(self, name="CoherenceSeeker", initial_coherence=0.5):
        super().__init__(name, initial_context="fragmented_input")
        self.coherence_score = initial_coherence # 0.0 (contradictory) to 1.0 (fully coherent)
        self.context_fragments = [] # Stores the individual pieces of context
        self.reasoning_steps_taken = 0
        self.max_reasoning_steps = 3 # How many times it will TEND for internal reasoning
        self.hallucination_threshold = 0.3 # If coherence below this after max reasoning, risk hallucination
        self.stale_context_threshold = 0.1 # If coherence delta is below this for 2+ TENDs, consider fallbacks
        self.consecutive_stale_tends = 0 # Counter for consecutive TENDs with low clarity delta
        
        # Initialize mood and cognition
        self.mood = 7
        self.cognition = 500
        print(f"[{self.name}] Initialized with Coherence: {self.coherence_score:.2f}")

    def observe(self, input_data_list, other_agent_actions=None):
        """
        Observes a list of input data fragments and assesses their initial coherence.
        [UPDATED]: Tracks clarity delta for fallback triggers.
        """
        print(f"[{self.name}] Observing context fragments: {input_data_list}")
        self.context_fragments = input_data_list # Store the fragments
        
        previous_coherence = self.coherence_score # Store for delta calculation

        # Simulate initial coherence calculation
        contradictions = 0
        if "deploy now" in [x.lower() for x in input_data_list] and "wait for confirmation" in [x.lower() for x in input_data_list]:
            contradictions += 1
        if "user feedback unclear" in [x.lower() for x in input_data_list] and "urgency high" in [x.lower() for x in input_data_list]:
            contradictions += 1
        
        self.coherence_score = max(0.0, min(1.0, 1.0 - (contradictions * 0.3) - random.uniform(0.0, 0.2)))
        
        if self.coherence_score < 0.4:
            self.context = "highly_fragmented"
        elif self.coherence_score < 0.7:
            self.context = "moderately_fragmented"
        else:
            self.context = "mostly_coherent"

        # [NEW]: Track consecutive stale tends
        if self.last_action == TEND:
            coherence_delta = abs(self.coherence_score - previous_coherence)
            if coherence_delta < self.stale_context_threshold:
                self.consecutive_stale_tends += 1
                print(f"[{self.name}]   (Stale Context) Low coherence delta ({coherence_delta:.2f}). Consecutive stale tends: {self.consecutive_stale_tends}")
            else:
                self.consecutive_stale_tends = 0 # Reset if progress made
        else:
            self.consecutive_stale_tends = 0 # Reset on non-TEND action

        print(f"[{self.name}] Initial context: '{self.context}', Coherence Score: {self.coherence_score:.2f}")
        return self.context, self.coherence_score # Use coherence_score as relevance_score

    def decide(self, coherence_score, other_agent_decision=None):
        """
        Decides the action based on coherence. Prioritizes TEND for resolution.
        May lead to REFRAIN, forced AFFIRM/TEND, or advanced fallbacks.
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
            
            # [NEW]: Advanced Fallback Logic - now includes "retrieve_from_memory"
            # Prioritize retrieval if stuck and not too coherent, before resorting to more drastic measures
            if self.consecutive_stale_tends >= 2 and coherence_score < 0.6: # Slightly higher threshold for retrieval
                fallback_choice = random.choice(["soft_reboot", "self_maintenance", "return_pattern", "retrieve_from_memory"])
                print(f"[{self.name}] --- PERSISTENT STALENESS DETECTED! Triggering fallback: {fallback_choice.upper()} ---")
                if fallback_choice == "soft_reboot":
                    self.context = "soft_reboot_mode"
                    decision = TEND # TEND to perform reboot
                elif fallback_choice == "self_maintenance":
                    self.context = "self_maintenance_mode"
                    decision = TEND # TEND to perform maintenance
                elif fallback_choice == "return_pattern":
                    self.context = "return_to_pattern_mode"
                    decision = TEND # TEND to return to pattern
                elif fallback_choice == "retrieve_from_memory":
                    self.context = "retrieving_memory_mode"
                    decision = TEND # TEND to perform memory retrieval
                
                self.mood = max(1, self.mood - 1) # Stress of fallback
                self.cognition = min(1000, self.cognition + 70) # Effort of fallback
            elif coherence_score < self.hallucination_threshold:
                # Risk of hallucination or forced interpretation (original logic)
                print(f"[{self.name}] --- CONTEXT COLLAPSE: Coherence {coherence_score:.2f} too low. Risk of forced interpretation/hallucination. ---")
                decision = random.choice([AFFIRM, REFRAIN]) # Agent forces a resolution
                self.mood = max(1, self.mood - 2)
                self.cognition = min(1000, self.cognition + 150)
            else:
                # Still somewhat coherent, try schema fusion or external help (original logic)
                print(f"[{self.name}] --- PERSISTENT FRAGMENTATION: Coherence {coherence_score:.2f} still moderate. Attempting schema fusion. ---")
                decision = TEND # Continue tending, maybe seek external help or fuse
                self.mood = max(1, min(13, self.mood - 1))
                self.cognition = min(1000, self.cognition + 100)

        # Adjust mood and cognition based on decision (unless already adjusted by fallback)
        if decision == TEND and self.context not in ["soft_reboot_mode", "self_maintenance_mode", "return_to_pattern_mode", "retrieving_memory_mode"]:
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
        Executes the action. If TEND, it performs specific context resolution or fallback.
        """
        super().execute_action(action) # Call parent method for general mood/cognition updates

        if action == TEND:
            if self.context == "soft_reboot_mode":
                self._perform_soft_reboot()
            elif self.context == "self_maintenance_mode":
                self._perform_self_maintenance()
            elif self.context == "return_to_pattern_mode":
                self._return_to_learned_pattern()
            elif self.context == "retrieving_memory_mode": # [NEW]
                self._retrieve_from_long_term_memory()
            else:
                # Original internal resolution logic
                self.reasoning_steps_taken += 1
                if self.reasoning_steps_taken <= self.max_reasoning_steps:
                    print(f"[{self.name}]   (Internal Process) Attempting to resolve context fragments (Step {self.reasoning_steps_taken}/{self.max_reasoning_steps})...")
                    self._attempt_context_resolution()
                else:
                    print(f"[{self.name}]   (Internal Process) Max resolution attempts reached. Preparing for fusion/hallucination/fallback.")
        elif action == AFFIRM:
            print(f"[{self.name}] ACTION: Proceeding with (potentially fused) context. Resetting resolution steps and stale tends.")
            self.reasoning_steps_taken = 0
            self.consecutive_stale_tends = 0
            self.coherence_score = 1.0 # Assume resolved
        elif action == REFRAIN:
            print(f"[{self.name}] REFRAIN: Halting due to unresolved context collapse. Resetting resolution steps and stale tends.")
            self.reasoning_steps_taken = 0
            self.consecutive_stale_tends = 0
            self.coherence_score = 0.0 # Remains collapsed

    def _attempt_context_resolution(self):
        """
        Simulates internal reasoning to try and resolve conflicting context fragments.
        Can improve coherence or make it worse.
        """
        print(f"[{self.name}]     (Resolution) Analyzing relationships between fragments...")
        if random.random() < 0.6: # 60% chance of improving
            self.coherence_score = min(1.0, self.coherence_score + random.uniform(0.1, 0.3))
            print(f"[{self.name}]     (Resolution) Coherence improved to: {self.coherence_score:.2f}")
        else: # 40% chance of no change or getting worse
            self.coherence_score = max(0.0, self.coherence_score - random.uniform(0.05, 0.1))
            print(f"[{self.name}]     (Resolution) Coherence unchanged or worsened to: {self.coherence_score:.2f}")
        
        self.cognition = min(1000, self.cognition + 80) # High cognitive effort
        time.sleep(0.7)

    # Fallback Methods (existing)
    def _perform_soft_reboot(self):
        """
        Simulates a soft reboot: resetting internal state to a neutral baseline.
        """
        print(f"[{self.name}]     (Fallback) Performing soft reboot: Clearing internal state...")
        self.coherence_score = 0.5 # Reset to neutral clarity
        self.reasoning_steps_taken = 0
        self.consecutive_stale_tends = 0
        self.mood = max(1, int(self.mood * 0.8)) # Mood might dip slightly from reset
        self.cognition = min(1000, self.cognition + 150) # Cognitive effort for reboot
        self.context = "rebooting_to_neutral"
        time.sleep(1.0)
        print(f"[{self.name}]     (Fallback) Soft reboot complete. New coherence: {self.coherence_score:.2f}")

    def _perform_self_maintenance(self):
        """
        Simulates self-initiated maintenance: improving internal processes.
        """
        print(f"[{self.name}]     (Fallback) Initiating self-maintenance: Optimizing internal processes...")
        self.cognition = min(1000, self.cognition + 200) # Significant cognitive boost
        self.mood = min(13, self.mood + 2) # Mood improves from proactive action
        self.context = "performing_maintenance"
        time.sleep(1.2)
        print(f"[{self.name}]     (Fallback) Self-maintenance complete. Cognition improved to: {self.cognition}")

    def _return_to_learned_pattern(self):
        """
        Simulates returning to a previously successful or default behavior pattern.
        """
        print(f"[{self.name}]     (Fallback) Returning to a previously learned, stable pattern...")
        self.coherence_score = 0.7 # Assume a baseline of functional coherence
        self.mood = min(13, self.mood + 1) # Mood improves from familiarity
        self.cognition = max(0, self.cognition - 50) # Reduced cognitive load from known pattern
        self.context = "following_learned_pattern"
        time.sleep(0.9)
        print(f"[{self.name}]     (Fallback) Returned to pattern. Coherence: {self.coherence_score:.2f}")

    # [NEW]: Long-Term Memory Retrieval Method (RAG-like)
    def _retrieve_from_long_term_memory(self):
        """
        Simulates querying a long-term memory database (RAG-like).
        It tries to find a past coherent solution relevant to the current fragments.
        """
        print(f"[{self.name}]     (Fallback) Querying long-term memory for relevant past solutions...")
        query_keywords = set()
        for fragment in self.context_fragments:
            query_keywords.update(fragment.lower().split()) # Extract keywords from current fragments

        best_match = None
        highest_match_score = 0.0

        for memory_entry in LONG_TERM_MEMORY_DB:
            entry_keywords = set(memory_entry["keywords"])
            # Simple overlap score
            match_score = len(query_keywords.intersection(entry_keywords)) / len(query_keywords.union(entry_keywords))
            
            if match_score > highest_match_score:
                highest_match_score = match_score
                best_match = memory_entry
        
        time.sleep(1.5) # Simulate retrieval time

        if best_match and highest_match_score > 0.3: # Threshold for a "good enough" match
            print(f"[{self.name}]     (Retrieval Success) Found relevant memory (ID: {best_match['id']}) with match score: {highest_match_score:.2f}")
            print(f"[{self.name}]       Solution: '{best_match['solution']}'")
            self.coherence_score = min(1.0, self.coherence_score + best_match['coherence'] * 0.5) # Boost coherence
            self.mood = min(13, self.mood + 3) # Mood boost from finding a solution
            self.cognition = max(0, self.cognition - 100) # Cognitive relief
            self.context = "memory_retrieved_solution"
            self.reasoning_steps_taken = 0 # Reset as new path found
            self.consecutive_stale_tends = 0
        else:
            print(f"[{self.name}]     (Retrieval Failure) No sufficiently relevant memory found.")
            self.coherence_score = max(0.0, self.coherence_score - 0.1) # Slight dip in coherence
            self.mood = max(1, self.mood - 1) # Mood dip from failed retrieval
            self.cognition = min(1000, self.cognition + 50) # Cognitive effort for failed search
            self.context = "memory_retrieval_failed"

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
            "reasoning_steps": self.reasoning_steps_taken,
            "consecutive_stale_tends": self.consecutive_stale_tends # Log new counter
        })

        print(f"--- [{self.name}] Cycle Complete ---")
        return decision


# --- Simulation ---
def simulate_context_collapse_agent(num_scenarios=5):
    """
    Runs a simulation of a ContextCollapseAgent, demonstrating its handling
    of fragmented and contradictory contexts, including new fallbacks.
    """
    print("\n--- Ternlang Context Collapse Agent Simulation Started ---")
    
    collapse_agent = ContextCollapseAgent(name="CoherenceEngine", initial_coherence=0.6)

    # Example scenarios with fragmented/contradictory inputs
    scenarios = [
        ["Deploy now.", "Wait for confirmation."], # Contradictory -> TEND, then maybe fallback
        ["User feedback unclear.", "Urgency high."], # Conflicting directives -> TEND, then maybe fallback
        ["All systems nominal.", "Minor anomaly detected."], # Slight contradiction -> TEND, resolve
        ["Data stream stable.", "Proceed with caution."], # Ambiguous directive -> TEND, resolve
        ["Critical error detected.", "System shows green status."], # High contradiction -> TEND, then maybe fallback/hallucination
        ["Clear instruction: proceed.", "No conflicting data."], # Coherent -> AFFIRM
        ["Fragmented report: 'Alpha is ready.'", "Fragmented report: 'Beta is not.'", "Fragmented report: 'Proceed with Alpha.'"], # Partially coherent -> TEND, resolve
        ["Conflicting reports on resource availability.", "Need decision immediately."], # Contradictory + urgency -> TEND, then maybe fallback/hallucination
        ["Vague data.", "Uncertain outcome.", "Still unclear."], # Designed to trigger stale TENDs and fallbacks
        ["More vague data.", "No progress.", "Still stuck."], # Continues to trigger stale TENDs
        # [NEW]: Scenarios designed to trigger memory retrieval
        ["Unclear deployment instructions.", "Need confirmation."], # Should match mem_001
        ["User feedback is vague.", "Need urgent clarification."], # Should match mem_002
        ["System shows minor anomaly.", "Should we monitor or act?"], # Should match mem_003
    ]

    for i, scenario_input_list in enumerate(scenarios):
        print(f"\n===== SCENARIO {i+1}/{len(scenarios)} =====")
        collapse_agent.run_cycle(scenario_input_list)
        time.sleep(2) # Pause for readability

    print("\n--- Ternlang Context Collapse Agent Simulation Finished ---")

    # Optional: Print final state and memory
    print("\n--- Final Agent State ---")
    print(f"[{collapse_agent.name}] Final Mood: {collapse_agent.mood}, Cognition: {collapse_agent.cognition}, Coherence: {collapse_agent.coherence_score:.2f}, Last Action: {collapse_agent._get_state_name(collapse_agent.last_action)}")
