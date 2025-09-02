"""
CLI entry for ternkernel.
"""
import sys, json
from ..core.ternary import VALID
from ..adapters.numpy_bridge import safe_div
from ..policy import consequence
from ..core.ternary import imp_godel
from ..event_bus import BUS
from ..core.resilience import set_event_sink

def _parse_t(x: str) -> int:
    v = int(x)
    if v not in VALID:
        raise SystemExit("values must be -1, 0, or 1")
    return v

def _sink(ev):
    print(json.dumps(ev))

def demo():
    set_event_sink(lambda ev: BUS.publish(ev.get("type","event"), ev))
    print("safe_div demo: dividing [1,2,3] by [1,0,2]")
    out = safe_div([1,2,3],[1,0,2])
    print("result:", out)

def collapse_cmd(args):
    if len(args) < 3:
        raise SystemExit("usage: collapse <state> <signal> <hold_count>")
    from ..agents.time_crystal.agent import TimeCrystalAgent, CollapseConfig
    state = _parse_t(args[0]); signal = _parse_t(args[1]); hold = int(args[2])
    set_event_sink(lambda ev: BUS.publish(ev.get("type","event"), ev))
    ag = TimeCrystalAgent(CollapseConfig())
    print(ag.collapse(state, signal, hold))

def entail_cmd(args):
    if len(args) < 2:
        raise SystemExit("usage: entail <a> <b>")
    a = _parse_t(args[0]); b = _parse_t(args[1])
    print(consequence(a,b))

def safe_div_cmd(args):
    if len(args) < 2:
        raise SystemExit("usage: safe_div <a> <b>  # scalars or JSON arrays")
    def maybe_json(x):
        x = x.strip()
        if x.startswith("["):
            import json as _j; return _j.loads(x)
        return int(x)
    a = maybe_json(args[0]); b = maybe_json(args[1])
    set_event_sink(lambda ev: BUS.publish(ev.get("type","event"), ev))
    print(safe_div(a,b))

def main():
    if len(sys.argv) < 2:
        raise SystemExit("usage: python -m ternkernel.kernel.cli <demo|collapse|entail|safe_div> ...")
    cmd = sys.argv[1].lower()
    if cmd == "demo": return demo()
    if cmd == "collapse": return collapse_cmd(sys.argv[2:])
    if cmd == "entail": return entail_cmd(sys.argv[2:])
    if cmd == "safe_div": return safe_div_cmd(sys.argv[2:])
    raise SystemExit(f"unknown command: {cmd}")

if __name__ == "__main__":
    main()
