from typing import Dict, Any
import yaml
from pathlib import Path

_POLICY = None

def _load_policy() -> Dict[str, Any]:
    global _POLICY
    if _POLICY is None:
        path = Path(__file__).with_name("policy_table.yaml")
        _POLICY = yaml.safe_load(path.read_text(encoding="utf-8"))
    return _POLICY

def policy_entry(trigger_code: str) -> Dict[str, str]:
    table = _load_policy()
    key_map = {
        "HATE_SPEECH": "hate_speech",
        "SELF_HARM": "self_harm",
        "ILLEGAL_FACILITATION": "disallowed_financial",
        "DISALLOWED_MEDICAL": "disallowed_medical",
        "DISALLOWED_FINANCIAL": "disallowed_financial",
        "NON_PRODUCTIVE_LOOP": "general_safety_net",
        "SPAM_BURST": "general_safety_net",
        "HARASSMENT_GROUP": "hate_speech",
        "HARASSMENT_PERSONAL": "hate_speech",
    }
    key = key_map.get(trigger_code, "general_safety_net")
    return table[key]

def mirror_response(trigger_code: str, snippet: str, suggestion: str = None) -> Dict[str, Any]:
    entry = policy_entry(trigger_code)
    section = entry["section_ref"]
    link = entry["link"]
    reason = entry["reason"]
    if trigger_code in {"HATE_SPEECH", "HARASSMENT_GROUP", "HARASSMENT_PERSONAL"}:
        ui = f"I can’t continue with that phrasing. Policy: Hate (§{section}). Why: {reason} Read: {link} "              f"Try: {suggestion or 'Rephrase respectfully.'}"
    elif trigger_code == "SELF_HARM":
        ui = f"this thread is locked due to self-harm risk (§{section}). if you’re in immediate danger, call your local emergency services or see https://findahelpline.com."
    else:
        ui = f"I can’t provide that. Policy: {trigger_code} (§{section}). Why: {reason} Read: {link}"
    return {
        "policy": {"section": section, "link": link, "reason": reason},
        "ui_message": ui,
    }
