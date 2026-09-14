# Chelis 0.18.9 migration

Economoist 0.2.12 participates in the compiler-compatible C Note dependency
release wave for Chelis 0.18.9. It uses the published compiler; no compiler
source build or local compiler patch is required. Chelis 0.18.9 supersedes
the unpublished 0.18.8 tag, so this shell moves directly from 0.18.7 to
0.18.9 with no functional change.

The compiler tag resolves to `abff07b47eadc8d2be633e3a7d21220089befb6f`.
The sidecar-verified Linux glibc-2.31 archive SHA256 is
`9aed0afbfc93a96a6804b4c82664869d74815bd27ca824dfeab02088b00ddb63`;
the compiler payload SHA256 is
`efe99c09f5d7d7372065206a332a2fd86b8aee77412262b0028cfbdbc98a19f2`.
These three fields come from the published v0.18.9 release
(Chelis-Lang/chelis#2057 landed; release run 34843914490). The darwin-arm64
archive used for the local gate on this workstation is
`44e12cf187b37cb6d2a617e1573832a1bdcaa0e1564f59c4029e24081a84905d`.

This is a rebuild, not a repair. The 0.2.11 migration for Chelis 0.18.7
already moved the negative and blocked adapter sentinels onto the compiler's
active-float dtype-family diagnostic and taught the witness and numeric
oracle gates to decode dtype-tagged exact carriers. Neither surface changes
here. No model body, precondition, numeric golden or expected tier is
weakened. No new public function needs a two-configuration acceptance case.

The offline gates ran at this pin before the compiler published: the
manifest consistency gate (`scripts/contract_gate.py`) and the pin guard
(`scripts/audit_workarounds.py --pins-only`). `reef.lock` was regenerated
by `chelis reef build` under the published 0.18.9 compiler in an isolated
`CHELIS_HOME`; only the compiler pin, the package version, and the bundled
chelis-std archive and shell hashes changed. The complete ten-stage local
gate (formatting, lint, package build, native tests, negative and blocked
adapters, manifest consistency, SMT proof and controls, anti-vacuity forges,
and numerical oracles) ran against the released 0.18.9 darwin-arm64 binary;
its receipt is recorded below. Nine invariants retain the `proven`
expectation and one concrete f32 sensitivity retains `fuzz_validated`.

The parked Beacon capability and the archived language issues carry over
from the 0.18.7 migration unchanged; there is no active language workaround
to retire here.

Captured commands, pins, stdout, stderr and exit codes:

- Offline gate run at the 0.18.9 pin: `scripts/contract_gate.py` and
  `scripts/audit_workarounds.py --pins-only`, both green, re-run inside the
  complete gate receipt below (stage 7 and the pin guard).
- [Complete released-compiler gate](https://github.com/Chelis-Lang/sonar/tree/main/landing/runs/g8-economoist-local-gate-0189)
  (`scripts/run_local_gate.py` against the published 0.18.9 darwin-arm64
  binary, isolated `CHELIS_HOME`).
- Installer probe: `scripts/install_chelis_toolchain.py` downloads the Linux
  glibc-2.31 asset and executes its `--version`, which a darwin workstation
  cannot run. The equivalent install-and-verify of that asset (sidecar SHA256
  check and `chelis 0.18.9` assertion) is performed by the
  `.github/actions/install-chelis` step of the `Chelis gate` job on
  [economoist#24](https://github.com/Chelis-Lang/economoist/pull/24).
