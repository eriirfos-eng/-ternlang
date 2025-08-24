# utils/seal.py
# prints the 𒀭 seal with a short message.
# no timestamps to respect the live-fetch rule.

BOX = "═" * 54

def print_seal(msg: str = "config set validated"):
    seal = "𒀭"
    banner = f"{seal}  rfi-irfos | ternlang/13"
    line1 = f"{banner:<54}"
    line2 = f"{msg:<54}"
    print(f"\n{BOX}\n{line1}\n{line2}\n{BOX}\n")
