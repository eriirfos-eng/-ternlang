import argparse, json
from .fusion import run
from .core import Orchestrator, DetectorOutput, FailsafeConfig, FusionWeights

def main():
    p = argparse.ArgumentParser(prog="ternary-orchestrator")
    sub = p.add_subparsers(dest="cmd", required=True)

    p1 = sub.add_parser("process", help="fuse detector scores into ternary state")
    p1.add_argument("--text", required=True)
    p1.set_defaults(func=lambda a: print(json.dumps(run(a.text), ensure_ascii=False, indent=2)))

    args = p.parse_args()
    args.func(args)

if __name__ == "__main__":
    main()
