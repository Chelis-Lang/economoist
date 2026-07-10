# Draft: nested fmax-style helper calls at a property goal site do not lower to Tier B

Filed upstream as chelis#425 on 2026-06-20.

**Status: CANDIDATE-FIXED (chelis 0.14.0).** The nested-`fmax` lowering gap is
resolved. The full n=3 per-output-state Bellman sup-norm contraction now lowers
and proves at SMT. Verified at the 0.14.0 pin via probe p15 and per-surface:
`bellman_contraction_state0_n3` / `_state1_n3` / `_state2_n3`, each upper and
lower (6 unqualified SMT greens + 6 refuting `*_guards_satisfiable` witnesses),
with the `fmax3` three-coordinate sup on the right and the two-call
`bellman_state0_n3` subtraction on the left. Economoist is de-narrowed: the n=3
contraction is no longer held out (see `docs/models/bellman.md`); general-`n` and
value-iteration convergence remain held out (they need induction). Archived in
`UPSTREAM_BUGS.md`. The historical analysis below -- which recorded that at 0.8.0
the `fmax3` helper lowered in isolation but did NOT yet make the n=3 contraction
provable -- is kept as the record.

**Summary.** A `@property` goal that nests local `fmax`-style helper calls at the
goal site (e.g. `fmax(fmax(a, b), c)` to express a three-way maximum) does not
lower to the SMT tier and drops to fuzz, even though each `fmax` helper lowers
cleanly as an `if/then/else` ITE in isolation and a single non-nested `fmax(...)`
at a goal site proves smt-green. The breakage is the helper-of-helper call at the
goal site, not the helper itself.

**Impact on downstream shells.** The n=3 Bellman sup-norm contraction takes a
three-way maximum over the per-state coordinate deviations
(`g * max(|v0-w0|, |v1-w1|, |v2-w2|)`). Written as a nested `fmax` at the goal
site, the contraction goal silently degrades to a sampled pass instead of an SMT
green, which for this shell would turn a structural economic green amber.

**Reproducer.** With `def fmax(a: f32, b: f32) -> f32 = if (a >= b) then a else b`,
a property goal of the form `... <= (g * fmax(fabs(d0), fmax(fabs(d1), fabs(d2))))`
does not lower to Tier B; the same goal with a single `fmax` over two arguments
does lower and proves smt-green.

**Workaround.** Flatten the three-way maximum into a single ternary helper that
nests `if/then/else` directly over the three arguments, with no helper-of-helper
call at the goal site:

```
def fmax3(a: f32, b: f32, c: f32) -> f32 =
  if (a >= b) then if (a >= c) then a else c else if (b >= c) then b else c
```

`fmax3` lowers to ITE in QF_NRA, so it removes the nested-`fmax` obstruction for
the helper itself. It does NOT, however, make the n=3 single-application
contraction provable: with the `fmax3` sup on the right and the n=3 operator
arithmetic inlined on the left, the contraction goal as a whole still reports
`unsupported` at Tier B (the combined nonlinear-plus-`fmax3` goal is past the
lowering limit). The n=3 per-state contraction is therefore HELD OUT in the shell
(see docs/models/bellman.md), not shipped. The two-state per-output-state
contractions, which use a single `fmax` and no `fmax3`, do prove smt-green.

**Ask.** Lower nested helper calls at a property goal site to Tier B (goal-site
inlining of `def`-bound helpers before lowering), so a three-way maximum can be
written by composing the two-argument `fmax` rather than hand-flattening a ternary.

**Filing condition.** Confirm nested `fmax`-style helper calls at a property goal
site still fail to lower to Tier B at the next release. Re-probe trigger: any
release note on prove-tier lowering or goal-site inlining of helper calls.
