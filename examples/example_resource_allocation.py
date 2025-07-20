# examples/example_resource_allocation.py
# Demonstrates Ternlang's REFRAIN, TEND, AFFIRM in a resource allocation scenario.

# Assuming ternlang_prototype.py is in the same parent directory
# If you moved ternlang_prototype.py to a /src directory, you might need:
# from src.ternlang_prototype import REFRAIN, TEND, AFFIRM, TernAgent
from ternlang_prototype import REFRAIN, TEND, AFFIRM, TernAgent

print("--- Ternlang Example: Resource Allocation Decision ---")

class ResourceManager(TernAgent):
    """
    A TernAgent specialized for managing resource allocation.
    It decides whether to AFFIRM, TEND, or REFRAIN from allocating a resource
    based on its availability.
    """
    def __init__(self, name="ResourceManager", initial_resource_level=100):
        super().__init__(name, initial_context="monitoring_resources")
        self.resource_level = initial_resource_level
        print(f"[{self.name}] Initial resource level: {self.resource_level}")

    def observe_resource_status(self, required_amount):
        """
        Observes the current resource status relative to a required amount.
        Updates context and returns a relevance score based on availability.
        """
        print(f"[{self.name}] Observing resource for request: {required_amount}")
        current_context = "neutral"
        relevance_score = 0.5 # Default

        if self.resource_level >= required_amount:
            current_context = "sufficient_resources"
            relevance_score = 0.9
        elif self.resource_level > 0 and self.resource_level < required_amount:
            current_context = "limited_resources"
            relevance_score = 0.7
        else: # self.resource_level == 0
            current_context = "no_resources"
            relevance_score = 0.1

        self.context = current_context # Update agent's internal context
        print(f"[{self.name}] Resource context: '{self.context}', Relevance: {relevance_score:.2f}")
        return current_context, relevance_score

    def decide_allocation(self, relevance_score):
        """
        Decides the allocation action based on resource context and relevance.
        Overrides the generic decide to implement specific resource logic.
        """
        print(f"[{self.name}] Deciding on allocation...")
        decision = TEND # Default to TEND

        if self.context == "sufficient_resources" and relevance_score > 0.8:
            decision = AFFIRM # Enough resources, proceed
        elif self.context == "limited_resources" and relevance_score > 0.6:
            decision = TEND # Resources are limited, tend (wait, re-evaluate, partial allocation?)
        elif self.context == "no_resources" or relevance_score < 0.2:
            decision = REFRAIN # No resources or very low relevance, do not allocate

        print(f"[{self.name}] Allocation decision: {self._get_state_name(decision)}")
        return decision

    def allocate(self, amount):
        """
        Simulates the allocation action, updating resource level if AFFIRMED.
        """
        self.observe_resource_status(amount)
        decision = self.decide_allocation(self.cognition / 1000) # Use cognition as a proxy for relevance for simplicity
        self.execute_action(decision)

        if decision == AFFIRM:
            self.resource_level -= amount
            print(f"[{self.name}] Allocated {amount} units. Remaining: {self.resource_level}")
        elif decision == TEND:
            print(f"[{self.name}] Tending to resource request. No allocation yet.")
        elif decision == REFRAIN:
            print(f"[{self.name}] Refrained from allocating {amount} units due to insufficient resources.")
        
        return decision

# --- Simulation ---
resource_manager = ResourceManager(name="ServerResource", initial_resource_level=150)

# Scenario 1: Sufficient resources
print("\n--- Scenario 1: Requesting 50 units (Sufficient) ---")
resource_manager.allocate(50)

# Scenario 2: Limited resources
print("\n--- Scenario 2: Requesting 80 units (Limited) ---")
resource_manager.allocate(80)

# Scenario 3: No resources
print("\n--- Scenario 3: Requesting 30 units (Insufficient) ---")
resource_manager.allocate(30)

# Scenario 4: Very small request (might still be TEND if limited)
print("\n--- Scenario 4: Requesting 5 units (Very Small) ---")
resource_manager.allocate(5)

print("\n--- Resource Allocation Example Finished ---")
