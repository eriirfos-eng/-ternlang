# protocols/quantum_logic_clock.py
from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timezone, timedelta
import json
from typing import Dict, Any, Tuple

MONTHS = [
    "Monad","Dyad","Triad","Tetrad","Pentad","Hexad",
    "Heptad","Octad","Ennead","Decad","Undecad","Duodecad","Tredecad"
]

@dataclass
class NumerusDate:
    year_anchor_utc: datetime
    month_index: int         # 1..13
    month_name: str
    day: int                 # 1..28
    is_void: bool

def parse_isoz(s: str) -> datetime:
    return datetime.fromisoformat(s.replace("Z","+00:00")).astimezone(timezone.utc)

def is_void_day(dt: datetime, void_mm_dd: str="09-14") -> bool:
    mmdd = dt.strftime("%m-%d")
    return mmdd == void_mm_dd

def days_since_anchor(anchor: datetime, dt: datetime, void_mm_dd: str="09-14") -> int:
    # count days since anchor, skipping the Void day each year as non-count
    days = 0
    step = timedelta(days=1)
    t = anchor
    inc = 1 if dt >= anchor else -1
    while t.date() != dt.date():
        t += step * inc
        if not is_void_day(t, void_mm_dd):
            days += inc
    return days

def to_numerus(anchor: datetime, dt: datetime, void_mm_dd: str="09-14") -> NumerusDate:
    if is_void_day(dt, void_mm_dd):
        return NumerusDate(anchor, 7, "Heptad", 0, True)  # month name is cosmetic for 0 day
    d = days_since_anchor(anchor, dt, void_mm_dd)
    d_mod = d % 364  # 13*28
    month_index = (d_mod // 28) + 1
    day = (d_mod % 28) + 1
    return NumerusDate(anchor, month_index, MONTHS[month_index-1], day, False)

def phase_fraction(elapsed_days: float, period_days: float) -> float:
    f = (elapsed_days / period_days) % 1.0
    return f if f >= 0 else f + 1.0

def gaussian_closeness(frac: float, centers: Tuple[float,...]=(0.0,), eps: float=0.03) -> float:
    # distance to nearest center on the circle
    import math
    d = min(min(abs(frac-c), 1-abs(frac-c)) for c in centers)
    return math.exp(- (d/eps)**2)

def elapsed_days(start_utc: datetime, now_utc: datetime) -> float:
    return (now_utc - start_utc).total_seconds() / 86400.0

def numerus_modulator(nu: NumerusDate) -> str:
    # quick mapping for decision flavor
    return {
        1:"sovereign cut",
        2:"name boundary",
        3:"invent third way",
        4:"build scaffold",
        5:"adapt and iterate",
        6:"rebalance ties",
        7:"study before acting",
        8:"tune the loop",
        9:"close with grace",
        10:"integrate branches",
        11:"protect the breakthrough",
        12:"publish cadence",
        13:"prune and renew",
    }[nu.month_index]

def tick(config: Dict[str,Any], now_utc: datetime|None=None) -> Dict[str,Any]:
    if not now_utc:
        now_utc = datetime.now(timezone.utc)

    start = parse_isoz(config["start_utc"])
    anchor = parse_isoz(config.get("calendar_anchor_utc","2025-03-15T00:00:00Z"))
    void_mm_dd = config.get("void_day_mm_dd","09-14")
    eps = float(config.get("epsilon_sync",0.03))
    w3 = float(config.get("weights",{}).get("w3",1.0))
    w6 = float(config.get("weights",{}).get("w6",1.0))
    w9 = float(config.get("weights",{}).get("w9",1.0))

    nu = to_numerus(anchor, now_utc, void_mm_dd)
    # elapsed days since start for continuous phase
    ed = elapsed_days(start, now_utc)

    p3 = phase_fraction(ed, 3.0)
    p6 = phase_fraction(ed, 6.0)
    p9 = phase_fraction(ed, 9.0)

    c3 = gaussian_closeness(p3, centers=(0.0,), eps=eps)
    c6 = gaussian_closeness(p6, centers=(0.0,0.5), eps=eps)  # allow 0 and half-cycle for symmetry
    c9 = gaussian_closeness(p9, centers=(0.0,), eps=eps)

    resonance = (w3*c3 + w6*c6 + w9*c9) / max(w3+w6+w9,1e-9)

    return {
        "now_utc": now_utc.isoformat().replace("+00:00","Z"),
        "numerus": {
            "is_void": nu.is_void,
            "month_index": nu.month_index,
            "month_name": nu.month_name,
            "day": nu.day
        },
        "phases": {
            "p3": round(p3,6),
            "p6": round(p6,6),
            "p9": round(p9,6),
            "sync": {
                "c3": round(c3,6),
                "c6": round(c6,6),
                "c9": round(c9,6),
                "resonance": round(resonance,6)
            }
        },
        "modulator": numerus_modulator(nu),
    }

if __name__ == "__main__":
    import argparse, sys, yaml
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="qlc.yaml")
    ap.add_argument("--now", default=None, help="ISO8601 Z time. Default: current UTC")
    args = ap.parse_args()
    with open(args.config,"r",encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    now = parse_isoz(args.now) if args.now else None
    print(json.dumps(tick(cfg, now), indent=2))
