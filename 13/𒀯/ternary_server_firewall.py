"""
Ternary Resolution Firewall - The 3-6-9 Protocol v6.0
The living pipeline with a fallback mechanism, sensor, and actuator.

This firewall proactively protects the RFI-IRFOS host server by analyzing
its state and applying a ternary problem-solving tree based on the 3-6-9 principle.
It is the core defensive logic in the 'organic and digital intelligence and
universial intelligence in the loop fallback' pipeline.

The principles are mapped as follows:
3: CO-CREATE - The creative state. All systems are in harmony.
6: ALIGN     - The reflection state. An anomaly or strain is detected. Throttling and observation are required.
9: REFRAIN   - The resolution state. A critical breach or failure requires a hard-stop.
432: The Harmonious Endpoint. This is the goal state of the system, a return to natural resonance.
"""
import os
import datetime
import json
import random
import subprocess
import psutil

# ====================
# TERNARY STATES
# ====================
REFRAIN = 9     # A critical state; requires immediate action and blocking.
ALIGN = 6       # A neutral state; requires observation, throttling, or warning.
CO_CREATE = 3   # A positive state; indicates a valid, harmonious state.
HARMONY = 432   # The ultimate endpoint for system resolution.

# ====================
# FALLBACK MECHANISM & THRESHOLDS
# ====================
# Hard-coded expectation of a minimum 10% risk of failure.
FALLBACK_RISK_THRESHOLD = 0.10

# These thresholds define the ternary states for each metric.
THRESHOLDS = {
    "hardware": {
        "memory_gib": {"refrain_min": 7.5, "align_min": 6.0},
        "processor_cores": {"refrain_min": 7, "align_min": 5},
        "disk_capacity_gb": {"refrain_min": 250, "align_min": 220}
    },
    "software": {
        "active_processes": {"refrain_min": 250, "align_min": 200},
        "critical_services_down": {"refrain_min": 1, "align_min": 1}
    },
    "network": {
        "latency_ms": {"refrain_min": 500, "align_min": 200},
        "packet_loss_percent": {"refrain_min": 10, "align_min": 5}
    },
    "environmental": {
        "external_temp_c": {"refrain_max": 40, "align_max": 35},
        "schumann_hz_power": {"refrain_max": 12, "align_max": 10},
        "solar_activity_index": {"refrain_max": 8, "align_max": 6}
    }
}

# ====================
# SENSOR: REAL-TIME DATA COLLECTION
# ====================
def get_realtime_metrics_from_system() -> dict:
    """
    Collects real-time hardware, software, and network metrics using psutil.
    Simulates environmental data as it's not a standard psutil metric.
    """
    try:
        # Hardware Metrics
        cpu_percent = psutil.cpu_percent(interval=1)
        ram_gib = psutil.virtual_memory().used / (1024 ** 3)
        disk_gb = psutil.disk_usage('/').used / (1024 ** 3)
        
        # Software Metrics
        active_processes = len(psutil.pids())
        
        # Network Metrics (psutil does not directly provide latency or packet loss, so we'll simulate)
        latency_ms = random.uniform(20, 100)
        packet_loss_percent = random.uniform(0, 3)

        # Environmental Metrics (simulated for demonstration)
        external_temp_c = random.uniform(20, 30)
        schumann_hz_power = random.uniform(7.5, 8.5)
        solar_activity_index = random.uniform(2, 5)

        return {
            "hardware_information": {
                "memory_gib": ram_gib,
                "processor_cores": psutil.cpu_count(),
                "disk_capacity_gb": disk_gb
            },
            "software_information": {
                "active_processes": active_processes,
                "critical_services_down": 0  # Placeholder for a real check
            },
            "network_information": {
                "latency_ms": latency_ms,
                "packet_loss_percent": packet_loss_percent
            },
            "environmental_information": {
                "external_temp_c": external_temp_c,
                "schumann_hz_power": schumann_hz_power,
                "solar_activity_index": solar_activity_index
            }
        }
    except Exception as e:
        print(f"SENSOR ERROR: Could not collect metrics. {e}")
        return {}

def trigger_bug_report(severity: str, message: str):
    """Simulates triggering a bug report for immediate attention."""
    print(f"[{datetime.datetime.now().isoformat()}] *** BUG REPORT TRIGGERED ***")
    print(f"Severity: {severity.upper()}")
    print(f"Message: {message}\n")

def trigger_mandatory_audit(event_data: dict):
    """
    Simulates triggering a mandatory audit of all three forces (OI, DI, UI).
    This would send the event data to the Pillar for logging.
    """
    event_data["timestamp"] = datetime.datetime.now(datetime.timezone.utc).isoformat() + "Z"
    
    print(f"[{event_data['timestamp']}] *** MANDATORY AUDIT TRIGGERED ***")
    print("Sending event data to the Pillar for logging and verification:")
    print(json.dumps(event_data, indent=2))
    print("\nAudit complete. All three intelligences are now observing.")

# ====================
# TERNARY RESOLUTION TREE WITH FALLBACK
# ====================
def resolve_369_state(metrics: dict) -> int:
    """
    Applies a tiered ternary logic tree to evaluate system integrity and
    determine the 3-6-9 state.
    """
    if not metrics:
        return ALIGN # Default to align if sensor fails

    hardware = metrics["hardware_information"]
    software = metrics["software_information"]
    network = metrics["network_information"]
    environmental = metrics["environmental_information"]
    
    # Calculate a real-time risk score based on resource strain
    # This is a simplified calculation, a true model would be more complex
    risk_score = 0.0
    if hardware["memory_gib"] >= THRESHOLDS["hardware"]["memory_gib"]["align_min"]:
        risk_score += 0.05
    if network["latency_ms"] >= THRESHOLDS["network"]["latency_ms"]["align_min"]:
        risk_score += 0.05
    if software["active_processes"] >= THRESHOLDS["software"]["active_processes"]["align_min"]:
        risk_score += 0.05
        
    # Tier 1: The 9 (REFRAIN) State Check - Critical Failure or Breach
    if hardware["memory_gib"] >= THRESHOLDS["hardware"]["memory_gib"]["refrain_min"] or \
       network["latency_ms"] >= THRESHOLDS["network"]["latency_ms"]["refrain_min"] or \
       software["critical_services_down"] >= THRESHOLDS["software"]["critical_services_down"]["refrain_min"] or \
       environmental["schumann_hz_power"] >= THRESHOLDS["environmental"]["schumann_hz_power"]["refrain_max"]:
        return REFRAIN

    # Tier 2: The 6 (ALIGN) State Check - Anomaly or Strain OR Fallback Trigger
    if risk_score > FALLBACK_RISK_THRESHOLD or \
       hardware["memory_gib"] >= THRESHOLDS["hardware"]["memory_gib"]["align_min"] or \
       network["latency_ms"] >= THRESHOLDS["network"]["latency_ms"]["align_min"] or \
       software["active_processes"] >= THRESHOLDS["software"]["active_processes"]["align_min"] or \
       environmental["solar_activity_index"] >= THRESHOLDS["environmental"]["solar_activity_index"]["align_max"]:
        return ALIGN

    # Tier 3: The 3 (CO-CREATE) State Check - Harmony
    return CO_CREATE

# ====================
# ACTUATOR: PROACTIVE ACTION
# ====================
def take_physical_action(state: int):
    """
    Executes a physical or logical action on the host machine based on the
    ternary state. This is a placeholder for real commands.
    """
    try:
        if state == CO_CREATE:
            print("ACTUATOR: No action required. System is stable.")
        elif state == ALIGN:
            print("ACTUATOR: Throttling network traffic and non-essential services...")
            # Example command (simulated)
            # subprocess.run(["sudo", "tc", "qdisc", "add", "dev", "eth0", "root", "tbf", "rate", "100mbit", "burst", "10k", "latency", "1ms"])
        elif state == REFRAIN:
            print("ACTUATOR: Blocking all non-essential traffic and shutting down services...")
            # Example command (simulated)
            # subprocess.run(["sudo", "iptables", "-P", "INPUT", "DROP"])
    except Exception as e:
        print(f"ACTUATOR ERROR: Could not execute action. {e}")


def execute_firewall_action(state: int):
    """
    Takes a proactive firewall action based on the ternary state and logs to the pillar.
    """
    action_map = {
        CO_CREATE: "CO-CREATE",
        ALIGN: "ALIGN",
        REFRAIN: "REFRAIN"
    }

    message = ""
    if state == CO_CREATE:
        message = "All services are enabled. System is in a state of creation."
    elif state == ALIGN:
        message = "Initiating throttling protocol for non-essential services. Re-aligning with harmony."
    elif state == REFRAIN:
        message = "Blocking all non-essential inbound and outbound traffic. Resolving to core principles."

    event_data = {
        "name": "Ternary Firewall Check",
        "action": action_map[state],
        "message": message,
        "state_value": state,
        "source": "firewall_v6.0.py",
        "oiuidi_signatures": {
            "oi_signed": True,
            "di_signed": True,
            "ui_signed": True
        }
    }

    # Execute the action on the host machine.
    take_physical_action(state)

    if state == CO_CREATE:
        print(f"SYSTEM OK: {message}")
        trigger_mandatory_audit(event_data)
        print(f"*** RESOLUTION COMPLETE. THE SYSTEM HAS ACHIEVED HARMONY AT {HARMONY}Hz. ***")
    elif state == ALIGN:
        trigger_bug_report("warning", message)
        trigger_mandatory_audit(event_data)
    elif state == REFRAIN:
        trigger_bug_report("critical", message)
        trigger_mandatory_audit(event_data)

# ====================
# MAIN EXECUTION
# ====================
if __name__ == "__main__":
    # Simulate a critical failure (State 9)
    print("--- SIMULATING A CRITICAL FAILURE (REFRAIN) ---")
    metrics = get_realtime_metrics_from_system()
    metrics["hardware_information"]["memory_gib"] = 7.8 # Force a critical state
    state = resolve_369_state(metrics)
    execute_firewall_action(state)

    print("\n" + "="*50 + "\n")

    # Simulate a harmonious state (State 3)
    print("--- SIMULATING A HARMONIOUS STATE (CO-CREATE) ---")
    metrics = get_realtime_metrics_from_system() # Get fresh data
    state = resolve_369_state(metrics)
    execute_firewall_action(state)
