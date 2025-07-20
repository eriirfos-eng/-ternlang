# examples/example_multiagent_consensus.py
# Demonstrates multiple TernAgents receiving partially conflicting inputs,
# initiating negotiation, reporting clarity and confidence, and escalating
# to a third "arbiter" agent if no consensus is reached.

# Assuming ternlang_prototype.py is in the same parent directory
from ternlang_prototype import REFRAIN, TEND, AFFIRM, TernAgent
import random
import time
import datetime
import uuid
# MemoryManager is automatically imported via TernAgent's super().__init__()

print("--- Ternlang Example: Multi-Agent Consensus and Arbitration ---")

class ConsensusAgent(TernAgent):
    """
    A TernAgent designed to participate in a multi-agent consensus process.
    It receives inputs, makes an initial decision, and can engage in negotiation
    with peers, reporting its clarity and confidence.
    """
    def __init__(self, name="ConsensusBot", initial_mood=7):
        super().__init__(name, initial_context="evaluating_input")
        self.mood = initial_mood
        self.cognition = 500
        self.clarity_score = 0.5 # 0.0 (uncertain) to 1.0 (clear)
        self.confidence_delta = 0.0 # How strongly the agent holds its current decision (0.0-1.0)
        self.negotiation_rounds = 0
        self.max_negotiation_rounds = 2 # Max rounds before escalating to arbiter
        self.last_negotiated_decision = None # Stores decision after negotiation attempt

        print(f"[{self.name}] Initialized. Mood={self.mood}, Cognition={self.cognition}")

    def observe(self, input_data, other_agent_actions=None):
        """
        Observes input and calculates initial clarity and confidence.
        """
        print(f"[{self.name}] Observing input: '{input_data}'")
        
        current_context = "neutral_observation"
        
        # Simulate clarity calculation based on keywords
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

        # Confidence delta is higher with higher clarity, and if mood is good
        self.confidence_delta = self.clarity_score * (self.mood / 13.0) 
        
        self.context = current_context
        print(f"[{self.name}] Context: '{self.context}', Clarity: {self.clarity_score:.2f}, Confidence: {self.confidence_delta:.2f}")
        return self.context, self.clarity_score # clarity_score as relevance for decide

    def decide(self, relevance_score, collective_state_for_negotiation=None):
        """
        Decides the action based on clarity. Incorporates negotiation logic.
        """
        print(f"[{self.name}] Deciding based on clarity: {relevance_score:.2f}...")
        
        # Initial decision based on clarity
        if relevance_score >= 0.7:
            decision = AFFIRM
        elif relevance_score < 0.3:
            decision = REFRAIN
        else:
            decision = TEND
        
        print(f"[{self.name}] Initial decision: {self._get_state_name(decision)}")

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

        return decision

    def execute_action(self, action):
        """
        Executes the action.
        """
        super().execute_action(action)

        if action == AFFIRM:
            print(f"[{self.name}] ACTION: Proceeding with consensus or independent action.")
        elif action == TEND:
            print(f"[{self.name}] TENDING: Participating in negotiation or awaiting consensus.")
        elif action == REFRAIN:
            print(f"[{self.name}] REFRAIN: Halting due to disagreement or arbitration.")
        else:
            print(f"[{self.name}] WARNING: Unknown action state received: {action}")

    def run_cycle(self, input_data, collective_state_for_negotiation=None):
        """
        Performs a full Ternlang cycle for a ConsensusAgent.
        """
        print(f"\n--- [{self.name}] Starting New Cycle ---")
        current_context, relevance_score = self.observe(input_data)
        
        # Initial decision before any negotiation
        initial_decision = self.decide(relevance_score)
        self.last_negotiated_decision = initial_decision # Store as initial decision for now

        # No direct execute_action here, as it's part of the consensus loop
        # The actual action will be executed after negotiation/arbitration

        # Add entry to MemoryManager (only initial state for now)
        self.memory_manager.add_entry(
            input_data=input_data,
            context=current_context,
            decision=initial_decision,
            mood=self.mood,
            cognition=self.cognition,
            impact=random.randint(1, 13),
            Summary=f"Initial decision: {self._get_state_name(initial_decision)}.",
            ClarityScore=round(self.clarity_score, 2),
            ConfidenceDelta=round(self.confidence_delta, 2),
            NegotiationRounds=self.negotiation_rounds,
            FinalConsensusDecision="Pending" # Will be updated later
        )

        print(f"--- [{self.name}] Cycle Complete (Initial) ---")
        return initial_decision # Return initial decision for negotiation

class ArbiterAgent(TernAgent):
    """
    A specialized TernAgent that acts as an arbiter to resolve conflicts
    between other agents when they cannot reach consensus.
    It has inherently higher clarity and can issue definitive rulings.
    """
    def __init__(self, name="ArbiterBot", initial_mood=10): # Higher initial mood/confidence
        super().__init__(name, initial_context="arbitrating")
        self.mood = initial_mood
        self.cognition = 900 # High cognition for complex analysis
        self.clarity_score = 0.95 # Assumed high clarity
        print(f"[{self.name}] Initialized. Mood={self.mood}, Cognition={self.cognition}")

    def arbitrate(self, agent_states_in_conflict):
        """
        Receives conflicting agent states and issues a definitive decision.
        
        Args:
            agent_states_in_conflict (list): A list of dictionaries, each containing
                                             'name', 'decision', 'clarity', 'confidence'.
        Returns:
            int: The final Ternlang decision (REFRAIN, TEND, or AFFIRM).
        """
        print(f"\n[{self.name}] --- ARBITRATION INITIATED ---")
        self.observe("arbitration request") # Set context
        self.decide(self.clarity_score) # Decide to TEND for arbitration

        # Analyze conflicting states
        affirm_votes = []
        tend_votes = []
        refrain_votes = []
        
        for state in agent_states_in_conflict:
            if state['decision'] == AFFIRM:
                affirm_votes.append(state)
            elif state['decision'] == TEND:
                tend_votes.append(state)
            elif state['decision'] == REFRAIN:
                refrain_votes.append(state)
            print(f"[{self.name}]   Reviewing {state['name']}: Decision={self._get_state_name(state['decision'])}, Clarity={state['clarity']:.2f}, Confidence={state['confidence']:.2f}")

        # Simple arbitration logic:
        # 1. Prefer majority if clear.
        # 2. If split, lean towards decision from agent with highest confidence/clarity.
        # 3. If still unclear, default to TEND or REFRAIN for safety.
        
        total_agents = len(agent_states_in_conflict)
        
        if len(affirm_votes) > total_agents / 2:
            final_decision = AFFIRM
            print(f"[{self.name}]   Majority AFFIRM. Arbiter rules AFFIRM.")
        elif len(refrain_votes) > total_agents / 2:
            final_decision = REFRAIN
            print(f"[{self.name}]   Majority REFRAIN. Arbiter rules REFRAIN.")
        elif len(tend_votes) > total_agents / 2:
            final_decision = TEND
            print(f"[{self.name}]   Majority TEND. Arbiter rules TEND.")
        else:
            # No clear majority, find highest confidence among conflicting decisions
            all_conflicting = affirm_votes + tend_votes + refrain_votes
            if all_conflicting:
                highest_confidence_agent = max(all_conflicting, key=lambda x: x['confidence'])
                final_decision = highest_confidence_agent['decision']
                print(f"[{self.name}]   No clear majority. Ruling based on highest confidence agent ({highest_confidence_agent['name']}): {self._get_state_name(final_decision)}")
            else:
                final_decision = TEND # Should not happen if agent_states_in_conflict is not empty
                print(f"[{self.name}]   Arbitration inconclusive, defaulting to TEND.")

        self.execute_action(final_decision) # Arbiter executes its decision (as a ruling)
        self.mood = min(13, self.mood + 1) # Mood boost from resolving conflict
        self.cognition = max(0, self.cognition - 50) # Cognitive relief

        # Log arbitration event to arbiter's memory
        self.memory_manager.add_entry(
            input_data="Arbitration request received.",
            context="arbitration_complete",
            decision=final_decision,
            mood=self.mood,
            cognition=self.cognition,
            impact=random.randint(1,13),
            Summary=f"Arbitrated conflict. Ruled: {self._get_state_name(final_decision)}.",
            ConflictingAgents=[s['name'] for s in agent_states_in_conflict],
            ArbitrationOutcome=self._get_state_name(final_decision)
        )
        print(f"[{self.name}] Arbitration complete. Final Ruling: {self._get_state_name(final_decision)}")
        return final_decision

# --- Simulation ---
def simulate_multiagent_consensus(num_cycles=5, num_consensus_agents=3):
    """
    Runs a simulation of a multi-agent consensus process with an arbiter.
    """
    print("\n--- Ternlang Multi-Agent Consensus Simulation Started ---")
    
    consensus_agents = [ConsensusAgent(name=f"Agent-{i+1}", initial_mood=random.randint(5,9)) for i in range(num_consensus_agents)]
    arbiter_agent = ArbiterAgent(name="CentralArbiter")

    # Load memory for all agents at the start
    for agent in consensus_agents + [arbiter_agent]:
        agent.memory_manager.load_from_file()

    # Example inputs: some clear, some conflicting
    scenarios = [
        {"input": "Clear directive: Proceed with phase 2.", "conflicts": []}, # Expected: AFFIRM
        {"input": "Vague data on resource allocation. Some say proceed, others wait.", "conflicts": [("Agent-1", AFFIRM), ("Agent-2", REFRAIN)]}, # Expected: Conflict, then arbitration
        {"input": "Urgent alert: System anomaly detected. Needs immediate attention.", "conflicts": [("Agent-1", AFFIRM), ("Agent-2", AFFIRM), ("Agent-3", TEND)]}, # Expected: Majority AFFIRM, one TEND
        {"input": "Conflicting reports on security breach. One says halt, other says investigate.", "conflicts": [("Agent-1", REFRAIN), ("Agent-2", TEND), ("Agent-3", AFFIRM)]}, # Expected: Conflict, then arbitration
        {"input": "Routine check. All systems nominal.", "conflicts": []}, # Expected: AFFIRM
    ]

    for i, scenario in enumerate(scenarios):
        print(f"\n===== SIMULATION CYCLE {i+1}/{len(scenarios)} =====")
        current_input = scenario["input"]
        
        # Step 1: Each agent makes an initial decision based on its input
        initial_decisions = []
        for agent in consensus_agents:
            initial_decision = agent.run_cycle(current_input) # This logs initial decision
            initial_decisions.append({
                'name': agent.name,
                'decision': initial_decision,
                'clarity': agent.clarity_score,
                'confidence': agent.confidence_delta
            })
            time.sleep(0.3)

        print("\n--- Initial Agent Decisions ---")
        for state in initial_decisions:
            print(f"  {state['name']}: {arbiter_agent._get_state_name(state['decision'])}, Clarity={state['clarity']:.2f}, Confidence={state['confidence']:.2f}")

        # Step 2: Check for consensus among initial decisions
        # Count votes for each decision
        decision_counts = {AFFIRM: 0, TEND: 0, REFRAIN: 0}
        for state in initial_decisions:
            decision_counts[state['decision']] += 1
        
        total_agents = len(consensus_agents)
        consensus_achieved = False
        final_group_decision = None

        if decision_counts[AFFIRM] == total_agents:
            final_group_decision = AFFIRM
            consensus_achieved = True
            print("\n--- Consensus Achieved: All AFFIRM ---")
        elif decision_counts[REFRAIN] == total_agents:
            final_group_decision = REFRAIN
            consensus_achieved = True
            print("\n--- Consensus Achieved: All REFRAIN ---")
        elif decision_counts[TEND] == total_agents:
            final_group_decision = TEND
            consensus_achieved = True
            print("\n--- Consensus Achieved: All TEND ---")
        else:
            # Check for majority consensus (e.g., > 60%)
            for decision_val, count in decision_counts.items():
                if count / total_agents > 0.6: # Simple majority threshold
                    final_group_decision = decision_val
                    consensus_achieved = True
                    print(f"\n--- Majority Consensus Achieved: {arbiter_agent._get_state_name(final_group_decision)} ---")
                    break

        # Step 3: If no consensus, initiate arbitration
        if not consensus_achieved:
            print("\n--- No Consensus. Initiating Arbitration ---")
            final_group_decision = arbiter_agent.arbitrate(initial_decisions)
            print(f"\n--- Arbitration Result: {arbiter_agent._get_state_name(final_group_decision)} ---")
        
        # Step 4: All consensus agents execute the final group decision and update their memory
        print("\n--- Agents Executing Final Group Decision ---")
        for agent in consensus_agents:
            agent.execute_action(final_group_decision)
            # Update the last memory entry with the final consensus decision
            if agent.memory_manager.entries:
                agent.memory_manager.entries[-1]["FinalConsensusDecision"] = arbiter_agent._get_state_name(final_group_decision)
            time.sleep(0.3)


    print("\n--- Ternlang Multi-Agent Consensus Simulation Finished ---")

    # Save memory for all agents at the end of simulation
    for agent in consensus_agents + [arbiter_agent]:
        agent.memory_manager.save_to_file()

    # Optional: Print memory of each agent at the end
    print("\n--- Agent Memory Snapshots ---")
    for agent in consensus_agents + [arbiter_agent]:
        print(f"\n[{agent.name}] Memory (last 3 entries):")
        for entry in agent.memory_manager.get_recent_entries(3):
            print(f"  - ID: {entry.get('ID', 'N/A')} | Decision: {entry.get('Decision', 'N/A')} | Final Consensus: {entry.get('FinalConsensusDecision', 'N/A')} | Summary: {entry.get('Summary', 'N/A')}")
