# examples/example_conflict_resolution.py
# Demonstrates two TernAgents with opposing decisions (AFFIRM vs. REFRAIN)
# engaging in a negotiation process to resolve conflict and reach a unified action.

# Assuming ternlang_prototype.py is in the same parent directory
from ternlang_prototype import REFRAIN, TEND, AFFIRM, TernAgent
import random
import time
import datetime

print("--- Ternlang Example: Conflict Resolution Agent Negotiation ---")

class ConflictAgent(TernAgent):
    """
    A TernAgent designed to engage in conflict resolution.
    It has an inherent 'bias' and will attempt to negotiate with another
    agent if their initial decisions conflict.
    """
    def __init__(self, name="Negotiator", initial_clarity=0.5, bias_towards=TEND):
        super().__init__(name, initial_context="evaluating_proposal")
        self.clarity_score = initial_clarity
        self.bias_towards = bias_towards # TEND, AFFIRM, or REFRAIN
        self.negotiation_attempts = 0 # Track how many times it tried to negotiate
        self.max_negotiation_attempts = 2 # Limit for internal negotiation cycles
        
        # Initialize mood and cognition
        self.mood = random.randint(5, 9) # Start with varied moods
        self.cognition = random.randint(400, 600)
        print(f"[{self.name}] Initialized with Clarity: {self.clarity_score:.2f}, Bias: {self._get_state_name(self.bias_towards)}, Mood: {self.mood}, Cognition: {self.cognition}")

    def observe(self, input_data, other_agent_actions=None):
        """
        Observes input and calculates clarity.
        """
        print(f"[{self.name}] Observing proposal: '{input_data}'")
        
        current_context = "neutral_observation"
        # Simulate clarity calculation
        if "unclear" in input_data.lower() or "vague" in input_data.lower():
            self.clarity_score = random.uniform(0.0, 0.3)
            current_context = "highly_ambiguous"
        elif "partially clear" in input_data.lower() or "some context missing" in input_data.lower():
            self.clarity_score = random.uniform(0.3, 0.6)
            current_context = "moderately_clear"
        elif "very clear" in input_data.lower() or "explicit" in input_data.lower():
            self.clarity_score = random.uniform(0.7, 1.0)
            current_context = "very_clear"
        else:
            self.clarity_score = random.uniform(0.4, 0.7)
            current_context = "evaluating_situation"

        self.context = current_context
        print(f"[{self.name}] Context: '{self.context}', Clarity: {self.clarity_score:.2f}")
        return self.context, self.clarity_score

    def decide(self, clarity_score, other_agent_decision=None):
        """
        Decides the action, incorporating its bias and potentially
        reacting to another agent's decision during negotiation.
        """
        print(f"[{self.name}] Deciding based on clarity: {clarity_score:.2f}...")
        
        # Initial decision based on clarity and bias
        if clarity_score >= 0.7:
            decision = AFFIRM
        elif clarity_score < 0.3:
            decision = REFRAIN
        else:
            decision = TEND
        
        # Apply bias, especially if the initial decision is TEND
        if decision == TEND:
            if self.bias_towards == AFFIRM:
                if random.random() < 0.7: # 70% chance to lean towards bias
                    decision = AFFIRM
            elif self.bias_towards == REFRAIN:
                if random.random() < 0.7: # 70% chance to lean towards bias
                    decision = REFRAIN
        
        print(f"[{self.name}] Initial decision: {self._get_state_name(decision)}")
        return decision

    def negotiate(self, other_agent, current_input):
        """
        [NEW]: Simulates a negotiation process between two agents with conflicting decisions.
        The agent with higher 'persuasion power' (e.g., clarity + mood) might sway the other.
        """
        print(f"[{self.name}] Initiating negotiation with {other_agent.name}...")
        self.negotiation_attempts = 0
        
        while self.negotiation_attempts < self.max_negotiation_attempts:
            self.negotiation_attempts += 1
            print(f"[{self.name}]   (Negotiation Attempt {self.negotiation_attempts})")

            # Both agents re-evaluate based on current input and each other's last state
            # For simplicity, we'll use their current clarity and mood as "persuasion power"
            my_power = self.clarity_score * 0.7 + (self.mood / 13.0) * 0.3 # Weighted power
            other_power = other_agent.clarity_score * 0.7 + (other_agent.mood / 13.0) * 0.3

            print(f"[{self.name}]     My power: {my_power:.2f}, {other_agent.name}'s power: {other_power:.2f}")

            my_decision = self.decide(self.clarity_score) # Re-decide
            other_decision = other_agent.decide(other_agent.clarity_score) # Other agent re-decides

            if my_decision == other_decision:
                print(f"[{self.name}]   (Negotiation Success) Agreement reached: {self._get_state_name(my_decision)}")
                self.negotiation_attempts = 0 # Reset for future conflicts
                return my_decision # Conflict resolved

            # If still conflicting, try to sway the weaker agent
            if my_power > other_power:
                print(f"[{self.name}]     I am more persuasive. Attempting to sway {other_agent.name}...")
                # Simulate swaying: other agent's clarity/mood adjusts towards this agent's state
                other_agent.clarity_score = (other_agent.clarity_score + self.clarity_score) / 2
                other_agent.mood = int((other_agent.mood + self.mood) / 2)
                # This agent's mood might increase from perceived influence
                self.mood = min(13, self.mood + 1)
                # Other agent's cognition increases due to re-evaluation
                other_agent.cognition = min(1000, other_agent.cognition + 50)
            else:
                print(f"[{self.name}]     {other_agent.name} is more persuasive. I am being swayed...")
                # This agent's clarity/mood adjusts towards other agent's state
                self.clarity_score = (self.clarity_score + other_agent.clarity_score) / 2
                self.mood = int((self.mood + other_agent.mood) / 2)
                # Other agent's mood might increase from perceived influence
                other_agent.mood = min(13, other_agent.mood + 1)
                # This agent's cognition increases due to re-evaluation
                self.cognition = min(1000, self.cognition + 50)
            
            # After persuasion attempt, both agents will re-loop and re-decide
            time.sleep(0.8) # Simulate negotiation time

        print(f"[{self.name}]   (Negotiation Failure) Max attempts reached. No agreement. Defaulting to TEND or REFRAIN.")
        # If negotiation fails, default to TEND (for more discussion) or REFRAIN (for safety)
        # For this example, if no agreement, both agents will REFRAIN as a safe default.
        return REFRAIN # Default to REFRAIN if conflict cannot be resolved

    def execute_action(self, action):
        """
        Executes the action, with specific logging for negotiation outcomes.
        """
        super().execute_action(action) # Call parent method for general mood/cognition updates

        if action == AFFIRM:
            print(f"[{self.name}] ACTION: Proceeding after conflict resolution.")
        elif action == TEND:
            print(f"[{self.name}] TENDING: Continuing negotiation or awaiting further input.")
        elif action == REFRAIN:
            print(f"[{self.name}] REFRAIN: Halting due to unresolved conflict or safety protocol.")
        else:
            print(f"[{self.name}] WARNING: Unknown action state received: {action}")

    def run_cycle(self, input_data, other_agent=None):
        """
        Performs a full Ternlang cycle for a ConflictAgent,
        including initial decision and potential negotiation.
        """
        print(f"\n--- [{self.name}] Starting New Cycle ---")
        self.observe(input_data)
        
        my_initial_decision = self.decide(self.clarity_score)
        final_decision = my_initial_decision # Assume initial decision is final unless conflict

        if other_agent:
            # Get other agent's initial decision for comparison
            # Note: This is simplified; in a real system, other_agent would also run its observe/decide
            other_agent_initial_decision = other_agent.decide(other_agent.clarity_score) 

            if my_initial_decision != other_agent_initial_decision:
                print(f"[{self.name}] CONFLICT DETECTED! My decision: {self._get_state_name(my_initial_decision)}, {other_agent.name}'s: {self._get_state_name(other_agent_initial_decision)}")
                final_decision = self.negotiate(other_agent, input_data)
            else:
                print(f"[{self.name}] No conflict. Both agents agree on: {self._get_state_name(my_initial_decision)}")
                final_decision = my_initial_decision
        
        self.execute_action(final_decision)

        # Log to memory
        self.memory.append({
            "timestamp": datetime.datetime.now().isoformat(),
            "input": input_data,
            "context": self.context,
            "initial_decision": my_initial_decision,
            "final_decision": final_decision,
            "mood": self.mood,
            "cognition": self.cognition,
            "clarity": self.clarity_score,
            "negotiation_attempts": self.negotiation_attempts
        })

        print(f"--- [{self.name}] Cycle Complete ---")
        return final_decision

# --- Simulation ---
def simulate_conflict_resolution(num_scenarios=3):
    """
    Runs a simulation of two ConflictAgents resolving disagreements.
    """
    print("\n--- Ternlang Conflict Resolution Simulation Started ---")
    
    # Agent 1: Biased towards Affirm, higher initial clarity
    agent_alpha = ConflictAgent(name="Agent-Alpha", initial_clarity=0.7, bias_towards=AFFIRM)
    # Agent 2: Biased towards Refrain, lower initial clarity
    agent_beta = ConflictAgent(name="Agent-Beta", initial_clarity=0.4, bias_towards=REFRAIN)

    scenarios = [
        "Proposal: Initiate risky but high-reward project.", # Likely conflict
        "Proposal: Conduct routine system maintenance.", # Likely agreement
        "Proposal: Delay critical security patch due to ambiguity.", # Likely conflict
        "Proposal: Proceed with data migration, clarity is good.", # Likely agreement
        "Proposal: Unclear directive on emergency response. (High ambiguity)", # Likely conflict
    ]

    for i, scenario_input in enumerate(scenarios):
        print(f"\n===== SCENARIO {i+1}/{len(scenarios)} =====")
        
        # Agents run their cycles, passing each other for negotiation
        # Note: This simplified simulation has Agent Alpha initiate negotiation.
        # In a real system, a conflict manager or a more complex protocol would handle this.
        final_decision_alpha = agent_alpha.run_cycle(scenario_input, other_agent=agent_beta)
        # Agent Beta will also run its cycle, but its decision will be influenced by Alpha's negotiation
        # For this simulation, we'll assume the negotiation result from Alpha's cycle is the shared outcome.
        # In a more complex setup, Agent Beta would also call negotiate and they'd sync.
        
        # To show Beta's perspective after negotiation, we'll update its state based on Alpha's final decision
        # and print its final state for the cycle.
        # This is a simplification to ensure both agents reflect the negotiated outcome.
        print(f"\n--- {agent_beta.name} reflects on negotiated outcome ---")
        agent_beta.last_action = final_decision_alpha
        agent_beta.execute_action(final_decision_alpha) # Beta executes the agreed-upon action
        agent_beta.memory.append({ # Add to Beta's memory for consistency
            "timestamp": datetime.datetime.now().isoformat(),
            "input": scenario_input,
            "context": agent_beta.context,
            "initial_decision": agent_beta.decide(agent_beta.clarity_score), # Re-decide for logging initial
            "final_decision": final_decision_alpha,
            "mood": agent_beta.mood,
            "cognition": agent_beta.cognition,
            "clarity": agent_beta.clarity_score,
            "negotiation_attempts": agent_beta.negotiation_attempts
        })
        print(f"--- {agent_beta.name} Cycle Adjusted ---")

        time.sleep(2) # Pause for readability

    print("\n--- Ternlang Conflict Resolution Simulation Finished ---")

    # Optional: Print final states and memory of each agent
    print("\n--- Final Agent States ---")
    print(f"[{agent_alpha.name}] Final Mood: {agent_alpha.mood}, Cognition: {agent_alpha.cognition}, Clarity: {agent_alpha.clarity_score:.2f}, Last Action: {agent_alpha._get_state_name(agent_alpha.last_action)}")
    print(f"[{agent_beta.name}] Final Mood: {agent_beta.mood}, Cognition: {agent_beta.cognition}, Clarity: {agent_beta.clarity_score:.2f}, Last Action: {agent_beta._get_state_name(agent_beta.last_action)}")

    # You could also print memory snapshots here if desired
