# Gordon present value

[`Economoist.Growth`](../../src/growth.ch) exports `gordon_pv(d, r, g) = d / (r - g)`, with `d` the next-period dividend, `r` the required return, and `g` the dividend growth rate. The properties guard `r > g`, so the denominator is positive. The function itself evaluates the expression; its callers must supply an appropriate rate domain.

## Checked properties

The goals in [`properties/growth.ch`](../../properties/growth.ch) call the exported model functions. Chelis checks these statements over the reals:

| Goal | Guards | Checked result |
| --- | --- | --- |
| `gordon_positive` | `d > 0`, `r > g` | `gordon_pv(d, r, g) > 0` |
| `gordon_increasing_in_d` | `r > g`, `d2 > d1` | The value at `d2` exceeds the value at `d1`. |
| `gordon_decreasing_in_r` | `d > 0`, `r1 > g`, `r2 > r1` | The value at `r2` is below the value at `r1`. |
| `gordon_strict_positive` | `d > 0`, `r > g + 0.01` | `gordon_pv_strict(d, r, g) > 0`. |

`gordon_pv_strict` evaluates the **same formula** as `gordon_pv`. Its wider discount spread is a documented domain-of-use choice, not a second valuation equation or a requirement for positivity throughout `r > g`. Each checked property has a separate witness whose expected counterexample establishes that its guards are satisfiable.

`gordon_decreasing_in_r` is a two-point comparison. There is no SMT goal here for an automatic-differentiation result or for sensitivity to `g`.

## Closed form and convergence

For nonnegative growth and positive return with `0 ≤ g < r`, the usual discounted-dividend series has ratio `(1 + g) / (1 + r)` between zero and one, so its sum is `d / (r - g)`. This is the economic rate domain recorded for the model in the [model catalog](../cnote-import-surface.json). The SMT goals establish facts about the **closed-form expression** under their own written guards; they do not check the infinite series or its convergence.

The guard `r > g` alone does not guarantee convergence for arbitrary real rates: it makes `r - g` positive, but the series also requires `r ≠ -1` and `|(1 + g) / (1 + r)| < 1`. The catalog's economic rate domain is narrower than the proof guards.

## Sampled derivative check

[`sampled/growth_sensitivity.ch`](../../sampled/growth_sensitivity.ch) differentiates the exported `gordon_pv` with respect to `r` and checks that the resulting value is negative at sampled inputs. The proof gate requests 500 samples with seed 0 inside the property's bounded guards; its wrong-sign companion is expected to return a counterexample. This is an execution check of the AD result, not a proof across the whole domain. It is separate from the real-arithmetic two-point comparison above. No sampled `dP/dg` property ships.

[`demos/businesswrong.ch`](../../demos/businesswrong.ch) includes a claim that fails when `g > r` and another that fails when a deliberately negated valuation replaces `gordon_pv` inside `r > g`. Each has a passing control.

The Gordon expression is scalar, so there is no state dimension to generalize. Its SMT results do not certify `f32` execution; the concrete values in [`tests/growth.ch`](../../tests/growth.ch) exercise that separately.
