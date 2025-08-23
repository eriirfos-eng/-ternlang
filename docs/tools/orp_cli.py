#!/usr/bin/env python3
import argparse, json
from ternary_phase_modulator import TernaryPhaseModulator

def main():
    p = argparse.ArgumentParser(description="Run ORP engine")
    p.add_argument("--host", default="Simeon")
    p.add_argument("--origin", type=int, default=1, help="1/0")
    p.add_argument("--action", type=int, default=1, help="1/0")
    p.add_argument("--lord", type=int, default=1, help="1/0")
    p.add_argument("--seed", type=int, default=None)
    p.add_argument("--blueprint", default="ternary_operator.json")
    p.add_argument("--op", choices=["xor","majority"], default="xor")
    args = p.parse_args()

    op = TernaryPhaseModulator._xor3 if args.op=="xor" \
         else TernaryPhaseModulator.majority3

    mod = TernaryPhaseModulator(
        host_name=args.host,
        origin=bool(args.origin),
        action=bool(args.action),
        lord=bool(args.lord),
        blueprint_path=args.blueprint,
        synthesis_fn=op,
        seed=args.seed
    )
    out = mod.run()
    print(json.dumps(out, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
