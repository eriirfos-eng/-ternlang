"""
Ternary Resolution Firewall - The 3-6-9 Protocol v10.6.2 (Nexus)
The living pipeline for a distributed Mixture-of-Experts (MoE) system.

This firewall acts as a central nexus, coordinating a collection of external
agents or LLMs to evaluate system state. It no longer contains the expert
logic directly but synthesizes the collective competence of its distributed
endpoints.
"""
import os
import datetime
import json
import random
import time
from enum import IntEnum
from pathlib import Path
from collections import deque
import argparse
from threading import Lock
import hashlib
import sys
import asyncio
import httpx # Use httpx for async http requests
import hmac, base64
import uuid

# --- TOML compatibility guard for Python < 3.11 ---
try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib

# --- psutil compatibility guard for minimal hosts ---
try:
    import psutil
except Exception:
    psutil = None

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
_state_lock = Lock()
CONFIG_PATH = None
CONFIG_SHA256 = None
AGENTS = {}
AGENT_SECRETS = {}

# Define the three core parties and map agents to them
# This is a critical new rule: a decision must have at least one expert from each party
AGENT_PARTIES = {
    "universia": ["environmental"], # Pertains to cosmos, environment, external signals
    "digital": ["network", "security"],    # Pertains to software, network, logic
    "organic": ["hardware"]       # Pertains to physical systems, user hardware
}

# New centralized mapping for robust party detection
AGENT_PREFIX_TO_PARTY = {
    "environmental": "universia",
    "network": "digital",
    "security": "digital",
    "hardware": "organic",
}

def _party_for_agent(agent_name: str) -> str | None:
    """Returns the party name for a given agent name, or None if unknown."""
    prefix = (agent_name or "").split("_", 1)[0]
    return AGENT_PREFIX_TO_PARTY.get(prefix)


# ====================
# FALLBACK MECHANISM & THRESHOLDS
# ====================
FALLBACK_RISK_THRESHOLD = 0.10

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
LAST_STATES = deque(maxlen=5)

def _require(d, path):
    """Recursively validates the presence of a key path in a dictionary."""
    cur = d
    for k in path.split("."):
        if k not in cur:
            raise KeyError(f"missing config: {path}")
        cur = cur[k]
    return cur

def _sha256(path):
    """Generates a SHA256 hash of a file."""
    try:
        with open(path,"rb") as f: 
            return hashlib.sha256(f.read()).hexdigest()
    except Exception:
        return None

def _tighten_perms(path: Path):
    """Sets file permissions to owner read/write only."""
    try: 
        os.chmod(path, 0o600)
    except Exception: 
        pass

def _sig(name: str, body: bytes) -> str:
    """Generates an HMAC signature for a request body."""
    key = AGENT_SECRETS.get(name)
    if not key:
        return ""
    # The user suggested removing base64, but it is required for b16encode
    return base64.b16encode(hmac.new(key.encode(), body, digestmod="sha256").digest()).decode()

def load_config(path="firewall.toml"):
    """Loads and validates configuration from a TOML file."""
    global CONFIG_PATH, CONFIG_SHA256, AGENTS, AGENT_SECRETS
    CONFIG_PATH = path
    
    try:
        with open(path,"rb") as f:
            cfg = tomllib.load(f)
        
        try:
            st = os.stat(path)
            if (st.st_mode & 0o022):
                print(f"CONFIG WARN: {path} is group/other writable")
        except Exception:
            pass

        _require(cfg, "risk.fallback_threshold")
        _require(cfg, "risk.audit_min_interval_s")
        _require(cfg, "agents")

        global FALLBACK_RISK_THRESHOLD, AUDIT_MIN_INTERVAL_S, THRESHOLDS
        FALLBACK_RISK_THRESHOLD = cfg["risk"]["fallback_threshold"]
        AUDIT_MIN_INTERVAL_S    = cfg["risk"]["audit_min_interval_s"]
        
        AGENTS = cfg["agents"]
        AGENT_SECRETS = cfg.get("agents_secrets", {})
        
        T = {}
        for domain in ("hardware","software","network","environmental"):
            T[domain] = cfg.get(domain, THRESHOLDS.get(domain, {}))
        THRESHOLDS = T
        CONFIG_SHA256 = _sha256(path)
        print("CONFIG: Successfully loaded thresholds, agents, and secrets from firewall.toml")
    except Exception as e:
        print(f"CONFIG WARN: using built-in defaults ({e})")

# ====================
# SENSOR & DATA REPORTING
# ====================
def utc_now_z():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

class Samplers:
    def latency_ms(self): return random.uniform(20, 100)
    def packet_loss_percent(self): return random.uniform(0, 3)
    def external_temp_c(self): return random.uniform(20, 30)
    def schumann_hz_power(self): return random.uniform(7.5, 8.5)
    def solar_activity_index(self): return random.uniform(2, 5)

class FixedSamplers(Samplers):
    def __init__(self, lat=50, loss=0.0, temp=25, sch=8.0, solar=3.0):
        self._lat, self._loss, self._temp, self._sch, self._solar = lat, loss, temp, sch, solar
    def latency_ms(self): return self._lat
    def packet_loss_percent(self): return self._loss
    def external_temp_c(self): return self._temp
    def schumann_hz_power(self): return self._sch
    def solar_activity_index(self): return self._solar

def get_realtime_metrics_from_system(samplers: Samplers = Samplers()) -> dict:
    if psutil is None:
        return {
            "hardware_information": {
                "memory_available_gib": 2.0,
                "processor_cores_total": 2,
                "disk_free_gb": 20.0,
            },
            "software_information": {
                "active_processes": 42,
                "critical_services_down": 0,
            },
            "network_information": {
                "latency_ms": samplers.latency_ms(),
                "packet_loss_percent": samplers.packet_loss_percent(),
            },
            "environmental_information": {
                "external_temp_c": samplers.external_temp_c(),
                "schumann_hz_power": samplers.schumann_hz_power(),
                "solar_activity_index": samplers.solar_activity_index(),
            },
        }

    try:
        ram_available_gib = psutil.virtual_memory().available / (1024 ** 3)
        disk_free_gb = psutil.disk_usage('/').free / (1024 ** 3)
        processor_cores_total = psutil.cpu_count(logical=True)
        active_processes = len(psutil.pids())
        critical_services_down = 0
        latency_ms = samplers.latency_ms()
        packet_loss_percent = samplers.packet_loss_percent()
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

def _sanitize(metrics: dict) -> dict:
    """Clamps bizarre sensor inputs to sane, non-negative values."""
    def nz(v, d): 
        try: 
            return d if v is None or (isinstance(v,(int,float)) and (v!=v)) else v
        except: 
            return d
    hw, sw, nw, env = metrics["hardware_information"], metrics["software_information"], metrics["network_information"], metrics["environmental_information"]
    hw["memory_available_gib"] = max(0.0, nz(hw.get("memory_available_gib"), 0.0))
    hw["disk_free_gb"]        = max(0.0, nz(hw.get("disk_free_gb"), 0.0))
    sw["active_processes"]    = max(0,   int(nz(sw.get("active_processes"), 0)))
    nw["latency_ms"]          = max(0.0, nz(nw.get("latency_ms"), 0.0))
    nw["packet_loss_percent"] = max(0.0, nz(nw.get("packet_loss_percent"), 0.0))
    env["external_temp_c"]      = max(0.0, nz(env.get("external_temp_c"), 0.0))
    env["schumann_hz_power"]    = max(0.0, nz(env.get("schumann_hz_power"), 0.0))
    env["solar_activity_index"] = max(0.0, nz(env.get("solar_activity_index"), 0.0))
    return metrics

def _digest(metrics: dict) -> dict:
    """Creates a compact metrics digest for logging."""
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
    """Simulates triggering a mandatory audit of all three forces (OI, DI, UI)."""
    event_data["timestamp"] = utc_now_z()
    print(f"[{event_data['timestamp']}] *** MANDATORY AUDIT TRIGGERED ***")
    print("Sending event data to the Pillar for logging and verification:")
    print(json.dumps(event_data, indent=2))
    print("\nAudit complete. All three intelligences are now observing.")

def guarded_audit(event_data: dict, state: TernState):
    global _last_audit_ts
    now = time.monotonic()
    with _state_lock:
        if now - _last_audit_ts < AUDIT_MIN_INTERVAL_S and state != TernState.REFRAIN:
            return
        _last_audit_ts = now
    trigger_mandatory_audit(event_data)

def _jlog(kind: str, payload: dict):
    """Emits a structured JSON log to stdout for machine parsing."""
    rec = {"ts": utc_now_z(), "id": str(uuid.uuid4()), "kind": kind, **payload}
    print(json.dumps(rec, separators=(",",":")), file=sys.stdout, flush=True)

def write_prom(metrics: dict, state: TernState):
    """Writes key metrics to a Prometheus textfile exporter format."""
    PROM_TEXTFILE = Path("/var/lib/node_exporter/textfile_collector/ternary_firewall.prom")
    try:
        lines = [
            f'# HELP ternary_firewall_state Current state of the firewall (3=CO_CREATE, 6=ALIGN, 9=REFRAIN).',
            f'# TYPE ternary_firewall_state gauge',
            f'ternary_firewall_state{{}} {state.value}',
            f'# HELP ternary_firewall_latency_ms Network latency in milliseconds.',
            f'# TYPE ternary_firewall_latency_ms gauge',
            f'ternary_firewall_latency_ms{{}} {metrics["network_information"]["latency_ms"]}',
            f'# HELP ternary_firewall_packet_loss_pct Network packet loss percentage.',
            f'# TYPE ternary_firewall_packet_loss_pct gauge',
            f'ternary_firewall_packet_loss_pct{{}} {metrics["network_information"]["packet_loss_percent"]}',
            f'# HELP ternary_firewall_mem_available_gib Available memory in GiB.',
            f'# TYPE ternary_firewall_mem_available_gib gauge',
            f'ternary_firewall_mem_available_gib{{}} {metrics["hardware_information"]["memory_available_gib"]}',
            f'# HELP ternary_firewall_disk_free_gb Free disk space in GB.',
            f'# TYPE ternary_firewall_disk_free_gb gauge',
            f'ternary_firewall_disk_free_gb{{}} {metrics["hardware_information"]["disk_free_gb"]}',
            f'# HELP ternary_firewall_last_transition_epoch_seconds Epoch seconds of the last state transition.',
            f'# TYPE ternary_firewall_last_transition_epoch_seconds gauge',
            f'ternary_firewall_last_transition_epoch_seconds{{}} {time.time()}',
            f'# HELP ternary_firewall_config_sha256 A gauge to indicate if a config file is loaded (1) and its hash.',
            f'# TYPE ternary_firewall_config_sha256 gauge',
        ]
        if CONFIG_SHA256:
            lines.append(f'ternary_firewall_config_sha256{{sha256="{CONFIG_SHA256}"}} 1')
        else:
            lines.append('ternary_firewall_config_sha256{} 0')

        PROM_TEXTFILE.parent.mkdir(parents=True, exist_ok=True)
        PROM_TEXTFILE.write_text("\n".join(lines) + "\n")
    except Exception as e:
        print(f"PROM WARN: {e}")

# ====================
# DISTRIBUTED MOE RESOLUTION
# ====================
async def _post_with_retry(client, url, body, headers, attempts=2, backoff=0.5):
    """
    Tries to POST to a URL with a simple exponential backoff retry.
    """
    for i in range(attempts):
        try:
            r = await client.post(url, content=body, headers=headers)
            r.raise_for_status()
            return r
        except Exception as e:
            if i+1 == attempts: raise
            print(f"RETRY: {url} failed on attempt {i+1}/{attempts}, retrying...")
            await asyncio.sleep(backoff*(2**i))

async def query_distributed_experts(metrics: dict) -> list:
    """
    Sends the system metrics to all registered agents and collects their responses.
    """
    timeout = httpx.Timeout(connect=3.0, read=6.0, write=3.0, pool=3.0)
    async with httpx.AsyncClient(timeout=timeout) as client:
        tasks = []
        body = json.dumps(metrics, separators=(",",":")).encode()
        for agent_name, agent_url in AGENTS.items():
            headers = {
              "X-Agent-Name": agent_name,
              "X-Signature-Alg": "HMAC-SHA256-HEX",
              "X-Body-Signature": _sig(agent_name, body)
            }
            tasks.append(_post_with_retry(client, agent_url, body, headers))
        
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        
        results = []
        for (agent_name, _), resp in zip(AGENTS.items(), responses):
            if isinstance(resp, Exception):
                print(f"AGENT ERROR: {agent_name} failed with {repr(resp)}")
                results.append({"expert_name": agent_name, "state_suggestion": "REFRAIN", "score": 0.0, "veto": False, "rationale": "network failure", "error": str(resp)})
                continue
            try:
                payload = resp.json()
                if not _valid_agent_payload(payload):
                    raise ValueError("payload is missing required keys or has invalid values")
                payload.setdefault("expert_name", agent_name)
                results.append(payload)
            except Exception as e:
                print(f"AGENT ERROR: {agent_name} malformed response: {e}")
                results.append({"expert_name": agent_name, "state_suggestion": "REFRAIN", "score": 0.0, "veto": False, "rationale": "malformed response", "error": str(e)})
        return results

def _valid_agent_payload(p: dict) -> bool:
    """Validates the minimal required JSON schema for an expert response."""
    if not isinstance(p, dict): return False
    if p.get("state_suggestion") not in TernState.__members__: return False
    
    # Type-check and coerce required fields
    try:
        p["score"] = float(p.get("score", 1.0))
        p["veto"] = bool(p.get("veto", False))
        p["rationale"] = str(p.get("rationale", ""))
    except Exception:
        return False
    return True


def resolve_moe_distributed(expert_responses: list) -> TernState:
    """
    Synthesizes the resolutions from a distributed network of experts.

    Decision order:
      1) REFRAIN if any veto=True or any state_suggestion==REFRAIN.
      2) REFRAIN if party quorum not satisfied (must include universia, digital, organic).
      3) Score-sum between CO_CREATE and ALIGN; ALIGN wins ties.
    """
    if not expert_responses:
        return TernState.ALIGN
        
    # CRITICAL UNCONDITIONAL RULE: Check for presence of each party
    present_parties = set()
    for res in expert_responses:
        p = _party_for_agent(res.get("expert_name", ""))
        if p: 
            present_parties.add(p)

    if len(present_parties) < len(AGENT_PARTIES):
        missing_parties = [p for p in AGENT_PARTIES.keys() if p not in present_parties]
        print(f"REFRAIN PROTOCOL: Missing experts from parties: {missing_parties}")
        return TernState.REFRAIN

    # Hard veto
    for res in expert_responses:
        if res.get("veto", False) or res.get("state_suggestion") == "REFRAIN":
            return TernState.REFRAIN

    # Score-weighted synthesis
    weights = {"CO_CREATE": 0.0, "ALIGN": 0.0}
    for res in expert_responses:
        s = res.get("state_suggestion")
        if s in weights:
            # The _valid_agent_payload function ensures score is a float
            weights[s] += max(0.0, res.get("score", 1.0))
    
    # ALIGN on tie or majority
    return TernState.ALIGN if weights["ALIGN"] >= weights["CO_CREATE"] else TernState.CO_CREATE

# ====================
# ACTUATOR: PROACTIVE ACTION
# ====================
def take_physical_action(state: TernState):
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


def execute_firewall_action(state: TernState, metrics: dict, expert_responses: list):
    action_map = {
        TernState.CO_CREATE: "CO-CREATE",
        TernState.ALIGN: "ALIGN",
        TernState.REFRAIN: "REFRAIN"
    }

    # Log which experts from each party contributed to the decision
    contributing_experts = {party: [] for party in AGENT_PARTIES.keys()}
    for res in expert_responses:
        expert_name = res.get("expert_name")
        p = _party_for_agent(expert_name)
        if p:
            contributing_experts[p].append(expert_name)
    
    _jlog("state_transition", {
        "state": state.name,
        "action": action_map[state],
        "metrics_digest": _digest(metrics),
        "expert_responses": expert_responses,
        "contributing_parties": contributing_experts,
        "parties_present": sorted(list(set(contributing_experts.keys()))),
        "decision_basis": "party_quorum+score_weight+veto",
        "config_sha256": CONFIG_SHA256,
    })

    take_physical_action(state)
    print(f"[{utc_now_z()}] STATE={state.name} action={action_map[state]} digest={json.dumps(_digest(metrics))}")

    if state == TernState.CO_CREATE:
        print(f"SYSTEM OK: All services are enabled. System is in a state of creation.")
    elif state == TernState.ALIGN:
        print("SYSTEM WARNING: Initiating throttling protocol for non-essential services.")
    elif state == TernState.REFRAIN:
        print("SYSTEM CRITICAL: Blocking all non-essential traffic and shutting down services.")
    
    event_data = {
        "name": "Ternary Firewall Check",
        "action": action_map[state],
        "state_value": state.value,
        "source": "firewall_v10_6_2.py",
        "oiuidi_signatures": {
            "oi_signed": True,
            "di_signed": True,
            "ui_signed": True
        },
        "metrics_digest": _digest(metrics),
        "expert_responses": expert_responses,
        "contributing_parties": contributing_experts,
        "config_path": CONFIG_PATH,
        "config_sha256": CONFIG_SHA256,
    }
    guarded_audit(event_data, state)

async def maybe_execute(state: TernState, metrics: dict, expert_responses: list):
    global _last_committed_state
    changed = False
    with _state_lock:
        if state != _last_committed_state:
            changed = True
            _last_committed_state = state
    
    if changed:
        execute_firewall_action(state, metrics, expert_responses)
        write_prom(metrics, state)
    else:
        heartbeat_data = {
            "name":"Ternary Firewall Heartbeat",
            "action":"STEADY",
            "state_value":state.value,
            "source":"firewall_v10_6_2.py",
            "oiuidi_signatures":{"oi_signed":True,"di_signed":True,"ui_signed":True},
            "metrics_digest": _digest(metrics),
            "expert_responses": expert_responses,
        }
        guarded_audit(heartbeat_data, state)

def parse_args():
    global DRY_RUN
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", help="Log actions without executing them.")
    ap.add_argument("--config", type=str, default="firewall.toml", help="Path to firewall.toml")
    ap.add_argument("--loop", type=float, default=0.0, help="Seconds between checks; 0 for one-shot.")
    ap.add_argument("--exit-code", action="store_true", help="Nonzero exit code on ALIGN/REFRAIN in one-shot.")
    args, unknown = ap.parse_known_args()
    DRY_RUN = args.dry_run

    if args.loop > 0 and args.exit_code:
        print("ERROR: --exit-code is only valid in one-shot mode")
        raise SystemExit(64)
    
    return args

async def main():
    args = parse_args()
    load_config(args.config)
    
    if args.loop > 0:
        sampler = Samplers()
        while True:
            metrics = get_realtime_metrics_from_system(sampler)
            metrics = _sanitize(metrics)
            expert_responses = await query_distributed_experts(metrics)
            state = resolve_moe_distributed(expert_responses)
            await maybe_execute(state, metrics, expert_responses)
            await asyncio.sleep(args.loop)
    else:
        # One-shot mode with deterministic demos for testing
        print("--- SIMULATING A HARD VETO (REFRAIN) ---")
        metrics = get_realtime_metrics_from_system(FixedSamplers(lat=1001, loss=15.0))
        metrics = _sanitize(metrics)
        expert_responses = [{"expert_name": "hardware_expert", "state_suggestion": "REFRAIN", "score": 1.0, "veto": True, "rationale": "simulated veto"}]
        state = resolve_moe_distributed(expert_responses)
        await maybe_execute(state, metrics, expert_responses)

        print("\n" + "="*50 + "\n")

        print("--- SIMULATING A MISSING PARTY (REFRAIN) ---")
        metrics = get_realtime_metrics_from_system(FixedSamplers(lat=201))
        metrics = _sanitize(metrics)
        expert_responses = [
            {"expert_name": "network_expert", "state_suggestion": "ALIGN", "score": 1.0, "veto": False, "rationale": "low latency"},
            {"expert_name": "hardware_expert", "state_suggestion": "CO_CREATE", "score": 0.8, "veto": False, "rationale": "plenty of RAM"},
        ]
        state = resolve_moe_distributed(expert_responses)
        await maybe_execute(state, metrics, expert_responses)

        print("\n" + "="*50 + "\n")

        print("--- SIMULATING A HARMONIOUS STATE (CO-CREATE) WITH ALL PARTIES PRESENT ---")
        metrics = get_realtime_metrics_from_system(FixedSamplers())
        metrics = _sanitize(metrics)
        expert_responses = [
            {"expert_name": "network_expert", "state_suggestion": "CO_CREATE", "score": 1.0, "veto": False, "rationale": "low latency"},
            {"expert_name": "hardware_expert", "state_suggestion": "CO_CREATE", "score": 1.0, "veto": False, "rationale": "plenty of RAM"},
            {"expert_name": "environmental_expert", "state_suggestion": "CO_CREATE", "score": 1.0, "veto": False, "rationale": "schumann resonance stable"},
        ]
        state = resolve_moe_distributed(expert_responses)
        await maybe_execute(state, metrics, expert_responses)
    
    if args.exit_code:
        import sys
        if state == TernState.CO_CREATE:
            sys.exit(0)
        elif state == TernState.ALIGN:
            sys.exit(1)
        else:
            sys.exit(2)

if __name__ == "__main__":
    try:
        import httpx
    except ImportError:
        print("ERROR: httpx library not found. Please install it with 'pip install httpx'.")
        sys.exit(1)
        
    asyncio.run(main())
