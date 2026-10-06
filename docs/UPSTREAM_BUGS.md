# Upstream issues affecting Economoist

The [model guide](SUMMARY.md) states what this package checks. A suspected
compiler or Beacon gap needs a live issue citation and a minimal reproducer.
An expressible open blocker also gets an isolated `.ch` and `.expect` in
[`tests_blocked/`](../tests_blocked/README.md), with the diagnostic measured
on the pinned Chelis release.

Re-probe cadence: check **Actively blocking** at every compiler release;
**Tracking** when its stated prerequisite ships or an issue changes;
**Archived** if a regression control fails or a new symptom appears. The
commands below run from the Economoist checkout against the
[`reef.toml`](../reef.toml) pin unless stated otherwise.

## Actively blocking

(none yet)

## Tracking

- **Fixed-point and convergence proofs — chelis#2829.** The two- and
  three-state Bellman properties check a single update, including both sides
  of each output-state contraction bound. They do not check existence or
  uniqueness of a fixed point, convergence of `v_(k+1) = T(v_k)`, or a
  general-state-count theorem. Chelis#978 provides structural induction for
  a particular directly recursive scalar shape, but no proof in this package
  connects its Bellman bounds to an iteration limit. These claims stay outside
  the proven catalog; there is no `.ch` reproducer of a
  false compiler verdict. Markov stationarity, ergodicity, and arbitrary
  state-count results are also outside the catalog. Chelis#978's scalar
  induction case does not establish those economic claims. Re-probe when
  chelis#2829 supplies an applicable checked limit argument and a negative
  control; scope any general-state theorem against a concrete model before
  claiming it.

- **Larger state-space bounds — chelis#2830.** This package proves fixed two-
  and three-state instances with SMT. With the pinned compiler,
  `chelis prove properties/growth.ch --tier beacon-only --json` reports
  eight `unsupported` results for the scalar Gordon inputs because this path
  requires distinct named rank-zero `tensor[f64]` parameters; it does not establish
  large economic-state bounds. Beacon's shape-semantic tensor handling is
  tracked in beacon#52; the Chelis reporting and dispatch need is chelis#2830.
  The catalog contains the fixed-dimension claims
  and no larger-state bound claim. Re-probe when beacon#52 decides its
  tensor path and chelis#2830 can report an applicable bound.

## Archived

The closed issues below have current controls or an explicit condition for a
focused re-probe. Check them if that control fails or the named capability is
used in a new claim.

- **Released-binary SMT — chelis#422.** `scripts/prove_gate.py` requires
  `properties/` results to report `proof_tier:"smt"`, zero samples, and
  real arithmetic. Investigate any sampled or unavailable result.
- **Eval package imports — chelis#423.** `scripts/oracle_harness.py` evaluates
  the imported `gordon_pv(2, 0.1, 0.05)` through `eval --file` and expects
  `40.0`. Investigate import or value failures.
- **Scalar `max`/`min`/`abs` — chelis#424.** The Reef package binds these
  `f32` functions. Bellman exports `fmax`, `fmax3`, and `fabs` as stable
  ITE-shaped functions; a direct stdlib call needs a package-context probe
  before replacing one.
- **Maximum goal lowering — chelis#425.** The `fmax3` Bellman contraction
  goals prove and their row-sum controls refute. The corpus does not exercise
  nested `fmax(fmax(...), ...)`; probe that exact form before using it.
- **Two-call ITE lowering — chelis#426.** The Bellman two-call goals prove
  and `bellman_call_collapse_wrong` refutes. Investigate a changed verdict.
- **Import attribution — chelis#922.** `scripts/prove_gate.py` requires
  an exact property-to-export edge in the complete linker-owned
  `dependency_graph`; the flat `dependency_edges` field is insufficient.
  Missing or incomplete attribution fails the gate.
- **Scalar `grad` SMT lowering — chelis#923.** `sampled/growth_sensitivity.ch`
  checks concrete AD by fuzz, with a wrong-sign control. The separate
  `gordon_decreasing_in_r` goal proves a real-arithmetic comparison.
  A new real-gradient claim needs its own SMT and false-goal probes.
- **Package proof preparation — chelis#924.** `scripts/prove_gate.py`
  executes the sampled AD property in its Reef package. Investigate a
  timeout or package-context failure.
- **Imported gradient — economoist#13.** Both sampled Gordon properties
  differentiate the imported `gordon_pv` export. The proof gate requires
  their direct dependency edges; investigate a changed verdict or edge.
- **File-level diagnostics — chelis#967.**
  `tests_neg/parse/type_mismatch.ch` has no test declaration and must
  produce its pinned checker diagnostic under `--expect neg`. Investigate
  a configuration error or changed diagnostic.
