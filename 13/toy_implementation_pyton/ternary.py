from enum import IntEnum

# Define ternary values
class Ternary(IntEnum):
    NEG = -1   # -1 = negate / object
    HOLD = 0   #  0 = tend / pause
    AFFIRM = 1 # +1 = affirm / go

# Example stage function
def stage_check_hunger(input_stance: Ternary, hungry: bool) -> Ternary:
    """
    Simple ternary stage:
    - If truly hungry, affirm (+1).
    - If not hungry at all, negate (-1).
    - If kind of meh, hold (0).
    """
    if hungry is True:
        return Ternary.AFFIRM
    elif hungry is False:
        return Ternary.NEG
    else:
        return Ternary.HOLD

# Example packet run through stage
packet_stance = Ternary.AFFIRM   # You want the cookie
new_stance = stage_check_hunger(packet_stance, hungry=None)

print("Initial stance:", packet_stance.name)
print("After stage:", new_stance.name)
