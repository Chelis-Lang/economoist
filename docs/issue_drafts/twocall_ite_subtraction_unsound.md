# Draft: two-call comparison/subtraction of an ITE-bodied def false-proves

Filed upstream as chelis#426 on 2026-06-20. This is the most serious of the
shell's upstream filings: a false `proven` at the SMT tier.

**Summary.** A `@property` goal that compares or subtracts two calls of the same
`def` whose body calls an ITE-bodied helper (for example an `fmax`-based
max-over-actions), with different arguments, does not lower faithfully. The
lowering collapses the two-call expression to the all-arguments-equal corner, so a
mathematically FALSE goal is reported `status:passed, proof_tier:smt,
composite_verdict:proven, samples:0, arith_model:real` with no counterexample.

**Reproducer (chelis 0.8.0, --features smt).**

```
def fmax(a: f32, b: f32) -> f32 = if (a >= b) then a else b
def bs(v0: f32, v1: f32, r0: f32, p00: f32, p01: f32, r1: f32, p10: f32, p11: f32, g: f32) -> f32 =
  fmax((r0 + (g * ((p00 * v0) + (p01 * v1)))), (r1 + (g * ((p10 * v0) + (p11 * v1)))))

@property cmp_unguarded forall(...):
  (bs(v0, v1, ...) <= bs(w0, w1, ...))           -- FALSE in general; reports proven
@property sub_unguarded forall(...):
  ((bs(v0, v1, ...) - bs(w0, w1, ...)) <= 0.0)   -- FALSE in general; reports proven
```

A constant RHS of `-1000` does fail, so it is specifically the two-call collapse
to the all-equal corner, not a total no-op. A def whose body is an inline
`if/then/else` (no further call) does NOT trigger it; inlining the operator
arithmetic directly at the goal site lowers correctly (true proves, false refutes).

**Impact on this shell.** The first cut of the Bellman contraction and
monotonicity properties called an `fmax`-based `bellman_state0` twice in the goal
and were vacuously green. They were rewritten to the inlined form, which is sound
(the per-output-state contractions prove true and refute false with real
counterexamples). The shipped operators `bellman_state0` and friends remain as
display/eval definitions (called once in tests, which is sound).

**Workaround taken.** Inline the operator arithmetic at the goal site; never call
an ITE-bodied operator def twice in a goal. `scripts/prove_gate.py` enforces this
structurally (the `unsound_pattern_lint`).

**Re-probe trigger.** Any release note on prove-tier lowering, goal-site inlining,
or two-call expression handling. Re-probe the reproducer above per release.

**Re-probe 2026-06-23 (chelis 0.9.0).** Still reproduces. The two FALSE goals
(`cmp_unguarded`, `sub_unguarded`) are reported `status:passed, proof_tier:smt`
with no counterexample; only the verdict token changed (`proven` ->
`proven_modulo_real_arithmetic`, the 0.9.0 unqualified-green token). The fix has
not landed; the `unsound_pattern_lint` workaround stays in force.
