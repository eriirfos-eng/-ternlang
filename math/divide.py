from ternlang.core.resilience import collapse_to_tend, REFRAIN, TEND, AFFIRM

@collapse_to_tend("divide")
def divide(a: float, b: float):
    res = a / b
    if res < 0:  return res, "REFRAIN"
    if res == 0: return res, "TEND"
    return res, "AFFIRM"
