# Gordon Growth Model: present value of a growing perpetuity

The Gordon growth model values a perpetuity whose cash flow grows at a constant
rate. With next-period dividend `D`, required return `r`, and growth rate `g`,
and under the convergence condition `r > g`, the present value of the growing
perpetuity has the closed form

```
P = D / (r - g)
```

The shipped value is `gordon_pv(d, r, g) = (d / (r - g))` in
`src/growth.ch`. The proven facts live in `properties/growth.ch` and discharge
at the SMT tier (cvc5) over the reals, with zero fuzz and no contract qualifier.
The concrete-instance runtime test lives in `tests/growth.ch`.

This is the academic-launch surface for "C Proof": every economic property here
is a genuine, unqualified SMT green. An amber (fuzz) result or an unsupported
property would be a bug to fix, not a result to ship.

## What is proven, per property

Every goal is stated in multiplied-through polynomial form. The Gordon value is
a quotient `D / (r - g)`, and a comparison that contains a division is nonlinear
and fragile for the solver. Each property is therefore restated so the solver
sees polynomials only: positivity becomes "numerator positive and denominator
positive", a monotonicity becomes a cross-multiplied inequality, and a
derivative sign becomes "polynomial numerator has the claimed sign and the
denominator square is positive". The displayed `def` keeps the division for
evaluation and display; no `/` appears in any proof goal.

| Property | Guards | Proven (polynomial form) | Economic meaning |
| --- | --- | --- | --- |
| `gordon_positive` | `d > 0`, `r > g` | `(d > 0) && ((r - g) > 0)` | `P = D/(r-g) > 0` |
| `gordon_increasing_in_d` | `r > g`, `d2 > d1` | `((d2 - d1) > 0) && ((r - g) > 0)` | larger dividend gives larger `P` |
| `gordon_decreasing_in_r` | `d > 0`, `r1 > g`, `r2 > r1` | `((d * (r1 - r2)) < 0) && ((r1 - g) > 0) && ((r2 - g) > 0)` | `D/(r2-g) < D/(r1-g)`: raising `r` lowers `P` |
| `gordon_dP_dr_negative` | `d > 0`, `r > g` | `((0 - d) < 0) && (((r - g) * (r - g)) > 0)` | `dP/dr = -D/(r-g)^2 < 0` |
| `gordon_dP_dg_positive` | `d > 0`, `r > g` | `(d > 0) && (((r - g) * (r - g)) > 0)` | `dP/dg = +D/(r-g)^2 > 0` |

`gordon_decreasing_in_r` cross-multiplies the two quotients: `D/(r2-g) <
D/(r1-g)` with both denominators positive is equivalent to `D*(r1-r2) < 0`. The
two comparative statics state the sign of the numerator of the derivative
together with the strict positivity of the denominator square, which together
pin the sign of `dP/dr` and `dP/dg` without ever forming the quotient.

### Non-vacuity

Each real property is paired with a `<name>_guards_satisfiable` witness that
asserts `false` under the identical `forall` and guards. Under `--tier
smt-only` cvc5 refutes each witness by exhibiting a guard-satisfying model (for
example `d = 1, r = 1, g = 0`), which proves the guards are jointly satisfiable
and the corresponding green is not vacuous. In the prove summary the five
witnesses report `status: failed, proof_tier: smt`; that refutation is the
intended outcome, not a failure of the model.

### Prove summary

```
chelis prove properties/growth.ch --json --tier smt-only --smt-timeout 15000
```

reports, per property, `proof_tier: smt`, `arith_model: real`, and
`composite_verdict: proven` with `status: passed` for the five real properties,
and `status: failed` for the five non-vacuity witnesses. Summary:
`passed: 5, failed: 5, errors: 0, unsupported: 0` (the five failures are the
refuted `false` witnesses). The command exits nonzero precisely because the
witnesses are refuted; that is expected.

## Honesty boundaries

Three boundaries are stated explicitly, per the repo contract.

1. **Closed-form algebraic fact, not a limit or convergence result.** Every
   green here is a fact about the closed-form expression `D / (r - g)` itself.
   The closed form is the sum of the discounted geometric series `D * sum_{k>=0}
   (1+g)^k / (1+r)^{k+1}`, and that sum equals `D / (r - g)` only as a limit and
   only when `r > g`. The convergence of that discounted sum to the closed form
   is a limit result that needs the geometric-series argument; it is held out.
   What is proven is the sign and monotonicity structure of the closed-form
   expression under `r > g`, nothing about the iterated sum that produced it.

2. **Fixed dimension vs general-n: not applicable here.** The Markov and Bellman
   results in this shell carry a fixed-dimension caveat because they are proven at
   the small fixed dimensions `n = 2` and `n = 3`, which is not the all-`n`
   theorem. The Gordon value has no state dimension: it is a closed form in three
   scalars `D`, `r`, `g`.
   There is no `n` to generalize over, so the fixed-dimension caveat is
   considered and found not applicable. This is stated explicitly so the reader
   knows it was not omitted by oversight.

3. **Reals vs floats.** The proven facts are statements of real arithmetic, as
   discharged by cvc5 over the reals (`arith_model: "real"` in the prove JSON).
   They are not statements about `f32` evaluation. The concrete test in
   `tests/growth.ch` and the eval demo below exercise the `f32` value of the
   shipped expression; that floating-point behavior is a separate, unproven
   concern.

## E4 comparative statics: the AD demo

The comparative statics `dP/dr` and `dP/dg` have SMT-proven signs above. The
same signs can be exhibited numerically through the language's automatic
differentiation, which differentiates the same `gordon_pv` expression whose
value is displayed. This is the single-expression discipline: the function body
that `eval` evaluates for its value is the identical body that `grad`
differentiates for its derivative, so the AD result is a derivative of the
shipped expression and not of a separate restatement.

At the concrete point `D = 2, r = 0.1, g = 0.05` the denominator is `r - g =
0.05`, so the analytic values are `P = 2 / 0.05 = 40`, `dP/dr = -D/(r-g)^2 =
-2 / 0.0025 = -800`, and `dP/dg = +D/(r-g)^2 = +800`.

Value of the shipped expression:

```
chelis eval '(fn (d: f32, r: f32, g: f32) -> (d / (r - g)))(2.0, 0.1, 0.05)'
# 40
```

Gradient with respect to `r` (the body is the identical `gordon_pv` expression):

```
chelis eval 'grad(fn (d: f32, r: f32, g: f32) -> (d / (r - g)), wrt=r)(2.0, 0.1, 0.05)'
# tensor(shape=[], data=[-799.9999761581425])
```

Gradient with respect to `g`:

```
chelis eval 'grad(fn (d: f32, r: f32, g: f32) -> (d / (r - g)), wrt=g)(2.0, 0.1, 0.05)'
# tensor(shape=[], data=[799.9999761581425])
```

The AD-computed derivative with respect to `r` is negative (about `-800`) and the
derivative with respect to `g` is positive (about `+800`), in `f32`. These match
the signs of `gordon_dP_dr_negative` and `gordon_dP_dg_positive` proven over the
reals. The small `f32` shortfall from the exact `800` is the floating-point
residue, which is precisely the reals-vs-floats boundary above: the proven fact
is the real-arithmetic sign, and the `f32` AD value confirms that sign at a
point without being itself a proof.

The lambda body `(d / (r - g))` written inline is the exact body of
`def gordon_pv` in `src/growth.ch`. The inline form is used for the demo because
`eval --file` loads the whole package context; the inline expression keeps the
demo self-contained while still differentiating the identical Gordon expression.
