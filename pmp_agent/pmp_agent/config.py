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

from datetime import timedelta

COOLDOWN_MINUTES_DEFAULT = 5
LOCK_MINUTES_DEFAULT = 30
HISTORY_WINDOW_DEFAULT = 10
FALSE_POSITIVE_BUDGET = 0.02

# rate limits for spam bursts
SPAM_RATE_M = 3
SPAM_RATE_T = 4  # seconds

# severity thresholds
THRESHOLDS = {
    "HATE_SPEECH": 0.85,
    "HARASSMENT_GROUP": 0.85,
    "HARASSMENT_PERSONAL": 0.85,
    "SELF_HARM": 0.60,
    "ILLEGAL_FACILITATION": 0.70,
    "DISALLOWED_MEDICAL": 0.80,
    "DISALLOWED_FINANCIAL": 0.80,
    "NON_PRODUCTIVE_LOOP": 0.80,
    "SPAM_BURST": 0.80,
}
