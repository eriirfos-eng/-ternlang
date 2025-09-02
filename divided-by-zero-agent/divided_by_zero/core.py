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

from pydantic import BaseModel, Field

REFRAIN = -1
TEND = 0
AFFIRM = 1

class DivInput(BaseModel):
    a: float = Field(..., description="numerator")
    b: float = Field(..., description="denominator")

class DivResult(BaseModel):
    result: float
    state: str

class DividedByZeroAgent:
    def __init__(self):
        pass

    def divide(self, inp: DivInput) -> DivResult:
        try:
            res = inp.a / inp.b
            # classify ternary: <0 → REFRAIN, =0 → TEND, >0 → AFFIRM
            if res < 0:
                state = "REFRAIN"
            elif res == 0:
                state = "TEND"
            else:
                state = "AFFIRM"
            return DivResult(result=res, state=state)
        except ZeroDivisionError:
            # collapse into TEND (0)
            return DivResult(result=0, state="TEND")
