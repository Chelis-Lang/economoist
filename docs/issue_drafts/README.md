# Issue Drafts

Upstream issue drafts. Most drafts have been filed on the `Chelis-Lang/chelis`
tracker; a few are not yet filed and are cited by draft path until a `chelis#NNN`
is assigned. The draft file is kept as the rationale record in either case. Cite
the filed issue number (`chelis#NNN`) -- or the draft path for an unfiled draft --
at narrowing sites and in `UPSTREAM_BUGS.md`.

| Draft | Filing condition | Status |
|---|---|---|
| `smt_in_release_tarball.md` | RESOLVED: SMT ships in the released tarball as of chelis v0.11.0 (verified at 0.14.0, 2026-07-10). | Filed as chelis#422 on 2026-06-20; archived in `UPSTREAM_BUGS.md`. |
| `eval_side_import_resolution.md` | Confirm eval still does not resolve standalone-file imports when a C Note template needs it. | Filed as chelis#423 on 2026-06-20. |
| `scalar_max_abs_f32.md` | RE-PROBED at 0.14.0 (2026-07-10): `abs` binds, `max`/`min` still unbound; the local `fmax` workaround still ships. | Filed as chelis#424 on 2026-06-20; Tracking (partial). |
| `nested_fmax_goal_site.md` | CANDIDATE-FIXED at chelis 0.14.0: the n=3 per-output-state contraction lowers and proves (p15 + per-surface). | Filed as chelis#425 on 2026-06-20; archived in `UPSTREAM_BUGS.md`. |
| `twocall_ite_subtraction_unsound.md` | RESOLVED at chelis 0.10.0, re-verified at 0.14.0 (p04). | Filed as chelis#426 on 2026-06-20; archived in `UPSTREAM_BUGS.md`. |
| `grad_smt_lowering.md` | grad goals do not lower to SMT (AD sensitivity is fuzz-only); tier-upgrade trigger for the sampled invariant. | Open draft (not yet filed; cite the path). |
| `grad_through_import.md` | grad hangs differentiating through a cross-module import call at 0.14.0. | Open draft (not yet filed; cite the path). |
| `dependency_edges_imports.md` | prove --json `dependency_edges` omits cross-module import references. | Open draft (not yet filed; cite the path). |
