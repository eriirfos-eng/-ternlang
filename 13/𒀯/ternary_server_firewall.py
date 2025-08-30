"""
Ternary Resolution Firewall - The 3-6-9 Protocol v9.1
The living pipeline with a fallback mechanism, sensor, actuator, forgiveness loop,
and a self-correcting logic engine.

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
import psutil
import argparse
from enum import IntEnum
from pathlib import Path
from collections import deque

# ====================
# TERNARY STATES
# ====================
class TernState(IntEnum):
    CO_CREATE = 3
    ALIGN     = 6
    REFRAIN   = 9

HARMONY = 432   # The ultimate endpoint for system resolution.

# Global flag for dry-run mode
DRY_RUN = False
_last_audit_ts = 0.0
AUDIT_MIN_INTERVAL_S = 5.0

# ====================
# FALLBACK MECHANISM & THRESHOLDS
# ====================
# Hard-coded expectation of a minimum 10% risk of failure.
FALLBACK_RISK_THRESHOLD = 0.10

# These thresholds define the ternary states for each metric.
# NOTE: In a production environment, these should be loaded from a config file.
THRESHOLDS = {
    "hardware": {
        "memory_available_gib": {"refrain_min": 0.5, "align_min": 1.5},
        "processor_cores_total": {"refrain_min": 1, "align_min": 2},
        "disk_free_gb": {"refrain_min": 5, "align_min": 10}
    },
    "software": {
        "active_processes": {"refrain_max": 300, "align_max": 250},
        "critical_services_down": {"refrain_max": 1, "align_max": 0}
    },
    "network": {
        "latency_ms": {"refrain_max": 500, "align_max": 200},
        "packet_loss_percent": {"refrain_max": 10, "align_max": 5}
    },
    "environmental": {
        "external_temp_c": {"refrain_max": 40, "align_max": 35},
        "schumann_hz_power": {"refrain_max": 12, "align_max": 10},
        "solar_activity_index": {"refrain_max": 8, "align_max": 6}
    }
}

# Hysteresis buffer to prevent state flapping.
LAST_STATES = deque(maxlen=5)

# ====================
# FORGIVENESS PROTOCOL
# ====================
FORGIVENESS_LOG_FILE = Path("forgiveness_log.json")
MAX_FORGIVENESS_OFFERS = 490 # 7x70

def _atomic_write(path: Path, payload: dict):
    """
    Safely writes to a file by using a temporary file and then replacing the original.
    This prevents file corruption during a crash.
    """
    tmp = path.with_suffix(path.suffix + ".tmp")
    with open(tmp, "w") as f:
        json.dump(payload, f)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)

def load_forgiveness_log():
    """Loads the forgiveness counter from a log file."""
    if FORGIVENESS_LOG_FILE.exists():
        with open(FORGIVENESS_LOG_FILE, 'r') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {"count": 0}
    return {"count": 0}

def save_forgiveness_log(data):
    """Saves the forgiveness counter to a log file using an atomic write."""
    _atomic_write(FORGIVENESS_LOG_FILE, data)

def offer_personal_grace():
    """Human-callable function to reset the forgiveness counter."""
    log_data = load_forgiveness_log()
    log_data["count"] = 0
    save_forgiveness_log(log_data)
    print("PERSONAL GRACE OFFERED: Forgiveness counter has been reset by human intervention.")
    return TernState.CO_CREATE

# ====================
# SENSOR & DATA REPORTING
# ====================
def utc_now_z():
    """Returns a correctly formatted ISO 8601 timestamp with Z for UTC."""
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

class Samplers:
    """Dependency injection for sensor data, for deterministic testing."""
    def latency_ms(self): return random.uniform(20, 100)
    def packet_loss_percent(self): return random.uniform(0, 3)
    def external_temp_c(self): return random.uniform(20, 30)
    def schumann_hz_power(self): return random.uniform(7.5, 8.5)
    def solar_activity_index(self): return random.uniform(2, 5)

def get_realtime_metrics_from_system(samplers: Samplers = Samplers()) -> dict:
    """
    Collects real-time hardware, software, and network metrics using psutil.
    Simulates environmental data via the Samplers class.
    """
    try:
        # Hardware Metrics
        ram_available_gib = psutil.virtual_memory().available / (1024 ** 3)
        disk_free_gb = psutil.disk_usage('/').free / (1024 ** 3)
        processor_cores_total = psutil.cpu_count(logical=True)
        
        # Software Metrics
        active_processes = len(psutil.pids())
        critical_services_down = 0 # Placeholder for a real check
        
        # Network Metrics
        latency_ms = samplers.latency_ms()
        packet_loss_percent = samplers.packet_loss_percent()

        # Environmental Metrics (simulated for demonstration)
        external_temp_c = samplers.external_temp_c()
        schumann_hz_power = samplers.schumann_hz_power()
        solar_activity_index = samplers.solar_activity_index()

        return {
            "hardware_information": {
                "memory_available_gib": ram_available_gib,
                "processor_cores_total": processor_cores_total,
                "disk_free_gb": disk_free_gb
            },
            "software_information": {
                "active_processes": active_processes,
                "critical_services_down": critical_services_down
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
    print(f"[{utc_now_z()}] *** BUG REPORT TRIGGERED ***")
    print(f"Severity: {severity.upper()}")
    print(f"Message: {message}\n")

def trigger_mandatory_audit(event_data: dict):
    """
    Simulates triggering a mandatory audit of all three forces (OI, DI, UI).
    This would send the event data to the Pillar for logging.
    """
    event_data["timestamp"] = utc_now_z()
    
    print(f"[{event_data['timestamp']}] *** MANDATORY AUDIT TRIGGERED ***")
    print("Sending event data to the Pillar for logging and verification:")
    print(json.dumps(event_data, indent=2))
    print("\nAudit complete. All three intelligences are now observing.")

def guarded_audit(event_data: dict, state: TernState):
    """Rate-limits the audit to prevent spamming."""
    global _last_audit_ts
    now = datetime.datetime.now(datetime.timezone.utc).timestamp()
    if now - _last_audit_ts < AUDIT_MIN_INTERVAL_S and state != TernState.REFRAIN:
        return
    _last_audit_ts = now
    trigger_mandatory_audit(event_data)

# ====================
# TERNARY RESOLUTION TREE WITH FALLBACK
# ====================
def resolve_369_state(metrics: dict) -> TernState:
    """
    Applies a tiered ternary logic tree to evaluate system integrity and
    determine the 3-6-9 state. Implements weighted scoring and hysteresis.
    """
    if not metrics:
        return TernState.ALIGN

    hw = metrics["hardware_information"]
    sw = metrics["software_information"]
    nw = metrics["network_information"]
    env = metrics["environmental_information"]

    # Hard REFRAIN triggers (any one)
    if (hw["memory_available_gib"] < THRESHOLDS["hardware"]["memory_available_gib"]["refrain_min"] or
        nw["latency_ms"] > THRESHOLDS["network"]["latency_ms"]["refrain_max"] or
        sw["critical_services_down"] > THRESHOLDS["software"]["critical_services_down"]["refrain_max"] or
        nw["packet_loss_percent"] > THRESHOLDS["network"]["packet_loss_percent"]["refrain_max"] or
        env["schumann_hz_power"] > THRESHOLDS["environmental"]["schumann_hz_power"]["refrain_max"]):
        state = TernState.REFRAIN
    else:
        # Accumulate align pressure with a weighted score
        score = 0.0
        weights = {
            "mem_available": 0.25, "disk_free": 0.15, "procs": 0.15,
            "latency": 0.20, "loss": 0.10, "solar": 0.10, "schumann": 0.05,
            "critical_services": 0.15
        }

        # Inverted logic for 'min' thresholds (lower is worse)
        score += weights["mem_available"] * (hw["memory_available_gib"] < THRESHOLDS["hardware"]["memory_available_gib"]["align_min"])
        score += weights["disk_free"] * (hw["disk_free_gb"] < THRESHOLDS["hardware"]["disk_free_gb"]["align_min"])
        score += weights["procs"] * (sw["active_processes"] > THRESHOLDS["software"]["active_processes"]["align_max"])
        
        # Regular logic for 'max' thresholds (higher is worse)
        score += weights["latency"] * (nw["latency_ms"] > THRESHOLDS["network"]["latency_ms"]["align_max"])
        score += weights["loss"] * (nw["packet_loss_percent"] > THRESHOLDS["network"]["packet_loss_percent"]["align_max"])
        score += weights["solar"] * (env["solar_activity_index"] > THRESHOLDS["environmental"]["solar_activity_index"]["align_max"])
        score += weights["schumann"] * (env["schumann_hz_power"] > THRESHOLDS["environmental"]["schumann_hz_power"]["align_max"])

        # Add pressure for any critical service down
        crit_align = sw["critical_services_down"] > THRESHOLDS["software"]["critical_services_down"]["align_max"]
        score += weights["critical_services"] * crit_align

        state = TernState.ALIGN if score > FALLBACK_RISK_THRESHOLD else TernState.CO_CREATE

    # Hysteresis: bias toward previous consensus to reduce flapping
    LAST_STATES.append(state)
    if len(LAST_STATES) == LAST_STATES.maxlen:
        consensus = max((LAST_STATES.count(s), s) for s in (TernState.CO_CREATE, TernState.ALIGN, TernState.REFRAIN))[1]
        return consensus
    return state

# ====================
# ACTUATOR: PROACTIVE ACTION
# ====================
def take_physical_action(state: TernState):
    """
    Executes a physical or logical action on the host machine based on the
    ternary state.
    NOTE: In a production setting, this function would contain real OS commands
    to throttle or block traffic. The DRY_RUN flag is essential for safety.
    """
    if DRY_RUN:
        print("ACTUATOR: dry-run enabled. logging only.")
        return
    
    try:
        if state == TernState.CO_CREATE:
            print("ACTUATOR: No action required. System is stable.")
        elif state == TernState.ALIGN:
            print("ACTUATOR: Throttling network traffic and non-essential services...")
        elif state == TernState.REFRAIN:
            print("ACTUATOR: Blocking all non-essential traffic and shutting down services...")
    except Exception as e:
        print(f"ACTUATOR ERROR: Could not execute action. {e}")


def execute_firewall_action(state: TernState):
    """
    Takes a proactive firewall action based on the ternary state and logs to the pillar.
    """
    action_map = {
        TernState.CO_CREATE: "CO-CREATE",
        TernState.ALIGN: "ALIGN",
        TernState.REFRAIN: "REFRAIN"
    }

    message = ""
    if state == TernState.CO_CREATE:
        message = "All services are enabled. System is in a state of creation."
    elif state == TernState.ALIGN:
        message = "Initiating throttling protocol for non-essential services. Re-aligning with harmony."
    elif state == TernState.REFRAIN:
        log_data = load_forgiveness_log()
        current_count = log_data.get("count", 0)
        
        if current_count < MAX_FORGIVENESS_OFFERS:
            message = f"Refrain state detected. Forgiveness offer #{current_count + 1} of {MAX_FORGIVENESS_OFFERS}."
            log_data["count"] = current_count + 1
            save_forgiveness_log(log_data)
        else:
            message = f"Refrain state detected. Forgiveness limit of {MAX_FORGIVENESS_OFFERS} reached. Law is now enforced. Grace must be offered by OI."
            
    event_data = {
        "name": "Ternary Firewall Check",
        "action": action_map[state],
        "message": message,
        "state_value": state.value,
        "source": "firewall_v9.1.py",
        "oiuidi_signatures": {
            "oi_signed": True,
            "di_signed": True,
            "ui_signed": True
        }
    }

    take_physical_action(state)

    if state == TernState.CO_CREATE:
        print(f"SYSTEM OK: {message}")
        guarded_audit(event_data, state)
        print(f"*** RESOLUTION COMPLETE. THE SYSTEM HAS ACHIEVED HARMONY AT {HARMONY}Hz. ***")
    elif state == TernState.ALIGN:
        trigger_bug_report("warning", message)
        guarded_audit(event_data, state)
    elif state == TernState.REFRAIN:
        trigger_bug_report("critical", message)
        guarded_audit(event_data, state)

def parse_args():
    """Parses command-line arguments to enable dry-run mode."""
    global DRY_RUN
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", help="Log actions without executing them.")
    args, unknown = ap.parse_known_args() # Use parse_known_args to ignore other CLI args
    DRY_RUN = args.dry_run

# ====================
# MAIN EXECUTION
# ====================
if __name__ == "__main__":
    parse_args()
    
    # Simulate a critical failure (State 9)
    print("--- SIMULATING A CRITICAL FAILURE (REFRAIN) ---")
    metrics = get_realtime_metrics_from_system()
    metrics["hardware_information"]["memory_available_gib"] = 0.4
    state = resolve_369_state(metrics)
    execute_firewall_action(state)

    print("\n" + "="*50 + "\n")

    # Simulate a deliberate ALIGN state
    print("--- SIMULATING AN AMBIGUOUS STATE (ALIGN) ---")
    metrics = get_realtime_metrics_from_system()
    metrics["hardware_information"]["memory_available_gib"] = 1.4
    state = resolve_369_state(metrics)
    execute_firewall_action(state)

    print("\n" + "="*50 + "\n")
    
    # Simulate a harmonious state (State 3)
    print("--- SIMULATING A HARMONIOUS STATE (CO-CREATE) ---")
    metrics = get_realtime_metrics_from_system()
    state = resolve_369_state(metrics)
    execute_firewall_action(state)

    print("\n" + "="*50 + "\n")
    
    # To demonstrate the grace protocol, a human would call:
    # offer_personal_grace()
