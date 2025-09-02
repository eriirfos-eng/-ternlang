import argparse
from neurosym_agent.core import load_agent

def main():
    parser = argparse.ArgumentParser(description="Run Neurosym Agent with a JSON payload")
    parser.add_argument("path", help="Path to JSON payload")
    args = parser.parse_args()
    agent = load_agent(args.path)
    print(agent.dict())
    print("Ternary state:", agent.state())

if __name__ == "__main__":
    main()
