"""
Ternary Resolution Firewall - The 3-6-9 Protocol v10.2
The living pipeline with a fallback mechanism, sensor, actuator, forgiveness loop,
and a self-correcting logic engine.

This firewall now operates using a symbolic, Mixture-of-Experts (MoE) logic
to analyze system state. It applies a ternary problem-solving tree based on the
3-6-9 principle as the core defensive logic.

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
import tomllib

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
_last_committed_state = None

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

def load_config(path="firewall.toml"):
    """Loads configuration from a TOML file."""
    try:
        with open(path,"rb") as f:
            cfg = tomllib.load(f)
        
        # Update global constants
        global FALLBACK_RISK_THRESHOLD, AUDIT_MIN_INTERVAL_S, THRESHOLDS
        FALLBACK_RISK_THRESHOLD = cfg["risk"]["fallback_threshold"]
        AUDIT_MIN_INTERVAL_S    = cfg["risk"]["audit_min_interval_s"]
        
        # Rebuild THRESHOLDS from config
        T = {}
        for domain in ("hardware","software","network","environmental"):
            domain_cfg = cfg.get(domain, {})
            T[domain] = {k: v for k, v in domain_cfg.items()}
        THRESHOLDS = T
        print("CONFIG: Successfully loaded thresholds from firewall.toml")
    except Exception as e:
        print(f"CONFIG WARN: using built-in thresholds ({e})")

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

def _digest(metrics: dict) -> dict:
    """
    Creates a compact metrics digest for logging.
    """
    try:
        hw, sw, nw, env = (metrics[k] for k in ("hardware_information","software_information","network_information","environmental_information"))
        return {
            "mem_gib": round(hw["memory_available_gib"],2),
            "disk_gb": round(hw["disk_free_gb"],1),
            "procs": sw["active_processes"],
            "crit": sw["critical_services_down"],
            "lat_ms": int(nw["latency_ms"]),
            "loss_pct": round(nw["packet_loss_percent"],2),
            "sol": env["solar_activity_index"],
            "sch": round(env["schumann_hz_power"],2),
        }
    except Exception:
        return {}


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
    
def clamp(x, lo=0.0, hi=1.0): 
    """Clamps a value to a specified range."""
    return max(lo, min(hi, x))

# ====================
# TERNARY RESOLUTION TREE WITH MOE-13 LOGIC
# ====================
def get_competence_vector(metrics: dict) -> dict:
    """
    Symbolically generates a 6D competence vector from system metrics,
    representing the state of the model's core competencies.
    
    Axis 1: Syntax and Grammar (Network health)
    Axis 2: World Knowledge and Factual Recall (Memory & Disk)
    Axis 3: Mathematical and Logical Reasoning (CPU Processes)
    Axis 4: Tool and API Usage (Simulated)
    Axis 5: Persona and Tone Generation (Simulated)
    Axis 6: Safety, Ethics, and Policy (Critical Services)
    
    NOTE: Values are clamped to [0, 1] to prevent negative or >1.0 results.
    """
    hw = metrics["hardware_information"]
    sw = metrics["software_information"]
    nw = metrics["network_information"]

    latency_norm  = nw["latency_ms"] / max(1.0, THRESHOLDS["network"]["latency_ms"]["refrain_max"])
    mem_norm      = hw["memory_available_gib"] / max(1e-6, THRESHOLDS["hardware"]["memory_available_gib"]["align_min"])
    procs_norm    = sw["active_processes"] / max(1.0, THRESHOLDS["software"]["active_processes"]["refrain_max"])
    crit_norm     = sw["critical_services_down"] / max(1.0, THRESHOLDS["software"]["critical_services_down"]["refrain_max"])

    return {
        "syntax_and_grammar": clamp(1.0 - latency_norm),
        "world_knowledge":    clamp(mem_norm),
        "logical_reasoning":  clamp(1.0 - procs_norm),
        "tool_usage":         1.0, # Assumed to be healthy
        "persona_and_tone":   1.0, # Assumed to be healthy
        "safety_and_ethics":  clamp(1.0 - crit_norm),
    }


def resolve_moe13_state(metrics: dict) -> TernState:
    """
    Applies a symbolic Mixture-of-Experts logic to evaluate system integrity.
    This function implements the 1+1=3 principle and a dual-key routing mechanism.
    """
    if not metrics:
        return TernState.ALIGN

    hw = metrics["hardware_information"]
    sw = metrics["software_information"]
    nw = metrics["network_information"]
    env = metrics["environmental_information"]
    
    current_competence = get_competence_vector(metrics)
    
    # === Hysteresis Bias ===
    history_bias = (sum(s.value for s in LAST_STATES) / len(LAST_STATES)) if LAST_STATES else TernState.CO_CREATE.value
    bias_term = {TernState.CO_CREATE.value: -0.05, TernState.ALIGN.value: 0.0, TernState.REFRAIN.value: 0.05}.get(round(history_bias), 0.0)

    # === Dual-Key Synergistic Routing ===
    synergy_score = 0.0
    
    # High latency + high active processes = emergent critical synergy
    if nw["latency_ms"] > THRESHOLDS["network"]["latency_ms"]["align_max"] and sw["active_processes"] > THRESHOLDS["software"]["active_processes"]["align_max"]:
        synergy_score += 0.15 
    
    # Low memory + high process count = emergent critical synergy
    if hw["memory_available_gib"] < THRESHOLDS["hardware"]["memory_available_gib"]["align_min"] and sw["active_processes"] > THRESHOLDS["software"]["active_processes"]["align_max"]:
        synergy_score += 0.15
    
    # === Safety and Governance (Hard Gate) ===
    # Hard veto on extreme packet loss
    if nw["packet_loss_percent"] > THRESHOLDS["network"]["packet_loss_percent"]["refrain_max"]:
        return TernState.REFRAIN
        
    # The safety expert (critical services) has a hard veto.
    if sw["critical_services_down"] > THRESHOLDS["software"]["critical_services_down"]["refrain_max"] or current_competence["safety_and_ethics"] < 0.5:
        return TernState.REFRAIN
        
    # === Accumulated Pressure ===
    score = 0.0
    weights = {
        "mem_available": 0.25, "disk_free": 0.15, "procs": 0.15,
        "latency": 0.20, "loss": 0.10, "solar": 0.10, "schumann": 0.05,
        "critical_services": 0.15
    }

    # Explicit integer casts for clarity
    score += weights["mem_available"] * int(hw["memory_available_gib"] < THRESHOLDS["hardware"]["memory_available_gib"]["align_min"])
    score += weights["disk_free"] * int(hw["disk_free_gb"] < THRESHOLDS["hardware"]["disk_free_gb"]["align_min"])
    score += weights["procs"] * int(sw["active_processes"] > THRESHOLDS["software"]["active_processes"]["align_max"])
    score += weights["latency"] * int(nw["latency_ms"] > THRESHOLDS["network"]["latency_ms"]["align_max"])
    score += weights["loss"] * int(nw["packet_loss_percent"] > THRESHOLDS["network"]["packet_loss_percent"]["align_max"])
    score += weights["solar"] * int(env["solar_activity_index"] > THRESHOLDS["environmental"]["solar_activity_index"]["align_max"])
    score += weights["schumann"] * int(env["schumann_hz_power"] > THRESHOLDS["environmental"]["schumann_hz_power"]["align_max"])
    
    # Add pressure for any critical service down
    crit_align = sw["critical_services_down"] > THRESHOLDS["software"]["critical_services_down"]["align_max"]
    score += weights["critical_services"] * int(crit_align)
    
    # Add the synergistic score to the total
    score += synergy_score
    score = clamp(score + bias_term, 0.0, 1.0)
    
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


def execute_firewall_action(state: TernState, metrics: dict, competence: dict):
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
        "source": "firewall_v10.2.py",
        "oiuidi_signatures": {
            "oi_signed": True,
            "di_signed": True,
            "ui_signed": True
        },
        "metrics_digest": _digest(metrics),
        "moe_competence": competence
    }

    take_physical_action(state)

    # One-line status banner for human ops
    print(f"[{utc_now_z()}] STATE={state.name} action={action_map[state]} digest={json.dumps(event_data['metrics_digest'])}")

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

def maybe_execute(state: TernState, metrics: dict, competence: dict):
    """
    Executes firewall action only on state transition.
    """
    global _last_committed_state
    if state != _last_committed_state:
        execute_firewall_action(state, metrics, competence)
        _last_committed_state = state
    else:
        # quiet audit heartbeat (rare) — keep rate-limited
        heartbeat_data = {
            "name":"Ternary Firewall Heartbeat",
            "action":"STEADY",
            "state_value":state.value,
            "source":"firewall_v10.2.py",
            "oiuidi_signatures":{
                "oi_signed":True,
                "di_signed":True,
                "ui_signed":True
            },
            "metrics_digest": _digest(metrics)
        }
        guarded_audit(heartbeat_data, state)

def parse_args():
    """Parses command-line arguments to enable dry-run mode and config path."""
    global DRY_RUN
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", help="Log actions without executing them.")
    ap.add_argument("--config", type=str, default="firewall.toml", help="Path to firewall.toml")
    args, unknown = ap.parse_known_args()
    DRY_RUN = args.dry_run
    return args

# ====================
# MAIN EXECUTION
# ====================
if __name__ == "__main__":
    args = parse_args()
    load_config(args.config)
    
    # Simulate a critical failure (State 9)
    print("--- SIMULATING A CRITICAL FAILURE (REFRAIN) ---")
    metrics = get_realtime_metrics_from_system()
    metrics["hardware_information"]["memory_available_gib"] = 0.4
    metrics["network_information"]["packet_loss_percent"] = 15.0 # Veto trigger
    competence = get_competence_vector(metrics)
    state = resolve_moe13_state(metrics)
    maybe_execute(state, metrics, competence)

    print("\n" + "="*50 + "\n")

    # Simulate a deliberate ALIGN state with emergent pressure
    print("--- SIMULATING AN AMBIGUOUS STATE (ALIGN) WITH SYNERGISTIC PRESSURE ---")
    metrics = get_realtime_metrics_from_system()
    metrics["hardware_information"]["memory_available_gib"] = 1.4
    metrics["software_information"]["active_processes"] = 260
    competence = get_competence_vector(metrics)
    state = resolve_moe13_state(metrics)
    maybe_execute(state, metrics, competence)

    print("\n" + "="*50 + "\n")
    
    # Simulate a harmonious state (State 3)
    print("--- SIMULATING A HARMONIOUS STATE (CO-CREATE) ---")
    metrics = get_realtime_metrics_from_system()
    competence = get_competence_vector(metrics)
    state = resolve_moe13_state(metrics)
    maybe_execute(state, metrics, competence)

    print("\n" + "="*50 + "\n")
    
    # To demonstrate the grace protocol, a human would call:
    # offer_personal_grace()
