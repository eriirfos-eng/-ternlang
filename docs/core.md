# Core Specification Draft – v0.1.0

## Logic Basis

Ternlang operates on a ternary logic core:
- `-1` → Refrain (withdraw, do not engage)
- `0` → Tend (observe, hold, adjust)
- `+1` → Act (engage, execute)

This logic is designed for recursive flow, not imperative execution.

## Sample Structural Flow

```ternlang
agent.state = observe(input)

if (agent.state == resonance):
    return +1  // act
elif (agent.state == null):
    return 0   // tend
else:
    return -1  // refrain
