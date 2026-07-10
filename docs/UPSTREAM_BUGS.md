# Economoist Upstream Bugs

Tracked upstream chelis issues and capability gaps that affect Economoist, per
the downstream shell repo contract section 4.

Re-probe cadence: **actively-blocking** entries are re-probed at every chelis
release; **tracking** entries when upstream signals movement; **parked** entries
when their gating dependency ships or a concrete need appears; **archived**
entries are historical. Executable probes live under `../tests_blocked/` where a
blocker is mechanically expressible; items that cannot be probed in-package are
listed in that README for manual re-probe.

Suspected chelis issues are cited as `chelis#NNN` or as a parked draft under
`issue_drafts/`, never by a prose name.

## Actively blocking

None. Every economic property in this shell discharges as an unqualified SMT
green at the pinned binary. The two-call ITE soundness bug (chelis#426) and the
nested-fmax lowering gap (chelis#425) that once contained this surface are both
resolved at the 0.14.0 pin and archived below; nothing upstream blocks shipping
the current surface.

## Tracking

- **eval does not resolve imports for standalone files.** `prove` resolves module
  imports, so the proven properties reach the real exported functions, but `eval`
  on a standalone file does not resolve a package import. Affected surface: a C
  Note template that needs to numerically `eval` a shell model must inline the
  model's single-expression body until eval-side import resolution lands. The
  proof surface is not blocked by this. Workaround: inline the displayed
  single-expression body (the oracle harness evals inline lambdas identical to the
  shipped bodies). Re-probe trigger: any release note naming eval-side import
  resolution. chelis#423 (draft: `issue_drafts/eval_side_import_resolution.md`).

- **Partial scalar `max`/`min`/`abs` for `f32`: `abs` binds, `max`/`min` still
  unbound.** First observed at 0.8.0 (a bare `max(...)` over `f32` is an unbound
  variable). Re-probed at the 0.14.0 pin on 2026-07-10: `abs` over `f32` now binds
  and proves smt-green, but `max` and `min` over `f32` remain unbound (typecheck
  error "unbound variable"). Affected surface: the Bellman operator and the
  sup-norm contraction, which take a max over actions. Workaround: the local
  `fmax`/`fmax3` `if/then/else` helpers still ship for the max (they lower as ITE
  and prove smt-green); the local `fabs` is kept for symmetry with `fmax` even
  though `abs` now binds. Status stays **Tracking**: do not claim `max`/`min` are
  fixed. Re-probe trigger: any release note adding scalar `max`/`min` reductions
  over `f32` to chelis-std. chelis#424 (draft: `issue_drafts/scalar_max_abs_f32.md`).

- **grad goals do not lower to the SMT tier (AD sensitivity is fuzz-only).** A
  `@property` goal whose body contains `grad(...)` degrades to fuzz at `--tier
  auto` and reports `unsupported` at `--tier smt-only`; there is no unqualified
  SMT green for an AD-derivative sign fact. Affected surface: the Gordon
  comparative-static dP/dr < 0, which therefore ships in the sampled lane
  (`sampled/growth_sensitivity.ch`, `gordon_dP_dr_negative_grad`, `fuzz_validated`
  amber) rather than in the proven `properties/` boundary. The same economic
  content is available as an unqualified SMT green via the two-point form
  `gordon_decreasing_in_r` over the reals; the grad lane is the AD confirmation at
  a point, not a proof. Workaround / tier-upgrade trigger: when grad goals lower
  to SMT the sampled invariant is re-probed and its expected tier bumped from
  `fuzz_validated` to `proven` (a de-narrowing event). Draft:
  `issue_drafts/grad_smt_lowering.md` (not yet filed; cite the path).

- **grad does not lower through a cross-module import call (hangs).**
  `grad(fn (...) -> imported_fn(...), wrt=...)` inside a `@property` goal makes no
  progress when `imported_fn` is imported from another module of the same package:
  `chelis prove` hangs with no verdict and no error, whereas the identical grad
  expression with the callee body inlined lowers and fuzz-validates promptly.
  Affected surface: the sampled AD-sensitivity lane, which wants to differentiate
  the exported `Economoist.Growth.gordon_pv`. Workaround: the sampled property
  inlines gordon_pv's shipped single-expression body `(d / (r - g))` (single-
  expression discipline; the manifest marks the binding
  `references_output_fn: "equivalent-form"` and the oracle harness pins the inline
  body against gordon_pv's numeric goldens so it cannot drift). Re-probe trigger:
  grad-through-import still hangs at the next release. Draft:
  `issue_drafts/grad_through_import.md` (not yet filed; cite the path).

- **prove --json `dependency_edges` omits cross-module import references.** The
  `dependency_edges` array lists only calls to defs in the same file; a call to a
  function imported from another module resolves and proves but does not appear in
  the array (it is `[]`). Affected surface: the characterization-contract
  anti-vacuity check for proven properties, which import their output fns from
  `src/`. Workaround: `scripts/prove_gate.py` verifies anti-vacuity from the
  prover-emitted `goal` string (which does carry the mangled imported reference)
  plus the corrupt-flip control, a stronger guarantee than `dependency_edges`
  alone. Re-probe trigger: `dependency_edges` still omits import references at the
  next release. Draft: `issue_drafts/dependency_edges_imports.md` (not yet filed;
  cite the path).

## Parked

- **Induction for limit and general-n results.** Convergence to stationarity, the
  unique Bellman fixed point, ergodicity, value-iteration convergence, and the
  general state-dimension theorems need induction or a fixed-point argument and
  are not reachable by SMT at fixed size. Re-probe trigger: an induction or
  proof-assistant tier in chelis.

- **Large concrete state-space verification.** Scaling concrete verification past
  the small fixed dimension SMT can handle is the Beacon roadmap (bound
  propagation and abstract interpretation). Re-probe trigger: Beacon availability.

## Archived

- **SOUNDNESS: two-call comparison/subtraction of an ITE-bodied def false-proves.
  RESOLVED (chelis v0.10.0).** A goal that compared or subtracted two calls of the
  same `fmax`-bodied operator def (with different args) collapsed to the
  all-arguments-equal corner, so a false goal reported `proven` at the SMT tier
  with no counterexample; this made the first cut of the Bellman
  contraction/monotonicity greens vacuous. Fixed upstream at chelis 0.10.0 and
  re-verified at the 0.14.0 pin on 2026-07-10 via probe p04 (the satisfying
  two-call goal proves; the corrupted twin refutes with a counterexample).
  Consequently `properties/bellman.ch` now calls `bellman_state0`/`bellman_state1`
  (and the `_n3` variants) DIRECTLY at the goal site instead of inlining the
  `fmax(...)` arithmetic, and the `unsound_pattern_lint` in `scripts/prove_gate.py`
  was deleted. A regression control pair `bellman_call_collapse_wrong` /
  `bellman_call_collapse_control` was added to `demos/` to keep the fixed behavior
  under watch. chelis#426 (draft:
  `issue_drafts/twocall_ite_subtraction_unsound.md`).

- **Nested fmax-style helper calls at a goal site do not lower to Tier B; the n=3
  contraction was consequently held out. RESOLVED / CANDIDATE-FIXED (chelis
  0.14.0).** A three-way maximum written with the `fmax3` ternary sup at a goal
  site, combined with the n=3 operator arithmetic on the left, previously reported
  `unsupported` at Tier B, so the full n=3 per-output-state sup-norm contraction
  was held out. Candidate-fixed at 0.14.0 and verified via probe p15 and
  per-surface: the full n=3 per-output-state Bellman sup-norm contraction now
  PROVES at SMT -- `bellman_contraction_state0_n3`, `bellman_contraction_state1_n3`,
  `bellman_contraction_state2_n3`, each upper AND lower (6 unqualified SMT greens
  plus 6 `*_guards_satisfiable` witnesses that refute), with the `fmax3`
  three-coordinate sup on the right and the two-call `bellman_state0_n3`
  subtraction on the left. This was PREVIOUSLY HELD OUT; it is now de-narrowed and
  ships green (see `docs/models/bellman.md`). Held out still: value-iteration
  convergence, the fixed point, and the general-`n` theorem (they need induction;
  see Parked). chelis#425 (draft: `issue_drafts/nested_fmax_goal_site.md`).

- **SMT prove was absent from the released chelis tarball. RESOLVED (chelis
  v0.11.0).** `chelis prove` historically reached the SMT tier only in a
  from-source `--features smt` build (linked against cvc5); the released tarball
  was fuzz-only and silently degraded an inequality goal to a sampled pass, which
  for this shell would have turned every economic green amber. SMT now ships in
  the released binary as of chelis v0.11.0. Verified at the pinned 0.14.0 release
  binary on 2026-07-10: `scripts/prove_gate.py` is fully green (every property
  `proof_tier: smt`, `samples: 0`, unqualified verdict) run against
  `~/.local/share/chelis/0.14.0/bin/chelis`. Consequently the prove gate, `ci.yml`,
  and `nightly.yml` run on the release binary; the from-source build and
  `scripts/build_chelis_smt.py` were removed. chelis#422 (draft:
  `issue_drafts/smt_in_release_tarball.md`).
