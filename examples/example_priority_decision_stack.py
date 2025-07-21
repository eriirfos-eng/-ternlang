# examples/example_priority_decision_stack.py
# Demonstrates a TernAgent juggling multiple inputs with varying TEMPRA levels,
# implementing dynamic priority shuffling and "soft preemption" (context switch
# without full override) to manage its attention and decision-making.

# Assuming ternlang_prototype.py is in the same parent directory
from ternlang_prototype import REFRAIN, TEND, AFFIRM, TernAgent
import random
import time
import datetime
import uuid
# MemoryManager is automatically imported via TernAgent's super().__init__()

print("--- Ternlang Example: Priority Decision Stack Agent ---")

class PriorityAgent(TernAgent):
    """
    A TernAgent capable of managing a dynamic stack of inputs with associated
    TEMPRA (Threat, Exposure, Mitigation, Probability, Risk, Action) levels.
    It prioritizes tasks, performs "soft preemption" (context switching),
    and adapts its decision-making based on the most urgent/important task.
    """
    def __init__(self, name="Prioritizer", initial_mood=7):
        super().__init__(name, initial_context="idle")
        self.mood = initial_mood
        self.cognition = 500
        self.current_task = None # The task currently being processed
        self.task_queue = [] # Stores (input_data, tempra_risk, task_id) tuples
        self.active_task_id = None # ID of the task currently holding agent's focus

        print(f"[{self.name}] Initialized. Mood={self.mood}, Cognition={self.cognition}")

    def _calculate_tempra_risk(self, input_data):
        """
        Simulates TEMPRA risk calculation based on input data.
        (Simplified version from example_urgency_override.py)
        """
        threat = random.uniform(0.0, 0.4)
        exposure = random.uniform(0.0, 0.4)
        probability = random.uniform(0.0, 0.4)

        if "critical" in input_data.lower() or "emergency" in input_data.lower():
            threat = random.uniform(0.7, 1.0)
            probability = random.uniform(0.7, 1.0)
        elif "urgent" in input_data.lower() or "immediate" in input_data.lower():
            threat = random.uniform(0.5, 0.8)
            probability = random.uniform(0.5, 0.8)
        elif "routine" in input_data.lower() or "low priority" in input_data.lower():
            threat = random.uniform(0.0, 0.2)
            probability = random.uniform(0.0, 0.2)
        
        # Assume mitigation is constant for simplicity, or could be context-dependent
        mitigation = random.uniform(0.5, 0.8) # Higher is better mitigation

        raw_risk = (threat + exposure + probability) * (1 - mitigation)
        risk_score = min(1.0, raw_risk / 3.0) # Normalize to 0-1 range
        return risk_score, {"threat": threat, "exposure": exposure, "mitigation": mitigation, "probability": probability}

    def add_task(self, input_data):
        """
        Adds a new task to the queue, calculates its TEMPRA risk, and assigns an ID.
        """
        task_id = str(uuid.uuid4())
        tempra_risk, tempra_components = self._calculate_tempra_risk(input_data)
        self.task_queue.append({
            "id": task_id,
            "input_data": input_data,
            "tempra_risk": tempra_risk,
            "tempra_components": tempra_components,
            "status": "pending",
            "received_time": datetime.datetime.now()
        })
        # Sort the queue by TEMPRA risk (highest risk first)
        self.task_queue.sort(key=lambda x: x["tempra_risk"], reverse=True)
        print(f"[{self.name}] Added task '{input_data[:20]}...' (ID: {task_id}) with TEMPRA Risk: {tempra_risk:.2f}")

    def _select_current_task(self):
        """
        Selects the highest priority task from the queue.
        Implements soft preemption if a higher priority task arrives.
        """
        if not self.task_queue:
            self.current_task = None
            self.active_task_id = None
            return

        highest_priority_task = self.task_queue[0]

        if self.active_task_id is None:
            # No active task, pick the highest priority one
            self.current_task = highest_priority_task
            self.active_task_id = highest_priority_task["id"]
            print(f"[{self.name}] Selected new primary task (ID: {self.active_task_id}) - '{self.current_task['input_data'][:20]}...'")
        elif self.active_task_id != highest_priority_task["id"]:
            # Soft preemption: a higher priority task has arrived
            old_task = next((t for t in self.task_queue if t["id"] == self.active_task_id), None)
            if old_task:
                old_task["status"] = "preempted"
                print(f"[{self.name}]   (Soft Preemption) Task (ID: {self.active_task_id}) preempted by higher priority task (ID: {highest_priority_task['id']}).")
                self.mood = max(1, self.mood - 1) # Slight mood dip from interruption
                self.cognition = min(1000, self.cognition + 50) # Cognitive load for context switch

            self.current_task = highest_priority_task
            self.active_task_id = highest_priority_task["id"]
            print(f"[{self.name}] Switched to new primary task (ID: {self.active_task_id}) - '{self.current_task['input_data'][:20]}...'")
        
        self.current_task["status"] = "active"


    def observe(self, input_data_for_queueing=None, other_agent_actions=None):
        """
        Observes environment and updates task queue.
        If current_task exists, its input is used for core observation.
        """
        # If new input comes in, add it to the queue first
        if input_data_for_queueing:
            self.add_task(input_data_for_queueing)

        self._select_current_task() # Select or re-select the active task

        if not self.current_task:
            print(f"[{self.name}] Observing: (No active task).")
            self.context = "idle"
            relevance_score = 0.0
            self.mood = min(13, self.mood + 1) # Mood can improve if idle is productive
            self.cognition = max(0, self.cognition - 10) # Low cognitive load
            return self.context, relevance_score

        # Use the current_task's input for core observation logic
        actual_input_for_observation = self.current_task["input_data"]
        print(f"[{self.name}] Observing primary task: '{actual_input_for_observation[:30]}...' (Risk: {self.current_task['tempra_risk']:.2f})")
        
        current_context = "evaluating_task"
        relevance_score = self.current_task["tempra_risk"] # Risk directly influences relevance for decision

        # Adjust context based on risk level
        if self.current_task["tempra_risk"] >= 0.8:
            current_context = "high_priority_critical"
        elif self.current_task["tempra_risk"] >= 0.5:
            current_context = "medium_priority"
        else:
            current_context = "low_priority_routine"

        self.context = current_context
        print(f"[{self.name}] Context: '{self.context}', Relevance (from Risk): {relevance_score:.2f}")
        return self.context, relevance_score

    def decide(self, relevance_score, other_agent_decision=None):
        """
        Decides the action based on relevance (TEMPRA risk) of the current task.
        """
        print(f"[{self.name}] Deciding based on task relevance: {relevance_score:.2f}...")
        
        if not self.current_task:
            decision = TEND # Stay idle
            print(f"[{self.name}] No active task. Decided to TEND (idle).")
            return decision

        # Decision heavily influenced by TEMPRA risk
        if relevance_score >= 0.7: # High risk -> AFFIRM
            decision = AFFIRM
            print(f"[{self.name}] High TEMPRA risk. Decided to AFFIRM.")
        elif relevance_score < 0.3: # Low risk -> TEND or REFRAIN (less urgent)
            decision = TEND # Tend for low priority tasks
            print(f"[{self.name}] Low TEMPRA risk. Decided to TEND.")
        else: # Moderate risk -> TEND
            decision = TEND
            print(f"[{self.name}] Moderate TEMPRA risk. Decided to TEND.")

        # Adjust mood and cognition based on decision and task context
        if decision == AFFIRM:
            self.mood = min(13, self.mood + 1)
            self.cognition = max(0, self.cognition - 30) # Action consumes cognition
        elif decision == TEND:
            self.mood = max(1, min(13, self.mood - 1)) # Tending to a task can be draining
            self.cognition = min(1000, self.cognition + 50) # Cognitive effort for processing
        elif decision == REFRAIN: # Not explicitly chosen here but for completeness
            self.mood = max(1, self.mood - 2)
            self.cognition = max(0, self.cognition - 20)

        print(f"[{self.name}] Decision: {self._get_state_name(decision)}")
        return decision

    def execute_action(self, action):
        """
        Executes the action. If a task is completed, it's removed from the queue.
        """
        super().execute_action(action)

        if not self.current_task:
            print(f"[{self.name}] ACTION: Remaining idle.")
            return

        # Simulate task completion based on action
        if action == AFFIRM:
            print(f"[{self.name}] ACTION: Executing task (ID: {self.current_task['id']}) - '{self.current_task['input_data'][:30]}...'")
            self.current_task["status"] = "completed"
            # Remove completed task from queue
            self.task_queue = [t for t in self.task_queue if t["id"] != self.current_task["id"]]
            self.active_task_id = None # No active task after completion
            print(f"[{self.name}] Task (ID: {self.current_task['id']}) completed. Queue size: {len(self.task_queue)}")
            self.mood = min(13, self.mood + 2) # Mood boost from completion
            self.cognition = max(0, self.cognition - 50) # Cognitive relief
        elif action == TEND:
            print(f"[{self.name}] TENDING: Processing task (ID: {self.current_task['id']}) - '{self.current_task['input_data'][:30]}...'")
            # Task remains active, status might change to 'in_progress'
            self.current_task["status"] = "in_progress"
            self.mood = max(1, min(13, self.mood - 1)) # Tending can be draining
            self.cognition = min(1000, self.cognition + 30) # Continued cognitive effort
        elif action == REFRAIN:
            print(f"[{self.name}] REFRAIN: Halting task (ID: {self.current_task['id']}) - '{self.current_task['input_data'][:30]}...'")
            self.current_task["status"] = "halted"
            self.task_queue = [t for t in self.task_queue if t["id"] != self.current_task["id"]] # Remove halted task
            self.active_task_id = None
            self.mood = max(1, self.mood - 3) # Mood drop from halting
            self.cognition = max(0, self.cognition - 20)
        else:
            print(f"[{self.name}] WARNING: Unknown action state received: {action}")

    def run_cycle(self, new_input_for_queue=None, other_agent_actions=None):
        """
        Performs a full Ternlang cycle for a PriorityAgent.
        Takes an optional new input to add to the queue.
        """
        print(f"\n--- [{self.name}] Starting New Cycle ---")
        
        # Observe now handles adding new inputs to the queue and selecting the current task
        current_context, relevance_score = self.observe(new_input_for_queue, other_agent_actions)
        
        decision = self.decide(relevance_score)
        self.execute_action(decision)

        # Add entry to MemoryManager
        self.memory_manager.add_entry(
            input_data=new_input_for_queue if new_input_for_queue else "No new input this cycle.",
            context=current_context,
            decision=decision,
            mood=self.mood,
            cognition=self.cognition,
            impact=random.randint(1, 13),
            
            Summary=f"Agent completed cycle. Decision: {self._get_state_name(decision)}.",
            Flags_Reminders=[],
            Milestone_Events=[],
            Lessons_Learned=[],
            Approach_Adjustments=[],
            Pending_Action_Items=[],
            Timestamp_Notes="",

            # Priority Agent specific fields
            CurrentActiveTaskID=self.active_task_id,
            CurrentActiveTaskInput=self.current_task["input_data"][:50] if self.current_task else "None",
            CurrentActiveTaskRisk=round(self.current_task["tempra_risk"], 2) if self.current_task else 0.0,
            TaskQueueSize=len(self.task_queue)
        )

        print(f"--- [{self.name}] Cycle Complete ---")
        return decision

# --- Simulation ---
def simulate_priority_agent(num_cycles=10):
    """
    Runs a simulation of a PriorityAgent, demonstrating dynamic priority management.
    """
    print("\n--- Ternlang Priority Decision Stack Agent Simulation Started ---")
    
    priority_agent = PriorityAgent(name="TaskMaster", initial_mood=8)
    priority_agent.memory_manager.load_from_file() # Load memory at start

    # Define tasks with varying urgency/priority
    # Format: (input_string, cycle_to_add)
    task_schedule = [
        ("Routine system check. Low priority.", 0),
        ("Urgent request: Client feedback needs immediate review.", 1), # Higher priority
        ("Critical alert: Database integrity compromised!", 2), # Highest priority, should preempt
        ("Another routine background process.", 3),
        ("Emergency! Server overload imminent!", 4), # Very high priority
        ("Review quarterly report. Non-urgent.", 5),
        ("Immediate action: Security breach detected!", 6), # High priority
        ("Daily log compilation. Low priority.", 7),
    ]
    
    # Keep track of tasks added
    tasks_added_this_cycle = []

    for i in range(num_cycles):
        print(f"\n===== SIMULATION CYCLE {i+1}/{num_cycles} =====")
        
        new_input_for_queue = None
        # Check if any tasks are scheduled for this cycle
        for task_input, schedule_cycle in task_schedule:
            if schedule_cycle == i:
                new_input_for_queue = task_input # Only one input per cycle for simplicity
                print(f"[{priority_agent.name}] Incoming new task: '{new_input_for_queue}'")
                break # Add only one scheduled task per cycle

        priority_agent.run_cycle(new_input_for_queue)
        time.sleep(1.5)

    print("\n--- Ternlang Priority Decision Stack Agent Simulation Finished ---")

    priority_agent.memory_manager.save_to_file() # Save memory at end

    print("\n--- Sample of Agent Memory (Structured) ---")
    for entry in priority_agent.memory_manager.get_recent_entries(min(5, len(priority_agent.memory_manager.entries))):
        for key, value in entry.items():
            print(f"  {key}: {value}")
        print("  ---")

    print("\n--- Final Agent State ---")
    print(f"[{priority_agent.name}] Final Mood: {priority_agent.mood}, Cognition: {priority_agent.cognition}, Last Action: {priority_agent._get_state_name(priority_agent.last_action)}")
    print(f"[{priority_agent.name}] Remaining Tasks in Queue: {len(priority_agent.task_queue)}")
    for task in priority_agent.task_queue:
        print(f"  - Task ID: {task['id'][:8]}..., Input: '{task['input_data'][:20]}...', Risk: {task['tempra_risk']:.2f}, Status: {task['status']}")
