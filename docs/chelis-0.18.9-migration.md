# Chelis 0.18.9 migration

Economoist 0.2.12 participates in the compiler-compatible C Note dependency
release wave for Chelis 0.18.9. It uses the published compiler; no compiler
source build or local compiler patch is required. Chelis 0.18.9 supersedes
the unpublished 0.18.8 tag, so this shell moves directly from 0.18.7 to
0.18.9 with no functional change.

The compiler tag resolves to `TBD after v0.18.9 publishes`.
The sidecar-verified Linux glibc-2.31 archive SHA256 is
`TBD after v0.18.9 publishes`;
the compiler payload SHA256 is
`TBD after v0.18.9 publishes`.
These three fields are filled in from the published release once
Chelis-Lang/chelis#2057 lands and the v0.18.9 assets exist.

This is a rebuild, not a repair. The 0.2.11 migration for Chelis 0.18.7
already moved the negative and blocked adapter sentinels onto the compiler's
active-float dtype-family diagnostic and taught the witness and numeric
oracle gates to decode dtype-tagged exact carriers. Neither surface changes
here. No model body, precondition, numeric golden or expected tier is
weakened. No new public function needs a two-configuration acceptance case.

The offline gates run at this pin before the compiler publishes: the
manifest consistency gate (`scripts/contract_gate.py`) and the pin guard
(`scripts/audit_workarounds.py --pins-only`). The complete ten-stage local
gate (formatting, lint, package build, native tests, negative and blocked
adapters, manifest consistency, SMT proof and controls, anti-vacuity forges,
and numerical oracles) runs against the released 0.18.9 binary once it is
available; its receipts are recorded here when it does. Nine invariants
retain the `proven` expectation and one concrete f32 sensitivity retains
`fuzz_validated`.

The parked Beacon capability and the archived language issues carry over
from the 0.18.7 migration unchanged; there is no active language workaround
to retire here.

Captured commands, pins, stdout, stderr and exit codes:

- Offline gate run at the 0.18.9 pin: TBD after v0.18.9 publishes
- Complete released-compiler gate: TBD after v0.18.9 publishes
- Installer probe: TBD after v0.18.9 publishes
