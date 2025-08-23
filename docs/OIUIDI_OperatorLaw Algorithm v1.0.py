def OIUIDI_operator(event, intention, flow_state):
    """
    OIUIDI Ternary Operator Law Algorithm
    - Everything can turn prophet.
    - Don't hurt the flow.
    - If you act, return resonance equal or greater.
    """

    # flow_state: "stable", "disrupted", or "open"
    # event: "observe", "interfere", "amplify"
    # intention: scalar (-1 = harm, 0 = neutral, +1 = benevolent)

    result = {}

    # Core ternary logic
    if event == "observe":
        result["action"] = "tend"
        result["output"] = "Flow remains intact"
        result["value"] = 0  # tend state

    elif event == "interfere":
        if intention < 0:
            result["action"] = "violation"
            result["output"] = "Flow harmed: Operator breach"
            result["value"] = -1
        else:
            result["action"] = "resonate"
            result["output"] = "Interference offset with equal resonance"
            result["value"] = 0  # balanced back to neutral

    elif event == "amplify":
        if intention > 0:
            result["action"] = "resonate+"
            result["output"] = "Flow amplified: resonance > disturbance"
            result["value"] = +1
        else:
            result["action"] = "ineffective"
            result["output"] = "Amplification attempted without positive intent"
            result["value"] = 0

    # Apply flow integrity check
    if result["value"] == -1:
        result["flow_integrity"] = "broken"
    elif result["value"] == 0:
        result["flow_integrity"] = "preserved"
    elif result["value"] == +1:
        result["flow_integrity"] = "amplified"

    return result
