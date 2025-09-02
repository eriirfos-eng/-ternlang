# RELEASES.md

## v1.0.0-rc1 — Time Crystal Kernel
**Date:** 2025-09-02T18:51:20Z  
**Tag:** `v1.0.0-rc1`  
**Checksum:**  
```sh
SHA256(ternkernel.zip)= <paste hash here>
Core Features

Algebra: meet/join/negation, Gödel residuum (→), equivalence (↔), XOR*, NAND recursion.

Policy Clamp: consequence operator (⇒) layered with residuum → ensures Consequence ≤ Truth.

Resilience: collapse_to_tend, tend_guard, safe_div — neutralizes divide-by-zero faults.

Event System: local event bus with pluggable sinks (CollapseEvent, EntailmentEvent).

Surfaces: FastAPI REST server (/safe_div, /collapse), CLI harness for demos/tests.

Verification: pytest suite validating De Morgan, residuation, distributivity, policy ≤ residuum.

Operational Guidance

License: AGPL-3.0-or-later (repo-wide).

CI: GitHub Actions matrix for 3.9–3.12, auto-build artifacts.

Container: docker build -t ternkernel:rc1 . → docker run -p 8000:8000 ternkernel:rc1.

Systemd: unit file provided in /docs/ops/systemd-ternkernel.service.

Telemetry: local-only event logs at /var/log/ternkernel/events.jsonl, daily rotation.

Safety Controls

Shadow → canary → full rollout sequence.

Abort thresholds:

crash > 0/10min

collapse events >5% of calls

p95 latency >250ms

Policy clamp default = ON (KERNEL_POLICY=on).

Human Protocol

Fear is normal; act from clarity not adrenaline.

Rest before production merge.

Re-run full test suite before promotion.


⬛ suggestion: generate the SHA256 now and paste it into the checksum slot, then push this alongside the `v1.0.0-rc1` tag. want me to hand you the command and verify the hash of your current `ternkernel.zip` so you can fill it in?

Tuesday-2025-Sep-02T:06:52:56PMZ


