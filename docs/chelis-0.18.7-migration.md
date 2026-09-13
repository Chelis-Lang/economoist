# Chelis 0.18.7 migration

Economoist 0.2.11 participates in the compiler-compatible C Note dependency
release wave. It uses the published compiler; no compiler source build or
local compiler patch is required.

The compiler tag resolves to `4109f8fdd1eef764ef91bb6d138401b351a2e1db`.
The sidecar-verified Linux glibc-2.31 archive SHA256 is
`bbaabf8e2d1517262f0e94d1574af455d4adb68d422929312d109857030db11c`;
the compiler payload SHA256 is
`33f0919ca8a6f350c05a02f89703a840ad45e63ee59caf5d9f6be6698eb5d2b0`.
The repository installer also installed that payload with its destination
relocated to isolated scratch storage.

Two migration failures were recorded before their repairs. The negative and
blocked adapter sentinels pinned the old bool-versus-f32 diagnostic. Their
sidecars now name the compiler's active-float dtype-family rejection. They
continue to exercise bare file-level diagnostics, and the blocked sentinel
is explicitly an adapter regression rather than an open language blocker.
The witness gate also treated an exact eval carrier as a JSON number. Both
the witness re-execution and numeric oracle now decode the dtype-tagged bits;
tests cover scalar and rank-zero carriers, signed zero and malformed widths.

The complete ten-stage local gate passes: formatting, lint, package build,
native tests, negative and blocked adapters, manifest consistency, SMT proof
and controls, anti-vacuity forges, and numerical oracles. Nine invariants retain
the `proven` expectation and one concrete f32 sensitivity retains
`fuzz_validated`. No model body, precondition, numeric golden or expected tier
was weakened. No new public function needs a two-configuration acceptance case.

The parked Beacon capability was re-probed against `properties/growth.ch`.
It returns structured unsupported for the existing f32 inputs, which do not
fit the named rank-zero tensor[f64] NN lane. This does not establish larger
economic state-space verification or induction. The archived language issues
remain historical; there is no active language workaround to retire here.

Captured commands, pins, source patches, stdout, stderr and exit codes:

- [Initial diagnostic drift](https://github.com/Chelis-Lang/sonar/tree/main/landing/runs/g5-economoist-canonical-bump)
- [Passing repaired bump](https://github.com/Chelis-Lang/sonar/tree/main/landing/runs/g5-economoist-canonical-bump-repair)
- [Exact-carrier failing oracle](https://github.com/Chelis-Lang/sonar/tree/main/landing/runs/g5-economoist-wire-decoder-red)
- [Exact-carrier passing tests](https://github.com/Chelis-Lang/sonar/tree/main/landing/runs/g5-economoist-wire-decoder-green)
- [Complete released-compiler gate](https://github.com/Chelis-Lang/sonar/tree/main/landing/runs/g5-economoist-full-release-gate-v2)
- [Installer probe](https://github.com/Chelis-Lang/sonar/tree/main/landing/runs/g5-economoist-published-installer)
- [Beacon surface re-probe](https://github.com/Chelis-Lang/sonar/tree/main/landing/runs/g5-economoist-beacon-surface-reprobe)
