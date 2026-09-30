# Chelis 0.18.12 migration candidate

Economoist 0.2.14 prepares a direct move from Chelis 0.18.10 to 0.18.12.
The package, workflow pins, bundled `chelis-std` lock, managed conformance
content, and C Note manifest move together. The 0.18.11 compiler release is
published, but Economoist did not publish a package at that pin.

Chelis release PR #2821 is still in CI. The official 0.18.12 asset and its
checksum do not exist yet. The lock and local probes in this candidate use
a Mach-O arm64 compiler built from the earlier reviewed release head
`8cb4946a365569ceda478f86a7c37baa3fda4082`. Its binary reports
`chelis 0.18.12` and has SHA-256
`87706ef371028e8f173c44e2fa894e1e5f9c3b90496de888c4542bbd9973b84d`;
this is provisional evidence, not the release gate.

The blocked diagnostic sentinel and negative test still report their expected
failures with the candidate. No `UPSTREAM_BUGS.md` tracking entry has a
0.18.12 re-probe trigger, and no model, property, or sampled source is changed.
The manifest retains nine expected SMT proofs and one sampled AD tier.
`CHELIS_BIN=<candidate> CHELIS_REEF_HOME=<isolated> .venv/bin/python
scripts/run_local_gate.py --quiet` passed all ten stages on 2026-09-30,
including package build, proof, forge, and numeric oracle checks.
`scripts/contract_gate.py`, `scripts/audit_workarounds.py --pins-only`,
and `chelis reef conform audit --explain` also passed; the conformance audit
reported no MUST failures.

Before this PR can leave draft, install the published 0.18.12 compiler with
`scripts/install_chelis_toolchain.py`, regenerate `reef.lock` with that binary,
and inspect the result. Run the complete ten-stage `scripts/run_local_gate.py`
with `CHELIS_BIN` set to the installed release binary, then recheck
`chelis reef conform audit`, the pin audit, C Note manifest consistency, and
all capability claims above. Record the official asset identity and exact gate
results in this migration record.
