# Changelog

All notable changes to the Economoist shell are recorded here. The package
`version` tracks its own line (not the chelis compiler pin).

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
- **Direct bindings consume compiler attribution when available.** The proof
  gate prefers chelis#922's linker-owned `dependency_graph` and fails closed on
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
