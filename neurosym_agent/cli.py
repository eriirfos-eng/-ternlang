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
import os
from azure.ai.inference import ChatCompletionsClient
from azure.ai.inference.models import SystemMessage, UserMessage
from azure.core.credentials import AzureKeyCredential

endpoint = "https://models.github.ai/inference"
model = "openai/gpt-5"
token = os.environ["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"]

client = ChatCompletionsClient(
    endpoint=endpoint,
    credential=AzureKeyCredential(token),
)

response = client.complete(
    messages=[
        SystemMessage("You are a helpful assistant."),
        UserMessage("What is the capital of France?"),
    ],
    model=model
)
