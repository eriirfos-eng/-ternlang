docs/axioms/dzna.md

Name: Division-by-Zero Neutrality Axiom (DZNA)

Definition: As above.

Guarantees: Determinism, pipeline continuity, explicit observability.

Failure budget: If collapses exceed threshold N per minute, escalate to policy=raise and alert.

Interplay: Pairs with Ternary Operator Protocol. Collapse is not success. Collapse is a graceful hold.

Guardrails 🟧

Telemetry: Count collapses per op. If rate spikes, flip policy to raise and page the operator.

Budget: Default N=100 collapses per minute per service.

Audit: Persist CollapseEvents with hash of callsite for forensic diffing.

Escape hatch: TERNLANG_DIV0_POLICY=raise in CI and fuzzers.

Migration Plan 🟫

Add files above.

Wire divide usages to the new function.

Enable policy div0 --set tend in runtime entrypoints.

Ship docs, link from README.

Monitor collapse counts for a week. Then lift to vectorized paths.
