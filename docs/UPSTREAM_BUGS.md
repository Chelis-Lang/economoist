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
green at the pinned binary, and the one soundness bug below is contained by an
enforced workaround; nothing upstream blocks shipping the current surface.

## Tracking

- **SOUNDNESS: two-call comparison/subtraction of an ITE-bodied def false-proves.**
  A goal that compares or subtracts two calls of the same `fmax`-bodied operator
  def (with different args) collapses to the all-arguments-equal corner, so a
  false goal reports `proven` at the SMT tier with no counterexample. This made the
  first cut of the Bellman contraction/monotonicity greens vacuous. Affected
  surface: any max-style operator contraction/monotonicity. Workaround: inline the
  operator arithmetic at the goal site (never call an ITE-bodied operator twice in
  a goal); `scripts/prove_gate.py` `unsound_pattern_lint` enforces this
  structurally. Re-probe trigger: any release note on prove-tier lowering or
  two-call expression handling. chelis#426 (draft:
  `issue_drafts/twocall_ite_subtraction_unsound.md`). This is the most serious
  upstream issue this shell has hit; re-probe the reproducer every release.

- **Nested fmax-style helper calls at a goal site do not lower; the n=3
  contraction is consequently held out.** A three-way maximum written as nested
  `fmax` at a goal site does not lower; the `fmax3` ternary helper lowers in
  isolation but the n=3 single-application contraction goal as a whole (n=3
  operator arithmetic plus the `fmax3` sup) still reports `unsupported`. Affected
  surface: the n=3 Bellman sup-norm contraction, which is held out (see
  `docs/models/bellman.md`). Workaround: ship the n=2 per-output-state
  contractions; hold out the n=3 contraction. Re-probe trigger: any release note
  on prove-tier lowering or goal-site inlining. chelis#425 (draft:
  `issue_drafts/nested_fmax_goal_site.md`).

- **eval does not resolve imports for standalone files.** `prove` resolves module
  imports, so the proven properties reach the real exported functions, but `eval`
  on a standalone file does not resolve a package import. Affected surface: a C
  Note template that needs to numerically `eval` a shell model must inline the
  model's single-expression body until eval-side import resolution lands. The
  proof surface is not blocked by this. Workaround: inline the displayed
  single-expression body (the oracle harness evals inline lambdas identical to the
  shipped bodies). Re-probe trigger: any release note naming eval-side import
  resolution. chelis#423 (draft: `issue_drafts/eval_side_import_resolution.md`).

- **No bound scalar `max`/`min`/`abs` for `f32`.** First observed at 0.8.0 (a bare
  `max(...)` over `f32` is an unbound variable); not re-probed at the current
  0.14.0 pin, where the local-helper workaround still ships. Affected surface: the
  Bellman operator and the sup-norm contraction. Workaround: define local
  `fmax`/`fabs` with `if/then/else` (they lower as ITE and prove smt-green).
  Re-probe trigger: any release note adding scalar reductions over `f32` to
  chelis-std. chelis#424 (draft: `issue_drafts/scalar_max_abs_f32.md`).

- **Nested `fmax`-style helper calls at a property goal site do not lower to
  Tier B.** A goal that nests local `fmax` helper calls (e.g. `fmax(fmax(a, b), c)`
  for an n=3 maximum) at the property goal site does not lower to the SMT tier and
  drops to fuzz, even though each helper lowers as ITE in isolation. Affected
  surface: the n=3 Bellman sup-norm contraction, whose goal takes a three-way
  maximum over the per-state deviations. Workaround: the flattened `fmax3` ternary
  helper (one nested `if/then/else` over the three arguments, no helper-of-helper
  call at the goal site), which lowers to ITE and proves smt-green. Re-probe
  trigger: any release note on prove-tier lowering or goal-site inlining of
  helper calls. chelis#425 (draft: `issue_drafts/nested_fmax_goal_site.md`).

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
