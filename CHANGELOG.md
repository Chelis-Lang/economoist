# Changelog

All notable changes to the Economoist shell are recorded here. The package
`version` tracks its own line (not the chelis compiler pin).

## [Unreleased]

## [0.2.15] - 2026-10-06

### Added

- `gordon_pv_checked` and `gordon_pv_strict_checked` (src/growth.ch) — the
  domain-checked Gordon entry points, returning `Option[f32]` and `None` when
  the **one rate inequality** each tests fails (`r > g` and `r > g + 0.01`
  respectively). They test that inequality and nothing else: they are not the
  hypothesis of the positivity properties, which also require `d > 0`, so
  `Some(v)` does not imply `v > 0`; they do not bound the quotient's magnitude;
  and they are weaker than the documented economic rate domain, admitting
  `r` above the published `r < 1` bound and divergent rate pairs. `Economoist.Growth` documented an `r > g`
  domain and enforced nothing, so a caller passing `r <= g` received a
  plausible-looking wrong answer rather than a signal: measured at the pin
  through the built package, `gordon_pv(1, 0.03, 0.08)` is `-20.000002` and
  `gordon_pv(1, 0.05, 0.05)` is `inf`, and `gordon_pv_strict` fails
  identically. The sibling `Economoist.Markov.make_dist` already guarded and
  returned `Option`; this brings Growth to the same convention (economoist#38).

  **The raw exports are unchanged and stay total**, for a mechanical reason
  rather than a stylistic one: `grad` rejects an `Option` result (`grad
  requires a scalar floating output, got Option f32`) and
  `sampled/growth_sensitivity.ch` differentiates the imported `gordon_pv` with
  respect to `r`, so an `Option` signature would take the AD lane out at the
  pin. The SMT goals and the `demos/businesswrong.ch` characterization gallery
  also compare the raw value against `0.0`, and
  `docs/cnote-import-surface.json` publishes `gordon_pv` under a frozen
  schema. The published C Note import surface is untouched; the new exports
  are not part of it.

  Each guard is written in its positive form, which is load-bearing:
  `if (r > g) then Some(...) else None` returns `None` for a `NaN` rate
  because every ordering comparison against `NaN` is false, so it fails
  closed, where the negated spelling states the same domain and returns
  `Some`. Eight tests cover the checked exports, every positive case with its
  negative twin; negating the guard fails the two NaN tests
  (`test_gordon_pv_checked_rejects_nan_rate`,
  `test_gordon_pv_checked_rejects_nan_growth`) and nothing else.

### Fixed

- `advance` and `advance3` no longer require transition rows to sum to exactly
  `1.0`. A row is admitted when its entries are nonnegative and its sum lies
  within `eps()` of one — the same band the `Dist2`/`Dist3` invariant carries —
  and when the masses the step computes also land inside that band. The exact
  guard refused row-stochastic matrices that sum to one in decimal but not in
  binary `f32`: on rows drawn uniformly on the simplex, written to 4 dp and
  written to 4 dp with the last entry absorbing the residual so the row sums to
  exactly one in decimal, and summed left-associated as the shipped code does,
  it refused 5.2% of individual three-state rows and, because `advance3`
  refuses the matrix if any row fails, 14.9% of three-state matrices. Under the
  band both are 0.00%. Two-state rows and matrices were refused at 0.00% under
  either guard, though `advance` is still behaviourally changed: it now admits a
  row summing to 1.00005, which the exact guard refused. (economoist#34)

- Those figures describe one population. Without the renormalization step the
  4 dp residual can itself reach or exceed `eps()`, and the band then reduces
  the per-row rejection rate rather than eliminating it: 28.96% to 0.11% at
  n=3. All of that 0.11% residual sits exactly on the tolerance edge — every
  refused row has a decimal sum of exactly 0.9999, whose `f32` sum falls one
  ulp below the `f32` band endpoint — so none of it is a genuinely
  out-of-tolerance matrix. The issue reports 4.5% at n=3 under a methodology it
  does not fully state; it is the renormalized per-row population, and the
  figures agree.

- The rate grows with the state count. That bears on the generalization
  economoist#32 asks for and not on anything shipped here, since this module
  exports `advance` and `advance3` only: there is no `advance4` or `advance7`.
  For the record, on un-renormalized rows the exact guard refused 39.87% at n=4
  and 59.08% at n=7 against the band's 0.50% and 5.37%. Every figure in these
  notes is a simulated draw that sizes the hazard; none observes it on a matrix
  a caller actually passed.

- The computed-mass band is what keeps the producer obligations discharging;
  banding only the row sums fails `invariant:Dist2:advance` and
  `invariant:Dist3:advance3` with SMT counterexamples, because a distribution
  and rows each at `1 + eps` put the output at `(1 + eps)²`. The rows the band
  newly admits are guarded at run time rather than covered by
  `markov_mass_preserved`, which still assumes exact row sums; see
  `docs/models/markov.md`.

### Changed

- Present the checked economic models, upstream issue inventory, and demo controls
  without migration drafts; require compiler-owned dependency attribution on the
  pinned toolchain and keep the file-level diagnostic under negative tests.

- Build Economoist with Chelis 0.19.0 and its bundled `chelis-std` archive.
  Repin the workflows and refresh the C Note invariant manifest for this
  package release.

### Security

- Add a pinned Git-history secret scan to pull-request and push checks, with
  contract tests.

## [0.2.14] - 2026-09-30

- Rebuild Economoist for the published Chelis 0.18.12 release. Repin the compiler, workflows,
  bundled standard-library lock, and C Note invariant expectations together.
- Keep the nine real-arithmetic proof expectations and one sampled AD
  expectation explicit. The complete local gate passed on the published
  0.18.12 compiler asset.

## [0.2.13] - 2026-09-15

- Rebuild Economoist for the published Chelis 0.18.10 release as part of the
  2026-09-15 dependency release wave. There is no functional change: no model
  body, precondition, numeric golden or expected tier moves.
- Chelis 0.18.10 is a corrective release over 0.18.9: it fixes the two 0.18.9
  regressions (chelis#2059 interpreter evaluation performance, chelis#2068
  native-C airy/ownership). Economoist never carried a perf or suite-timeout
  bandaid for those regressions, so none is reverted and none is needed at
  this pin.
- The compiler and workflow pins, package identity, regenerated lockfile, and
  C Note characterization manifest move together. All nine proven and one
  sampled invariant expectations remain explicit at the new pin.

## [0.2.12] - 2026-09-14

- Rebuild Economoist for the published Chelis 0.18.9 release as part of the
  2026-09-14 dependency release wave. There is no functional change: no model
  body, precondition, numeric golden or expected tier moves.
- Chelis 0.18.9 supersedes the unpublished 0.18.8 tag; this shell never
  pinned 0.18.8 and moves directly from 0.18.7 to 0.18.9.
- The compiler and workflow pins, package identity, and C Note
  characterization manifest move together. All nine proven and one sampled
  invariant expectations remain explicit at the new pin.

## [0.2.11] - 2026-09-13

- Adopt the published Chelis 0.18.7 release and regenerate compiler-bound
  artifacts for the C Note dependency release wave.
- Refresh the bare file-level diagnostic sidecars for the active-float dtype
  check. Decode exact f32/f64 scalar and rank-zero tensor eval carriers in the
  witness and numerical gates, preserving signed zero and rejecting malformed
  bit widths. This repairs economoist#22 without changing economic models.
- The complete ten-stage local gate passes on the released compatibility
  binary, including SMT controls, anti-vacuity forges and numerical oracles.
  All nine proven and one sampled invariant expectations remain explicit.

## [0.2.10] - 2026-08-23

- Prepare Economoist 0.2.10 for Chelis 0.18.5. The compiler and workflow pins,
  package identity, lockfile, and C Note characterization manifest move
  together; all ten invariant tiers remain explicit at the new pin.
- The v0.18.5 source tag resolves to
  `6602f01719f55b8d4c7f52ee70e7c7b58f136107`. The official glibc release
  asset has publisher SHA-256
  `6b9b944ccd96b0053fc071de0ecfbb9e80e02a07a6a176e87056267ae8e0c26a`.
- Re-verify the complete package, import, proof, anti-vacuity, and numeric
  oracle surfaces with the official 0.18.5 release binary. The honest boundary
  remains nine real-arithmetic properties expected `proven` and one concrete
  `f32` Gordon sensitivity expected `fuzz_validated`.
- None of the three Chelis 0.18.5 breaking changes reaches this shell. It
  declares no polymorphic recursion, writes no integer literal in a bare type
  position, and every operand of a `>` comparison in `src/`, `properties/`,
  `demos/`, and `sampled/` is a pure `f32` expression, so the new
  left-to-right operand evaluation order is unobservable here.

## [0.2.9] - 2026-08-20

- Prepare Economoist 0.2.9 for Chelis 0.18.4. The compiler and workflow pins,
  package identity, lockfile, and C Note characterization manifest move
  together; all ten invariant tiers remain explicit at the new pin.
- The v0.18.4 source tag resolves to
  `c0138c828bf2c42e1c8941e824f16616bd974fd5`. The official glibc release
  asset has publisher SHA-256
  `c31b59a830ca232fa4e0a454e1314810026b5ec4f2b1a6e54d024eb049f65902`.
- Re-verify the complete package, import, proof, anti-vacuity, and numeric
  oracle surfaces with the official 0.18.4 release binary. The honest boundary
  remains nine real-arithmetic properties expected `proven` and one concrete
  `f32` Gordon sensitivity expected `fuzz_validated`.

## [0.2.8] - 2026-08-01

- Prepare Economoist 0.2.8 for Chelis 0.18.1. The compiler and workflow pins,
  package identity, and C Note characterization manifest move together; all ten
  invariant tiers remain explicit at the new pin.
- The v0.18.1 source tag resolves to
  `c8db387d06d538ce8039ac37645a43def48373c9`. The official glibc release asset
  has publisher SHA-256
  `88a1a53b47b7168e4df614e66a6d9313176174b1dc3a25a43db5f73a3ee8f0cd`.
- Retire the stale eval-import narrowing (chelis#423). The official 0.18.1
  binary resolves an ad hoc `eval --file` snippet through the current Reef
  package, so numeric and defective-model controls now import and execute the
  shipped exports instead of reconstructing their source bodies.
- Retain the honest proof boundary: nine real-arithmetic properties are
  expected `proven`, while the concrete `f32` Gordon sensitivity remains
  `fuzz_validated` and is not promoted by the compiler bump.

## [0.2.6] - 2026-07-31

### Changed

- **The Gordon AD sensitivity now differentiates the shipped export directly
  (economoist#13).** Both the satisfying property and its sign-flipped corrupt
  twin call imported `Economoist.Growth.gordon_pv`; the manifest binding is
  `direct`, not `equivalent-form`.
- **The sampled proof gate now exercises the real Reef package context.** The
  fuzz-only, 500-sample lane no longer copies source into a standalone
  temporary package. Economoist#13 established direct imported-grad execution
  at the 0.17.1 pin; chelis#924 removes the remaining package-sized fixed
  cost, and the published 0.17.4 asset repeats the real-package proof gate.
- **Direct bindings consume compiler attribution.** From Chelis 0.17.2 onward,
  the proof gate requires chelis#922's linker-owned `dependency_graph` and fails closed on
  a complete graph without the required property-to-model edge. The official
  0.17.4 release asset passes the complete dependency-attributed proof gate.
- **Prepared the Chelis 0.17.4 / Economoist 0.2.6 release cascade.** The
  compiler pin, workflow installers, lockfile, manifest package/pin fields,
  and every expected-tier row move together. Chelis 0.17.2 supplied the
  dependency, gradient, and package-context capabilities, but its auto-batch
  test worker can outlive the useful per-test timeout (chelis#927). The 0.17.4
  release bounds that suite lifetime, and its official SMT-bearing
  compatibility asset passes all ten local-gate stages. The forge negative's
  temporary package now derives its
  compiler pin from the binary under test instead of retaining a historical
  0.14.0 pin, so its ACCEPT/REJECT oracle actually executes at every new pin.
- **Retired the expected-failure fallback (chelis#967).** Negative and blocked
  suites now run exclusively through `chelis test <dir> --expect neg|blocked`.
  The negative corpus includes a bare file-level check failure, proving the
  compiler-owned adapter preserves its pinned diagnostic; the duplicate Python
  runners and CI fallback chain are gone.
- **Archived the stale scalar-intrinsic blocker (chelis#424).** Real Reef
  executable probes show scalar `max` and `min` compile and pass with the
  published 0.17.4 toolchain. The old adapter copied the probe outside its Reef dependency
  context and falsely kept reporting `unbound variable`. Stable exported
  `fmax`/`fmax3`/`fabs` helpers remain for API and proof-corpus compatibility,
  not as a narrowing.
- **Release acquisition now selects and authenticates the compatibility
  artifact.** Linux automation installs
  `linux-x86_64-glibc2.31`, verifies the publisher's SHA-256 sidecar before
  extraction, and rotates the cache namespace. The local installer
  reauthenticates on every invocation and rolls back a failed replacement
  without destroying the prior toolchain.

## [0.2.3] - 2026-07-13

Metamorphic anti-vacuity hardening: close the forge surface the red-team defeated
engine-side, in the shell gate itself.

### Added
- **Metamorphic anti-vacuity check in `prove_gate.py`.** The syntactic
  "goal calls the output fn" check is forgeable — a canceling call
  `F(x) - F(x) < c` or a reflexive `F(x) == F(x)` references `F` textually and
  passes both it and an honest violating control, yet is true for any `F`. For
  each `properties/` proven, direct-call invariant the gate now re-proves the
  goal with the referenced output fn's body substituted by distinct alternative
  bodies and requires the verdict to CHANGE (proven → disproved) under at least
  one substitution; a green that survives every substitution is model-independent
  and fails the gate. Strictly stronger than the goal-string + corrupt-flip pair.
- **`scripts/run_forge_tests.py`** — executable forge negatives: a throwaway
  package with canceling and reflexive greens (must be rejected) plus an honest
  green (must be accepted), asserting the metamorphic check behaves. Wired into
  `run_local_gate.py` and the `prove-gate` CI job.

## [0.2.2] - 2026-07-13

Honest close of a real hole a red-team forge found: the manifest under-declared
preconditions, so a consumer could derive a validity region wider than the proof
covers (a non-stochastic witness `p00 = -1` claimed in-region).

### Fixed
- **Completed under-declared preconditions.** `econ.inv.bellman_monotone.v1` and
  `econ.inv.bellman_contraction.v1` each gain their four `p** >= 0.0`
  nonnegativity guards; `econ.inv.bellman3_contraction.v1` gains its six. Every
  invariant's declared `preconditions` now exactly match the referenced
  property's full where-clause. (No proof changed — the properties always carried
  these guards; only the manifest under-declared them.)

### Added
- **contract_gate.py completeness check.** For each invariant, the gate now
  parses the referenced property's where-clause and asserts the declared
  preconditions COVER every guard (declared ⊇ where-clause), not merely that each
  declared guard appears in the where-clause (⊆). Under-declaration now fails the
  gate, naming the missing guard. Negative-tested.

## [0.2.1] - 2026-07-12

### Added
- `gordon_pv_strict` (src/growth.ch) — the conservative margin-of-safety Gordon
  variant: the same closed form as `gordon_pv`, but with a documented strict
  domain of use `r > g + 0.01`. Manifest model `gordon_strict` and invariant
  `econ.inv.gordon_strict_positive.v1` (preconditions `d > 0` AND `r > (g + 0.01)`,
  proven), with `nests_inside: econ.inv.gordon_positive.v1`.
- Its proven positivity region `{d>0, r>g+0.01}` nests strictly inside gordon's
  `{d>0, r>g}` — a proof-backed org implication (strict -> standard) the
  characterization consumer surfaces as a candidate. `properties/growth.ch` gains
  `gordon_strict_positive` + its `_guards_satisfiable` witness;
  `demos/businesswrong.ch` gains the out-of-region twin
  `gordon_strict_positive_wrong`/`_control`.
- Manifest preconditions now support an `{expr}` RHS (e.g. `g + 0.01`), written
  left-associated to match the prover's canonical where-clause text; contract_gate
  and prove_gate evaluate it.

## [0.2.0] - 2026-07-10

The econ canon: honest, output-referencing invariants under the characterization
contract (`chelis-shell.invariant-surface/1.0`), plus three de-narrowings
verified against the pinned 0.14.0 release binary.

### Added
- `docs/cnote-import-surface.json` restructured to the invariant-surface manifest
  (schema `chelis-shell.invariant-surface/1.0`): 6 models (including the
  defective `gordon_mispriced`) and 9 invariants with per-pin expected tiers,
  controls, and preconditions. Published as the release asset
  `economoist-0.2.0.invariants.json` via `release.yml`.
- `scripts/contract_gate.py` -- offline manifest-consistency gate (contract §3).
- `sampled/` lane (module prefix `Economoist.Sampled`): the fuzz-validated AD
  sensitivity `gordon_dP_dr_negative_grad` (honest amber), gated separately from
  the `properties/` green boundary.
- Defective reference model `gordon_pv_negated` (a mispriced perpetuity) and the
  in-region-defect twin `gordon_pv_corrupted_wrong`/`_control`, with an
  f32-confirmed in-domain witness.
- `bellman_call_collapse_wrong`/`_control` regression control pair guarding the
  chelis#426 de-narrowing.

### Changed
- **Gordon (anti-vacuity):** `gordon_positive`, `gordon_increasing_in_d`,
  `gordon_decreasing_in_r` now CALL the exported `gordon_pv` (positivity once;
  comparative statics as two-point calls) instead of restating their guards in
  multiplied-through polynomial form. Verified unqualified SMT greens
  (cnote.dischargeability p01/p02/p03).
- **chelis#426 de-narrow:** `properties/bellman.ch` goals now call
  `bellman_state0`/`bellman_state1`/`_n3` directly instead of inlining the
  operator arithmetic. `scripts/prove_gate.py` evolved to be manifest-driven
  (expected-tier enforcement classified from proof_tier + assumptions +
  qualifiers, never `composite_verdict`); the `unsound_pattern_lint` was removed.
- **chelis#425 de-narrow:** the n=3 per-output-state Bellman sup-norm contraction
  (state 0/1/2, upper and lower) now ships as SMT green; it was previously held
  out. Verified via p15 and the per-surface proofs.
- CI: a `contract-gate` job (offline) runs per-PR; fmt/lint cover `sampled/`.

### Removed
- The vacuous derivative-sign greens `gordon_dP_dr_negative` /
  `gordon_dP_dg_positive` (guard restatements). The dP/dr sign now ships as the
  proven two-point `gordon_decreasing_in_r` green plus the fuzz-validated AD
  `gordon_dP_dr_negative_grad`.

### Upstream
- Archived chelis#425 and chelis#426 (resolved; re-verified at 0.14.0).
- Re-probed chelis#424 at 0.14.0: scalar `abs` for f32 now binds; `max`/`min`
  still unbound (the `fmax`/`fmax3` workaround still ships) -- stays tracking.
- New drafts: `grad_through_import.md`, `grad_smt_lowering.md`,
  `dependency_edges_imports.md`.

## [0.1.4] - prior
- chelis pin 0.11.1 -> 0.14.0; release-binary SMT prove gate (chelis#422).
