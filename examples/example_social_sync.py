# examples/example_social_sync.py
# Demonstrates multiple TernAgents synchronizing their state and decisions,
# including peer influence and a supervisor override.

# Assuming ternlang_prototype.py is in the same parent directory
from ternlang_prototype import REFRAIN, TEND, AFFIRM, TernAgent
import random
import time

print("--- Ternlang Example: Social Synchronization Agent Swarm ---")

class SynchronizedAgent(TernAgent):
    """
    A TernAgent designed to be influenced by the collective state of its peers.
    It can adapt its decision based on majority TEND behavior and can be
    overridden by a 'Supervisor' agent.
    """
    def __init__(self, name="SyncAgent", initial_mood=7, initial_clarity=0.5):
        super().__init__(name, initial_context="observing_peers")
        self.mood = initial_mood
        self.cognition = 500
        self.clarity_score = initial_clarity # Individual clarity
        self.is_supervisor = False # Flag to identify supervisor
        print(f"[{self.name}] Initialized with Mood: {self.mood}, Clarity: {self.clarity_score:.2f}")

    def observe(self, input_data, collective_state=None):
        """
        Observes external input and the collective state of the swarm.
        [NEW]: Integrates collective state (mood, cognition, actions) for influence.
        """
        print(f"[{self.name}] Observing: '{input_data}'")
        
        # Store current clarity before updating for delta calculation
        current_clarity_at_start = self.clarity_score

        # Simulate clarity calculation based on keywords (similar to previous examples)
        if "unclear" in input_data.lower() or "vague" in input_data.lower():
            self.clarity_score = random.uniform(0.0, 0.3)
            self.context = "highly_ambiguous"
        elif "partially clear" in input_data.lower() or "some context missing" in input_data.lower():
            self.clarity_score = random.uniform(0.3, 0.6)
            self.context = "moderately_clear"
        elif "very clear" in input_data.lower() or "explicit" in input_data.lower():
            self.clarity_score = random.uniform(0.7, 1.0)
            self.context = "very_clear"
        else:
            self.clarity_score = random.uniform(0.4, 0.7)
            self.context = "evaluating_situation"

        # [NEW]: Influence from Collective State
        if collective_state:
            # Calculate majority TEND from other agents' last actions
            other_actions = [s['last_action'] for s in collective_state if s['name'] != self.name]
            tend_count = other_actions.count(TEND)
            affirm_count = other_actions.count(AFFIRM)
            refrain_count = other_actions.count(REFRAIN)
            total_others = len(other_actions)

            if total_others > 0:
                # If majority (e.g., >60%) are TENDING, this agent's clarity might decrease slightly
                # or its mood might shift towards TEND if it was leaning otherwise.
                if tend_count / total_others > 0.6:
                    self.clarity_score = max(0.0, self.clarity_score - 0.1) # Becomes more cautious
                    self.mood = max(1, min(13, self.mood - 1)) # Mood might reflect shared uncertainty
                    print(f"[{self.name}]   (Social Sync) Majority TENDING, reducing clarity and mood slightly.")
                elif affirm_count / total_others > 0.6:
                    self.clarity_score = min(1.0, self.clarity_score + 0.1) # Becomes more confident
                    self.mood = min(13, self.mood + 1) # Mood reflects shared confidence
                    print(f"[{self.name}]   (Social Sync) Majority AFFIRMING, increasing clarity and mood slightly.")
                elif refrain_count / total_others > 0.6:
                    self.clarity_score = max(0.0, self.clarity_score - 0.15) # Becomes more cautious
                    self.mood = max(1, self.mood - 2) # Mood reflects shared caution
                    print(f"[{self.name}]   (Social Sync) Majority REFRAINING, significantly reducing clarity and mood.")

        print(f"[{self.name}] Context: '{self.context}', Clarity Score: {self.clarity_score:.2f}, Mood: {self.mood}, Cognition: {self.cognition}")
        return self.context, self.clarity_score

    def decide(self, clarity_score, supervisor_directive=None):
        """
        Decides the action, influenced by clarity and a potential supervisor directive.
        [NEW]: Supervisor directive can override local ambiguity.
        """
        print(f"[{self.name}] Deciding based on clarity: {clarity_score:.2f}...")
        decision = TEND # Default

        # [NEW]: Supervisor Override Logic
        if supervisor_directive:
            print(f"[{self.name}]   (Supervisor Override) Receiving directive: {self._get_state_name(supervisor_directive)}")
            if supervisor_directive == AFFIRM:
                decision = AFFIRM
                self.clarity_score = 1.0 # Supervisor provides absolute clarity
                self.mood = min(13, self.mood + 2) # Mood boost from clear direction
                self.cognition = max(0, self.cognition - 100) # Reduced cognitive load
            elif supervisor_directive == REFRAIN:
                decision = REFRAIN
                self.clarity_score = 0.0 # Supervisor enforces halt
                self.mood = max(1, self.mood - 2) # Mood drop from forced stop
                self.cognition = max(0, self.cognition - 50) # Reduced cognitive load
            # If supervisor TENDs, it reinforces the TEND state, no direct override

            print(f"[{self.name}]   (Supervisor Override) Decision forced to: {self._get_state_name(decision)}")
            return decision # Override takes precedence

        # Normal decision logic (similar to AmbiguityAgent, but simplified for this example)
        if clarity_score >= 0.7:
            decision = AFFIRM
        elif clarity_score < 0.7 and self.mood > 5: # If ambiguous but not too low mood, tend
            decision = TEND
        else: # Ambiguous and low mood, or very low clarity
            decision = REFRAIN

        # Adjust mood and cognition based on decision (if not overridden)
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
        Executes the action.
        """
        # Call parent method for general mood/cognition updates
        # Note: Mood/Cognition are also adjusted in decide()
        # For this example, we'll let decide() handle most of it.
        # super().execute_action(action)

        self.last_action = action # Store the last action for collective state

        if action == AFFIRM:
            print(f"[{self.name}] ACTION: Proceeding with synchronized task!")
        elif action == TEND:
            print(f"[{self.name}] TENDING: Synchronizing, observing peers, or awaiting clarity.")
        elif action == REFRAIN:
            print(f"[{self.name}] REFRAIN: Halting due to collective uncertainty or supervisor directive.")
        else:
            print(f"[{self.name}] WARNING: Unknown action state received: {action}")

    def run_cycle(self, input_data, collective_state=None, supervisor_directive=None):
        """
        Performs a full Ternlang cycle for a SynchronizedAgent.
        Passes collective_state and supervisor_directive.
        """
        print(f"\n--- [{self.name}] Starting New Cycle ---")
        current_context, relevance_score = self.observe(input_data, collective_state)
        decision = self.decide(relevance_score, supervisor_directive)
        self.execute_action(decision)

        # Log to memory (similar to TernAgent)
        self.memory.append({
            "timestamp": datetime.datetime.now().isoformat(),
            "input": input_data,
            "context": current_context,
            "decision": decision,
            "mood": self.mood,
            "cognition": self.cognition
        })

        print(f"--- [{self.name}] Cycle Complete ---")
        return decision

class SupervisorAgent(TernAgent):
    """
    A special TernAgent that represents a supervisor or authority.
    It has inherently high clarity and can issue directives.
    """
    def __init__(self, name="Supervisor"):
        super().__init__(name, initial_context="providing_guidance")
        self.mood = 12 # High mood, confident
        self.cognition = 900 # High cognition, analytical
        self.clarity_score = 1.0 # Assumed high clarity
        self.is_supervisor = True

    def issue_directive(self, current_swarm_state):
        """
        Based on the collective state of the swarm, issues a directive (AFFIRM, TEND, or REFRAIN).
        This simulates the supervisor's decision to intervene.
        """
        print(f"\n[{self.name}] --- SUPERVISOR REVIEWING SWARM STATE ---")
        
        # Analyze collective state
        total_agents = len(current_swarm_state)
        tend_count = sum(1 for s in current_swarm_state if s['last_action'] == TEND)
        affirm_count = sum(1 for s in current_swarm_state if s['last_action'] == AFFIRM)
        refrain_count = sum(1 for s in current_swarm_state if s['last_action'] == REFRAIN)

        directive = None
        if total_agents > 0:
            if tend_count / total_agents > 0.6: # If majority are TENDING
                print(f"[{self.name}] Swarm is largely TENDING ({tend_count}/{total_agents}). Considering intervention.")
                # If supervisor's clarity is high, it might push for AFFIRM or REFRAIN
                if self.clarity_score > 0.9:
                    directive = random.choice([AFFIRM, REFRAIN]) # Supervisor forces a decision
                    print(f"[{self.name}] Swarm stuck in TEND. Supervisor issues a decisive directive: {self._get_state_name(directive)}")
                else:
                    directive = TEND # Supervisor also TENDs, reinforcing observation
                    print(f"[{self.name}] Swarm is TENDING. Supervisor reinforces TEND.")
            elif refrain_count / total_agents > 0.5: # If a significant portion are REFRAINING
                print(f"[{self.name}] Swarm is largely REFRAINING ({refrain_count}/{total_agents}). Supervisor confirms halt.")
                directive = REFRAIN
            elif affirm_count / total_agents > 0.7: # If majority are AFFIRMING
                print(f"[{self.name}] Swarm is largely AFFIRMING ({affirm_count}/{total_agents}). Supervisor approves.")
                directive = AFFIRM
        
        # Simulate supervisor's own cognitive effort/mood
        self.cognition = max(0, self.cognition - 20)
        self.mood = min(13, self.mood + 0.5) # Supervisor remains relatively stable
        
        return directive

# --- Simulation ---
def simulate_social_sync_swarm(num_cycles=8, num_agents=4):
    """
    Runs a simulation of a swarm of SynchronizedAgents with a Supervisor.
    """
    print("\n--- Ternlang Social Synchronization Swarm Simulation Started ---")
    
    agents = [SynchronizedAgent(name=f"SyncAgent-{i+1}", initial_clarity=random.uniform(0.3, 0.7)) for i in range(num_agents)]
    supervisor = SupervisorAgent(name="CentralCommand")

    # Example inputs to simulate different scenarios
    # These inputs can be ambiguous to encourage TEND states
    example_inputs = [
        "Directive: Analyze the vague market data.",
        "Situation: Uncertain about next steps for project X.",
        "Request: Clarify the ambiguous client feedback.",
        "Event: Unexpected system behavior, requires investigation.",
        "Guidance: Proceed with caution, data is inconclusive.",
        "Command: Full system deployment, all clear.", # Clear command
        "Warning: Critical failure imminent, halt all operations!", # Clear halt
        "Data: Mixed signals from external sensors.",
        "Query: What is the collective sentiment on this proposal?"
    ]

    # Store last cycle's state for social influence in the next cycle
    last_cycle_collective_state = []

    for i in range(num_cycles):
        print(f"\n===== SIMULATION CYCLE {i+1}/{num_cycles} =====")
        current_input = random.choice(example_inputs)
        
        # Supervisor issues a directive based on the *previous* collective state
        # (or can be hardcoded for specific scenarios)
        supervisor_directive = supervisor.issue_directive(last_cycle_collective_state)

        current_cycle_states = []
        for agent in agents:
            # Each agent runs its cycle, influenced by the collective state and supervisor
            action_taken = agent.run_cycle(current_input, 
                                           collective_state=last_cycle_collective_state,
                                           supervisor_directive=supervisor_directive)
            
            # Collect current state for next cycle's collective state
            current_cycle_states.append({
                'name': agent.name,
                'last_action': action_taken,
                'mood': agent.mood,
                'cognition': agent.cognition,
                'clarity_score': agent.clarity_score
            })
            time.sleep(0.3) # Short pause for readability

        last_cycle_collective_state = current_cycle_states # Update for next cycle

    print("\n--- Ternlang Social Synchronization Swarm Simulation Finished ---")

    # Optional: Print final states and memory of each agent
    print("\n--- Final Agent States ---")
    for agent in agents:
        print(f"[{agent.name}] Final Mood: {agent.mood}, Cognition: {agent.cognition}, Clarity: {agent.clarity_score:.2f}, Last Action: {agent._get_state_name(agent.last_action)}")
    print(f"[{supervisor.name}] Final Mood: {supervisor.mood}, Cognition: {supervisor.cognition}")

    # You could also print memory snapshots here if desired, similar to ternlang_prototype.py
