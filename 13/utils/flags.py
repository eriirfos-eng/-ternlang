# utils/flags.py
def resolve_flag(state: float, master_docs: dict) -> str:
    """
    returns the color glyph for the current ternary stance based on thresholds
    and stage_09 'mapping' colors if present.
    """
    harm = master_docs["stage_06"]["rules"]["harm_threshold"]
    align = master_docs["stage_07"]["rules"]["alignment_score"]["min"]
    mapping = master_docs.get("stage_09", {}).get("mapping", {})
    if state <= harm:
        return mapping.get("REFRAIN", {}).get("color", "🟜")
    if state >= align:
        return mapping.get("AFFIRM", {}).get("color", "⬛")
    return mapping.get("TEND", {}).get("color", "🟫")
