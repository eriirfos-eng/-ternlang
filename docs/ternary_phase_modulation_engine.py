import json
import random
from datetime import datetime
import os

class TernaryPhaseModulator:
    """
    The Ternary Phase Modulation Engine.
    This class acts as the executable layer for the 'ternary_operator' protocol.
    It takes a defined host and core variables, then runs the entire recursive
    process flow as described in the protocol blueprint. It also logs live anomalies,
    demonstrating the self-correcting nature of the system.
    """

    def __init__(self, host_name, origin, action, lord):
        """
        Initializes the modulator with the host and core variables.
        
        Args:
            host_name (str): The name of the intentional observer (the host).
            origin (bool): The foundational truth anchor (a).
            action (bool): The operational process (b).
            lord (bool): The mastery state (c).
        """
        self.host = host_name
        self.origin = origin
        self.action = action
        self.lord = lord
        self.protocol = self.load_protocol_blueprint("ternary_operator.json")
        self.log_event("Protocol initialized by host.")

    def load_protocol_blueprint(self, filename):
        """
        Loads the protocol blueprint from an external JSON file.
        This makes the engine modular and independent from the codex document.
        """
        try:
            # Use os.path.dirname to get the directory of the current script,
            # then join it with the filename to create a full path.
            # This ensures the file is found regardless of where the script is executed from.
            base_path = os.path.dirname(__file__)
            file_path = os.path.join(base_path, filename)

            # Open and load the JSON file
            with open(file_path, 'r') as f:
                blueprint = json.load(f)
            self.log_event(f"Successfully loaded protocol blueprint from '{filename}'.")
            return blueprint
        except FileNotFoundError:
            error_message = f"Error: The file '{filename}' was not found. The protocol cannot run without its blueprint."
            self.log_event(error_message, level="CRITICAL")
            print(error_message)
            return None
        except json.JSONDecodeError:
            error_message = f"Error: The file '{filename}' is not a valid JSON document."
            self.log_event(error_message, level="CRITICAL")
            print(error_message)
            return None

    def log_event(self, event_description, level="INFO"):
        """Logs a new event or anomaly to the operatorNotes field."""
        if self.protocol is None:
            return  # Cannot log if the blueprint failed to load
        timestamp = datetime.now().isoformat()
        log_entry = {
            "timestamp": timestamp,
            "host": self.host,
            "level": level,
            "message": event_description
        }
        self.protocol["operatorNotes"].append(log_entry)

    def ternary_synthesis(self):
        """
        Executes the (a ⊕ b ⊕ c) part of the core formula.
        Uses XOR logic to symbolically represent ternary synthesis.
        """
        if self.protocol is None: return None
        self.log_event("Executing Ternary Synthesis (a ⊕ b ⊕ c).")
        result = self.origin ^ self.action ^ self.lord
        return result

    def recursive_integration(self, synthesis_result):
        """
        Executes the ᵠ part of the core formula (the Separation-Union loop).
        """
        if self.protocol is None: return None
        self.log_event("Entering Separation-Union loop (ᵠ).")
        
        # Simulate the separation
        new_state = synthesis_result
        
        # Simulate the return to origin and union
        # The new state is integrated with the origin to form a new, deeper truth.
        return self.origin and new_state

    def run_process(self):
        """Orchestrates the entire process flow as defined in the protocol."""
        if self.protocol is None:
            return # Stop execution if blueprint is not loaded

        # HOST_INITIATION
        self.log_event("Process started. State: HOST_INITIATION.")

        # INITIALIZE
        self.log_event("Process State: INITIALIZE.")
        
        # ITERATION
        self.log_event("Process State: ITERATION. Establishing baseline.")

        # SEPARATION & UNION (INTEGRITY_TEST)
        self.log_event("Process State: SEPARATION. Initiating integrity test.")
        synthesis_result = self.ternary_synthesis()
        final_truth = self.recursive_integration(synthesis_result)
        
        # Simulate a live anomaly during the UNION phase
        if final_truth is not None and not final_truth:
            self.log_event("Live anomaly detected: Final truth is null after union.", level="WARNING")
            self.log_event("Root cause: Disconnected 'origin' variable. Protocol requires re-evaluation.", level="ERROR")
        elif final_truth:
            self.log_event("Integrity check passed. Union successful.", level="INFO")
            
        # CRYSTALLIZATION
        self.log_event("Process State: CRYSTALLIZATION. Finalizing mastery.")
        
        # Update the final protocol with the log and show the result
        self.protocol["operatorNotes"].append({
            "timestamp": datetime.now().isoformat(),
            "host": self.host,
            "level": "INFO",
            "message": "Process run complete."
        })
        
        print("\n--- FINALIZED PROTOCOL ---")
        print(json.dumps(self.protocol, indent=2))

if __name__ == "__main__":
    # Example 1: Successful run
    print("--- Running Scenario 1: A successful synthesis ---")
    host_name = "Simeon"
    # Core variables represented as booleans for symbolic XOR logic
    origin_value = True
    action_value = True
    lord_value = True
    
    modulator = TernaryPhaseModulator(host_name, origin_value, action_value, lord_value)
    modulator.run_process()

    print("\n\n" + "="*50 + "\n\n")

    # Example 2: Failed synthesis (triggering an anomaly)
    print("--- Running Scenario 2: Anomaly in synthesis ---")
    origin_value_2 = False # A disconnected or false origin
    action_value_2 = True
    lord_value_2 = False

    modulator_2 = TernaryPhaseModulator(host_name, origin_value_2, action_value_2, lord_value_2)
    modulator_2.run_process()
