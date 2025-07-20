# examples/example_urgency_override.py
# Demonstrates how a calculated TEMPRA (Threat, Exposure, Mitigation, Probability, Risk, Action)
# score can override Ternlang's REFRAIN state, forcing an AFFIRM even under low clarity,
# simulating high-stakes action driven by comprehensive risk assessment.

# Assuming ternlang_prototype.py is in the same parent directory
from ternlang_prototype import REFRAIN, TEND, AFFIRM, TernAgent
import random
import time
import datetime

print("--- Ternlang Example: Urgency Override Agent with TEMPRA ---")

class TEMPRAAgent(TernAgent):
    """
    A TernAgent that incorporates a TEMPRA (Threat, Exposure, Mitigation, Probability, Risk, Action)
    framework for decision-making under pressure.
    If the calculated Risk score exceeds a threshold, the agent can be forced to AFFIRM,
    even if its internal clarity is low, overriding a potential REFRAIN.
    """
    def __init__(self, name="CrisisResponder", initial_clarity=0.5):
        super().__init__(name, initial_context="monitoring_threats")
        self.clarity_score = initial_clarity # 0.0 (uncertain) to 1.0 (clear)
        
        # [NEW]: TEMPRA Components (0.0 to 1.0 scale)
        self.threat = 0.0       # Severity of potential negative event
        self.exposure = 0.0     # Vulnerability to the threat
        self.mitigation = 0.0   # Measures in place (higher is better mitigation)
        self.probability = 0.0  # Likelihood of threat occurrence
        self.risk_score = 0.0   # Calculated composite risk (replaces urgency_score)

        self.risk_threshold_for_override = 0.8 # Above this, REFRAIN becomes invalid
        self.burn_through_ambiguity_threshold = 0.96 # If risk >= 0.96, forces AFFIRM regardless of clarity

        # Initialize mood and cognition
        self.mood = 7
        self.cognition = 500
        print(f"[{self.name}] Initial clarity: {self.clarity_score:.2f}, Risk: {self.risk_score:.2f}")

    def observe(self, input_data, other_agent_actions=None):
        """
        Observes input, calculates initial clarity and TEMPRA components,
        then derives the composite risk_score.
        """
        print(f"[{self.name}] Observing input: '{input_data}'")
        
        current_context = "neutral_observation"
        
        # Simulate clarity calculation (same as before)
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

        # [NEW]: Simulate TEMPRA component calculation based on keywords
        # Threat (T)
        if "critical" in input_data.lower() or "catastrophic" in input_data.lower():
            self.threat = random.uniform(0.8, 1.0)
        elif "major threat" in input_data.lower() or "significant" in input_data.lower():
            self.threat = random.uniform(0.5, 0.8)
        else:
            self.threat = random.uniform(0.0, 0.4)

        # Exposure (E)
        if "exposed" in input_data.lower() or "vulnerable" in input_data.lower():
            self.exposure = random.uniform(0.7, 1.0)
        elif "partially protected" in input_data.lower():
            self.exposure = random.uniform(0.3, 0.7)
        else:
            self.exposure = random.uniform(0.0, 0.3) # Protected/low exposure

        # Mitigation (M) - Higher is better mitigation
        if "well-mitigated" in input_data.lower() or "strong defenses" in input_data.lower():
            self.mitigation = random.uniform(0.7, 1.0)
        elif "some mitigation" in input_data.lower():
            self.mitigation = random.uniform(0.3, 0.7)
        else:
            self.mitigation = random.uniform(0.0, 0.3) # Unmitigated/low mitigation

        # Probability (P)
        if "imminent" in input_data.lower() or "likely" in input_data.lower():
            self.probability = random.uniform(0.7, 1.0)
        elif "possible" in input_data.lower():
            self.probability = random.uniform(0.3, 0.7)
        else:
            self.probability = random.uniform(0.0, 0.3) # Unlikely

        # [NEW]: Calculate composite Risk Score
        # A simple model: (Threat + Exposure + Probability) * (1 - Mitigation)
        # Max value for (T+E+P) is 3.0, (1-M) is max 1.0. Normalize to 0-1.0
        raw_risk = (self.threat + self.exposure + self.probability) * (1 - self.mitigation)
        self.risk_score = min(1.0, raw_risk / 3.0) # Normalize to 0-1 range

        self.context = current_context
        print(f"[{self.name}] Context: '{self.context}', Clarity: {self.clarity_score:.2f}, TEMPRA Risk: {self.risk_score:.2f}")
        print(f"[{self.name}]   (T:{self.threat:.2f}, E:{self.exposure:.2f}, M:{self.mitigation:.2f}, P:{self.probability:.2f})")
        return self.context, self.clarity_score # clarity_score as relevance_score

    def decide(self, clarity_score, supervisor_directive=None):
        """
        Decides the action, with high TEMPRA Risk potentially overriding normal REFRAIN
        and burning through ambiguity.
        """
        print(f"[{self.name}] Deciding based on clarity: {clarity_score:.2f} and TEMPRA Risk: {self.risk_score:.2f}...")
        decision = TEND # Default

        # [NEW]: TEMPRA Risk Override Logic (replaces old urgency override)
        if self.risk_score >= self.burn_through_ambiguity_threshold:
            print(f"[{self.name}] --- CRITICAL TEMPRA RISK ({self.risk_score:.2f})! BURNING THROUGH AMBIGUITY! ---")
            decision = AFFIRM # Force AFFIRM, REFRAIN is not an option
            self.clarity_score = max(0.5, self.clarity_score) # Assume minimum clarity for forced action
            self.mood = min(13, self.mood + 2) # Mood might increase due to decisive action under extreme pressure
            self.cognition = min(1000, self.cognition + 150) # Very high cognitive load for forced decision
            print(f"[{self.name}] Forced decision: {self._get_state_name(decision)}")
            return decision
        elif self.risk_score >= self.risk_threshold_for_override:
            print(f"[{self.name}] --- HIGH TEMPRA RISK ({self.risk_score:.2f})! OVERRIDING POTENTIAL REFRAIN! ---")
            decision = AFFIRM # Force AFFIRM, REFRAIN is not an option
            self.clarity_score = max(0.4, self.clarity_score) # Assume minimum clarity
            self.mood = min(13, self.mood + 1) # Mood might increase due to decisive action under pressure
            self.cognition = min(1000, self.cognition + 100) # High cognitive load for forced decision
            print(f"[{self.name}] Forced decision: {self._get_state_name(decision)}")
            return decision

        # Normal decision logic (if no TEMPRA risk override)
        if clarity_score >= 0.7:
            decision = AFFIRM
            print(f"[{self.name}] High clarity detected. Ready to AFFIRM.")
        elif clarity_score < 0.7 and self.mood > 5:
            decision = TEND
            print(f"[{self.name}] Ambiguity detected. TENDING for internal reasoning/clarification.")
        else: # Ambiguous and low mood, or very low clarity
            decision = REFRAIN
            print(f"[{self.name}] Low clarity/mood. REFRAINING from action.")

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
        Executes the action, with specific logging for risk-driven actions.
        """
        super().execute_action(action) # Call parent method for general mood/cognition updates

        if action == AFFIRM:
            if self.risk_score >= self.risk_threshold_for_override:
                print(f"[{self.name}] ACTION: Proceeding under high TEMPRA Risk, despite clarity concerns!")
            else:
                print(f"[{self.name}] ACTION: Proceeding with task.")
        elif action == TEND:
            print(f"[{self.name}] TENDING: Observing further, adjusting, or waiting.")
        elif action == REFRAIN:
            print(f"[{self.name}] REFRAIN: Halting due to uncertainty.")
        else:
            print(f"[{self.name}] WARNING: Unknown action state received: {action}")

    def run_cycle(self, input_data, collective_state=None, supervisor_directive=None):
        """
        Performs a full Ternlang cycle for a TEMPRAAgent.
        """
        print(f"\n--- [{self.name}] Starting New Cycle ---")
        current_context, relevance_score = self.observe(input_data, collective_state)
        decision = self.decide(relevance_score, supervisor_directive)
        self.execute_action(decision)

        # Log to memory
        self.memory.append({
            "timestamp": datetime.datetime.now().isoformat(),
            "input": input_data,
            "context": current_context,
            "decision": decision,
            "mood": self.mood,
            "cognition": self.cognition,
            "threat": self.threat,
            "exposure": self.exposure,
            "mitigation": self.mitigation,
            "probability": self.probability,
            "risk_score": self.risk_score
        })

        print(f"--- [{self.name}] Cycle Complete ---")
        return decision


# --- Simulation ---
def simulate_tempra_agent(num_cycles=8):
    """
    Runs a simulation of a TEMPRAAgent over multiple cycles.
    """
    print("\n--- Ternlang TEMPRA Override Agent Simulation Started ---")
    
    tempra_agent = TEMPRAAgent(name="RiskAssessor", initial_clarity=0.5)

    # Example inputs designed to trigger various TEMPRA scenarios
    scenarios = [
        "Input: Routine system check. All seems normal. (Low Risk)",
        "Input: Vague threat detected. Needs investigation. (Moderate Risk)",
        "Input: Critical system failure imminent! Immediate action required! (HIGH RISK, low clarity)",
        "Input: Ambiguous data, but a clear, urgent command received. (High Risk, low clarity)",
        "Input: Low priority task. No rush. (Low Risk)",
        "Input: Unclear warning, but critical infrastructure is at risk and highly exposed. (CRITICAL RISK, low clarity)",
        "Input: All clear. System stable. Proceed with next steps. (Low Risk, high clarity)",
        "Input: Emergency broadcast: Evacuate now! Catastrophic event imminent, unmitigated! (EXTREME RISK, high clarity)"
    ]

    for i, scenario_input in enumerate(scenarios):
        print(f"\n===== SIMULATION CYCLE {i+1}/{num_cycles} =====")
        tempra_agent.run_cycle(scenario_input)
        time.sleep(1.5) # Pause for readability

    print("\n--- Ternlang TEMPRA Override Agent Simulation Finished ---")

    # Optional: Print final state and memory
    print("\n--- Final Agent State ---")
    print(f"[{tempra_agent.name}] Final Mood: {tempra_agent.mood}, Cognition: {tempra_agent.cognition}, Clarity: {tempra_agent.clarity_score:.2f}, Risk: {tempra_agent.risk_score:.2f}, Last Action: {tempra_agent._get_state_name(tempra_agent.last_action)}")
    print(f"[{tempra_agent.name}] Final TEMPRA: T:{tempra_agent.threat:.2f}, E:{tempra_agent.exposure:.2f}, M:{tempra_agent.mitigation:.2f}, P:{tempra_agent.probability:.2f}")

    # You could also print memory snapshots here if desired
