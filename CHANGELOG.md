# Changelog

All notable changes to the Economoist shell are recorded here. The package
`version` tracks its own line (not the chelis compiler pin).

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
