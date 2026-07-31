# Draft: scalar max/min/abs over f32 in chelis-std

Filed upstream as chelis#424 on 2026-06-20.

**Status: RESOLVED at the Chelis 0.17.4 source candidate.** Executable
zero-argument tests in the real Economoist Reef context compile and pass for
both scalar `max(f32, f32)` and `min(f32, f32)`; `abs` was already verified at
0.14.0. The historical standalone reproducer below records the original gap,
not the current package surface.

**Summary.** At chelis 0.8.0 there is no bound scalar `max`/`min`/`abs` for `f32`;
a bare `max(a, b)` over `f32` is an unbound variable. chelis-std exposes tensor
reductions and ad hoc per-file helpers, but no scalar elementwise reductions.

**Impact on downstream shells.** Any model that needs a scalar maximum (the
Bellman operator is a max over actions) or a scalar absolute value (a sup-norm
distance) must define a local helper with `if/then/else`. These helpers lower to
cvc5 as ITE and prove smt-green, so this is an ergonomics gap, not a blocker.

**Reproducer.** `def f(a: f32, b: f32) -> f32 = max(a, b)` fails with `unbound
variable: max`.

**Ask.** Provide scalar `fmax`/`fmin`/`fabs` (or polymorphic `max`/`min`/`abs`)
over `f32` in chelis-std so downstream shells do not each define their own.

**Filing condition.** No scalar `f32` max/min/abs lands in chelis-std at the next
release.
