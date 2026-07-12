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

Every goal REFERENCES the exported `gordon_pv` directly: it calls the shipped
`gordon_pv(d, r, g) = (d / (r - g))` at the goal site rather than restating the
guards in a separate polynomial form. Positivity calls `gordon_pv` once; each
comparative static compares two `gordon_pv` calls at shifted inputs. The goals
discharge at SMT under the `r > g` guard (the denominator is guarded nonzero),
verified via probes p01/p02/p03.

This is the anti-vacuity discipline. An earlier cut restated each goal in
multiplied-through polynomial form (for example positivity as
`(d > 0) && ((r - g) > 0)`); that restatement never mentions `gordon_pv`, so it
was a VACUOUS restatement of the guards, not a fact about the shipped value. The
restatements were replaced by calls to the export, so the green is now a fact
about `gordon_pv` itself.

| Property | Guards | Proven (calls `gordon_pv`) | Economic meaning |
| --- | --- | --- | --- |
| `gordon_positive` | `d > 0`, `r > g` | `gordon_pv(d, r, g) > 0` | `P = D/(r-g) > 0` |
| `gordon_increasing_in_d` | `r > g`, `d2 > d1` | `gordon_pv(d2, r, g) > gordon_pv(d1, r, g)` | larger dividend gives larger `P` |
| `gordon_decreasing_in_r` | `d > 0`, `r1 > g`, `r2 > r1` | `gordon_pv(d, r2, g) < gordon_pv(d, r1, g)` | raising `r` lowers `P` |

`gordon_decreasing_in_r` compares the value at the higher `r2` against the value
at the lower `r1` at the same `d` and `g`; that the higher discount rate yields
the smaller present value is exactly the two-point statement of `dP/dr < 0` over
the reals. `gordon_increasing_in_d` likewise compares two values at shifted `d`.

The two derivative-SIGN properties an earlier cut shipped
(`gordon_dP_dr_negative`, `gordon_dP_dg_positive`) were REMOVED from
`properties/`: each stated a polynomial numerator sign plus a positive
denominator square and never referenced `gordon_pv`, so each was a vacuous
restatement of the guards. The `dP/dr` sign now lives in the sampled AD lane
(`fuzz_validated`, amber) and is ALSO available over the reals as the proven
two-point green `gordon_decreasing_in_r`; see the AD demo below.

### Non-vacuity

Each real property is paired with a `<name>_guards_satisfiable` witness that
asserts `false` under the identical `forall` and guards. Under `--tier
smt-only` cvc5 refutes each witness by exhibiting a guard-satisfying model (for
example `d = 1, r = 1, g = 0`), which proves the guards are jointly satisfiable
and the corresponding green is not vacuous. In the prove summary the three
witnesses report `status: failed, proof_tier: smt`; that refutation is the
intended outcome, not a failure of the model. Because every goal now calls
`gordon_pv`, the prover-emitted goal string carries the mangled export
reference, which the producer gate cross-checks for anti-vacuity
(`dependency_edges` does not survive the module-import boundary; see
`issue_drafts/dependency_edges_imports.md`).

### Prove summary

```
chelis prove properties/growth.ch --json --tier smt-only --smt-timeout 15000
```

reports, per property, `proof_tier: smt`, `arith_model: real`, and
`composite_verdict: proven` with `status: passed` for the three real properties,
and `status: failed` for the three non-vacuity witnesses. Summary:
`passed: 3, failed: 3, errors: 0, unsupported: 0` (the three failures are the
refuted `false` witnesses). The command exits nonzero precisely because the
witnesses are refuted; that is expected.

### Defective controls: in-region vs out-of-region breakage

Two defective exemplars guard the positivity canon from opposite sides, so the
green is load-bearing rather than merely satisfiable in some corner:

- `gordon_positive_wrong` is the OUT-of-region exemplar: it flips the guard to
  `g > r` (outside the convergence region `r > g`), where `D/(r - g)` is
  negative. It shows the guard `r > g` is doing real work -- drop it and
  positivity fails.
- `gordon_pv_negated` (manifest model `gordon_mispriced`, `defective: true`) is a
  mispriced perpetuity whose closed form negates the value. Its positivity canon
  breaks IN region, at `r > g`, with an `f32`-confirmed counterexample: the demos
  `gordon_pv_corrupted_wrong` (refutes) and `gordon_pv_corrupted_control` (the
  correct model, passes) pin that the break is a genuine mispricing inside the
  valid region, not an out-of-region artifact.

## The strict (margin-of-safety) variant and the nested-region implication

`gordon_pv_strict(d, r, g) = (d / (r - g))` in `src/growth.ch` is the
conservative variant of the model: numerically the identical closed form, but the
one a cautious analyst uses when the discount spread `r - g` must clear a safety
margin before the valuation is trusted. Its documented domain of use is the
strict region `r > g + 0.01` (the spread clears a one-point margin), a proper
subset of `gordon_pv`'s convergence region `r > g`. It is a real modeling
artifact, not a demo property: the same perpetuity, valued under a tighter stated
domain.

Shipping it as its own export and manifest model (`gordon_strict`, kind
`econ.perpetuity_pv`, same params) lets the characterization surface state a
region-nesting relationship precisely. The strict positivity invariant
`gordon_strict_positive` proves `gordon_pv_strict(d, r, g) > 0` under `d > 0` and
`r > (g + 0.01)` (same division-form call, verified via probe p01), and
`gordon_positive` proves the same for `gordon_pv` under `d > 0` and `r > g`. The
region inclusion is pure arithmetic -- `r > g + 0.01` implies `r > g` -- so the
strict proven region is contained in the standard one:

```
{ d > 0, r > g + 0.01 }   subset of   { d > 0, r > g }
```

The two proofs establish positivity on each region; the arithmetic inclusion is
what makes it an organization implication: any use inside the strict domain is a
valid use inside the standard domain (never the reverse). The manifest records
this as `econ.inv.gordon_strict_positive.v1` with
`nests_inside: econ.inv.gordon_positive.v1`, which the consumer surfaces as a
candidate org implication.

The `+ 0.01` margin is a domain-of-USE choice, not a positivity necessity.
Positivity of `D / (r - g)` holds throughout the convergence region `r > g`, so
for any `r` in `(g, g + 0.01]` the value is still positive; the margin encodes an
analyst's trust threshold on the discount spread `r - g` (a razor-thin spread
makes the closed form ill-conditioned in `f32`), not a mathematical requirement
for a positive price. The out-of-region twin `gordon_strict_positive_wrong` flips
the guard to `g > r`, which leaves the CONVERGENCE region `r > g` (not merely the
margin band); it refutes with an in-domain witness, demonstrating that the
`r > g` convergence guard -- the one shared with `gordon_positive` -- is the
load-bearing hypothesis for positivity.

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

## E4 comparative statics: the AD demo (sampled lane)

The `dP/dr` sign is a proven fact over the reals as the two-point green
`gordon_decreasing_in_r` above. It is ALSO exhibited numerically through the
language's automatic differentiation, which differentiates the same `gordon_pv`
expression whose value is displayed. This is the single-expression discipline:
the function body that `eval` evaluates for its value is the identical body that
`grad` differentiates for its derivative, so the AD result is a derivative of the
shipped expression and not of a separate restatement.

The AD sensitivity ships as an honest amber, NOT a proven green. It lives in the
sampled lane (`sampled/growth_sensitivity.ch`, module prefix
`Economoist.Sampled`, property `gordon_dP_dr_negative_grad`) at tier
`fuzz_validated`, kept out of the pure-SMT-green `properties/` boundary. Two
upstream gaps force this: a `grad` goal does not lower to the SMT tier -- it only
fuzz-validates (`issue_drafts/grad_smt_lowering.md`) -- and `grad` does not lower
through a cross-module import call (it hangs), so the sampled property inlines
`gordon_pv`'s shipped single-expression body `(d / (r - g))` rather than
referencing the export directly (`issue_drafts/grad_through_import.md`). The
oracle harness pins the inline body against `gordon_pv`'s numeric goldens so the
equivalent form cannot drift from the export. When `grad` goals lower to SMT this
amber is re-probed and its expected tier bumps to `proven` -- a de-narrowing
event, not a rewrite.

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
derivative with respect to `g` is positive (about `+800`), in `f32`. The `dP/dr`
sign is the shipped sampled invariant `gordon_dP_dr_negative_grad`
(`fuzz_validated`, amber) and matches the proven two-point green
`gordon_decreasing_in_r` over the reals; the `dP/dg` gradient is shown here only
as an eval illustration and is not itself a shipped invariant. The small `f32`
shortfall from the exact `800` is the floating-point residue, which is precisely
the reals-vs-floats boundary above: the proven fact is the real-arithmetic sign,
and the `f32` AD value confirms that sign at a point without being itself a proof.

The lambda body `(d / (r - g))` written inline is the exact body of
`def gordon_pv` in `src/growth.ch`. The inline form is used for the demo because
`eval --file` loads the whole package context; the inline expression keeps the
demo self-contained while still differentiating the identical Gordon expression.
