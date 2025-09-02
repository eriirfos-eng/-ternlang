import numpy as np
from ternlang.core.resilience import CollapseEvent, _emit

def set_numpy_div0_policy():
    # map inf/nan from vectorized ops to TEND by replacement
    np.seterr(all="ignore")
    # user applies: y = safe_div(a, b)
def safe_div(a, b):
    out = np.divide(a, b, out=np.zeros_like(a, dtype=float), where=(b!=0))
    if np.any(b==0):
        _emit(CollapseEvent(op="np.divide", a=float(np.nan), b=0.0, meta={"vectorized":True}))
    # classify is per-element; keep scalar TEND semantics at aggregate layer
    return out
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
