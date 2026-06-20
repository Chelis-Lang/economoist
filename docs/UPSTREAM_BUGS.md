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
green at the pinned binary; nothing upstream blocks shipping the current surface.

## Tracking

- **SMT prove is absent from the released chelis tarball.** `chelis prove` only
  reaches the SMT tier when the binary is built `cargo build --release -p
  chelis-cli --features smt` (linked against cvc5). The released tarball is
  fuzz-only and silently degrades an inequality goal to a sampled pass, which for
  this shell would turn every economic green amber. Affected surface: the whole
  proof story. Workaround: build the SMT binary from source
  (`scripts/build_chelis_smt.py`) and run the prove gate against it; CI builds it
  in the `smt-prove-gate` job. Re-probe trigger: any release note shipping the
  `smt` feature in the published tarball. Draft: `issue_drafts/smt_in_release_tarball.md`.

- **eval does not resolve imports for standalone files.** `prove` resolves module
  imports, so the proven properties reach the real exported functions, but `eval`
  on a standalone file does not resolve a package import. Affected surface: a C
  Note template that needs to numerically `eval` a shell model must inline the
  model's single-expression body until eval-side import resolution lands. The
  proof surface is not blocked by this. Workaround: inline the displayed
  single-expression body (the oracle harness evals inline lambdas identical to the
  shipped bodies). Re-probe trigger: any release note naming eval-side import
  resolution. Draft: `issue_drafts/eval_side_import_resolution.md`.

- **No bound scalar `max`/`min`/`abs` for `f32`.** At 0.8.0 a bare `max(...)` over
  `f32` is an unbound variable. Affected surface: the Bellman operator and the
  sup-norm contraction. Workaround: define local `fmax`/`fabs` with `if/then/else`
  (they lower as ITE and prove smt-green). Re-probe trigger: any release note
  adding scalar reductions over `f32` to chelis-std. Draft:
  `issue_drafts/scalar_max_abs_f32.md`.

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

None.
