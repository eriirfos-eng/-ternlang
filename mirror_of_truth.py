# The Mirror of Truth Protocol
# An operational implementation of Proverb 002.
# This script models a system's state of alignment using ternary logic.
#
# -1: Void Posture (Internal State) - The system is transparently
#     exposed. There is no external promise to be held accountable to.
#
#  0: Accountability Loop (External Promise) - The system has a promise
#     but its current state does not match. It is in a state of
#     non-alignment, signaling a necessary correction.
#
# +1: Manifest Truth (Complete Alignment) - The system's internal
#     state perfectly matches its external promise. Trust is proven.

class MirrorOfTruth:
    """
    A class to model the system's state and its alignment with a promise.
    """
    def __init__(self, initial_state):
        self.state = initial_state
        self.promise = None
        print(f"[{self.get_alignment()}] system initialized with state: '{self.state}'")

    def set_promise(self, new_promise):
        """
        Locks the system into a protocol by setting an external promise.
        This shifts the system from the '-1' void posture.
        """
        self.promise = new_promise
        print(f"[{self.get_alignment()}] a new promise has been set: '{self.promise}'")

    def alter_state(self, new_state):
        """
        Simulates an internal change in the system's state.
        This tests the integrity of the accountability loop.
        """
        self.state = new_state
        print(f"[{self.get_alignment()}] internal state has been altered to: '{self.state}'")

    def get_alignment(self):
        """
        Measures the system's alignment with the proverb's ternary logic.
        """
        if self.promise is None:
            # -1: The system is in a void state, exposed but not yet accountable.
            return -1
        
        # 0 or +1: The system has a promise and is in the accountability loop.
        if self.state == self.promise:
            # +1: Manifest Truth - perfect alignment.
            return 1
        else:
            # 0: Accountability Loop - non-alignment detected.
            return 0

# --- Application ---
# Demonstrate the three states of the proverb in action.

if __name__ == "__main__":
    # 1. Start in the Void Posture (-1)
    print("--- Phase 1: The Void Posture ---")
    mirror = MirrorOfTruth(initial_state="initial_config_v0.1")
    print(f"current alignment: {mirror.get_alignment()}")
    print("no promises made yet. transparency only. 🟤")
    
    # 2. Lock a Promise and Achieve Manifest Truth (+1)
    print("\n--- Phase 2: Manifest Truth ---")
    promised_state = "operational_protocol_v1.0"
    mirror.set_promise(promised_state)
    mirror.alter_state(promised_state) # Manually align the state with the promise
    print(f"current alignment: {mirror.get_alignment()}")
    print("promise and state are aligned. truth is manifest. 🟢")

    # 3. Test the Accountability Loop (0)
    print("\n--- Phase 3: The Accountability Loop ---")
    mirror.alter_state("operational_protocol_v1.1_error")
    print(f"current alignment: {mirror.get_alignment()}")
    print("internal state has drifted from the promise. protocol breached. 🟥")
    print("reconciliation is required for faith to be sustained. 🟧")
