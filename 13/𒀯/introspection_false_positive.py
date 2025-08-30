from introspection_false_positive import propose_and_simulate

# inside the hourly loop
finding, sim = propose_and_simulate(CFG_CHAIN_PATH)
if finding:
    self._append("introspection_finding", {
        "window": {"start": finding.window_start, "end": finding.window_end},
        "sig_key": finding.sig_key,
        "total_alerts": finding.total_alerts,
        "overruled": finding.overruled,
        "overrule_rate": round(finding.overrule_rate,4),
        "proposal_delta_lo": finding.proposal_delta_lo,
        "evidence": finding.evidence_digests,
    })
    self._append("introspection_simulation", {
        "window": {"start": sim.window_start, "end": sim.window_end},
        "delta_lo": sim.delta_lo,
        "overrides_before": sim.overrides_before,
        "overrides_after": sim.overrides_after,
        "improvement_pct": sim.improvement_pct,
        "potential_missed_affirms": sim.potential_missed_affirms,
        "missed_affirms_pct": sim.missed_affirms_pct,
        "decision": sim.decision,
        "notes": sim.notes,
    })
    if sim.decision == "approve":
        # canary apply: record it, then set overlay param
        self._append("introspection_apply", {
            "target": "CFG_LO",
            "delta": finding.proposal_delta_lo,
            "mode": "canary",
            "fraction": 0.1,
            "duration_min": 60,
            "sig_key": finding.sig_key,
        })
        # example overlay setter; you already have ParamOverlay in your code sketch
        PARAMS.set("CFG_LO", PARAMS.get("CFG_LO", CFG_LO) + finding.proposal_delta_lo)
