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

Current validation: the official Chelis 0.18.12 binary passed the complete
ten-stage local gate on 2026-09-30; [the migration record](chelis-0.18.12-migration.md)
records its asset and lock provenance.
The nine proven and one sampled expected tiers remain unchanged.

## Actively blocking

None. Every economic property in this shell discharges as an unqualified SMT
green at the pinned binary. The two-call ITE soundness bug (chelis#426) and the
nested-fmax lowering gap (chelis#425) that once contained this surface are both
resolved at the 0.14.0 pin and archived below; nothing upstream blocks shipping
the current surface.

## Tracking

None.

## Parked

- **Induction for limit and general-n results.** Convergence to stationarity, the
  unique Bellman fixed point, ergodicity, value-iteration convergence, and the
  general state-dimension theorems need induction or a fixed-point argument and
  are not reachable by SMT at fixed size. Re-probe trigger: an induction or
  proof-assistant tier in chelis. Parked rationale:
  `docs/issue_drafts/induction_fixed_point.md`.

- **Large concrete state-space verification.** Scaling concrete verification past
  the small fixed dimension SMT can handle is the Beacon roadmap (bound
  propagation and abstract interpretation). The official 0.18.12 re-probe of
  `properties/growth.ch` returns eight structured `unsupported` records because
  the NN lane requires distinct named rank-zero tensor[f64] inputs.
  Re-probe trigger: a published bound lane that can consume these economic models.
  Parked rationale: `docs/issue_drafts/large_state_space_beacon.md`.

## Archived

- **Eval-side package import resolution works in Chelis 0.18.1 (chelis#423).**
  Re-probed with the official release binary using an ad hoc file outside `src/`
  that imports `Economoist.Growth.gordon_pv`; `chelis eval --file` resolves the
  current Reef package and returns `40.0`. The numeric oracle and defective-model
  witness gate now import and execute shipped exports directly. Their old
  source-body reconstruction is removed.

- **Scalar `max`/`min`/`abs` for `f32` bind in Chelis 0.17.4 (chelis#424).**
  Real-Reef executable probes against the published 0.17.4 release asset
  compile and pass for both `max(f32, f32)` and `min(f32, f32)`; `abs` was
  already verified at 0.14.0. The old blocker copied its source into a
  dependency-free standalone directory, so it kept reporting `unbound
  variable` after the package surface was usable. That misleading adapter
  probe is removed. Exported `fmax`/`fmax3`/`fabs` remain stable shell API and
  preserve the audited ITE-shaped proof corpus, not a capability narrowing.

- **Native expected-failure runner preserves bare check-time diagnostics in
  Chelis 0.17.4 (chelis#967).** Re-probed against the published 0.17.4 release:
  the bare `tests_neg/parse/type_mismatch.ch` file, which deliberately
  declares no `test_*` function, is classified `verdict:"ok"` with its pinned
  diagnostic. CI and the local gate now use only
  `chelis test <dir> --expect neg|blocked`; the two Python adapters and the
  fallback chain are removed. A genuinely clean testless file remains a
  configuration error upstream, so this de-narrowing stays fail-closed.

- **Compiler-owned dependency attribution shipped in Chelis 0.17.2
  (chelis#922).** The published 0.17.4 gate observes a complete
  linker-owned graph and direct stable-ID edges from both sampled Gordon
  properties to `Economoist.Growth.gordon_pv`. The gate fails closed if a
  complete graph omits either edge. The older flat `dependency_edges` field
  still omits cross-module references, but it is now a compatibility field
  rather than a narrowing: the compiler-owned graph supersedes it.

- **Scalar-grad SMT lowering shipped in Chelis 0.17.2 (chelis#923).** The
  supported real-arithmetic lane is available. Economoist intentionally keeps
  its concrete `f32` AD characterization fuzz-validated and its mathematical
  monotonicity theorem separately SMT-proven.

- **Persistent package prove preparation shipped in Chelis 0.17.2
  (chelis#924).** Economoist's sampled gate now executes the checked-in
  direct-import property in its real Reef package context. The complete
  ten-stage gate passes with the official 0.17.4 compatibility asset.

- **Direct grad through an imported function. RESOLVED at the 0.17.1 pin
  (economoist#13).** A two-module package re-probe returned a fuzz verdict whose
  compiler-emitted goal directly contained the imported function call.
  Economoist now differentiates `Economoist.Growth.gordon_pv` directly in both
  the satisfying property and corrupt sign twin; the manifest binding is
  `direct`. The distinct package-latency and scalar-grad-SMT issues remain
  tracked above as chelis#924 and chelis#923. Historical probe:
  `issue_drafts/grad_through_import.md`.

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
