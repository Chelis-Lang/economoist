# Gordon present value

[`Economoist.Growth`](../../src/growth.ch) exports `gordon_pv(d, r, g) = d / (r - g)`, with `d` the next-period dividend, `r` the required return, and `g` the dividend growth rate. The properties guard `r > g`, so the denominator is positive. The function itself evaluates the expression; its callers must supply an appropriate rate domain, or call the domain-checked entry points below.

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

## Domain-checked entry points

`gordon_pv` and `gordon_pv_strict` are **total**: they evaluate the closed form for any rates, and Chelis `f32` division does not trap. Outside the documented domain the result is wrong rather than absent:

| call | result |
| --- | --- |
| `gordon_pv(1, 0.08, 0.03)` — in domain | `20.000002` |
| `gordon_pv(1, 0.03, 0.08)` — `r < g` | `-20.000002` |
| `gordon_pv(1, 0.05, 0.05)` — `r = g` | `inf` |
| `gordon_pv_strict(1, 0.03, 0.08)` — `r < g` | `-20.000002` |

`gordon_pv_checked` and `gordon_pv_strict_checked` return `Option[f32]`, `None` outside the **rate** domain each raw export documents — the signalling convention [`Economoist.Markov`](../../src/markov.ch)'s `make_dist` already uses:

| export | rate condition enforced | rate condition of the matching property |
| --- | --- | --- |
| `gordon_pv_checked` | `r > g` | `gordon_positive` (`d > 0`, `r > g`) |
| `gordon_pv_strict_checked` | `r > g + 0.01` | `gordon_strict_positive` (`d > 0`, `r > g + 0.01`) |

Inside the rate domain each returns the same value as its raw counterpart. `r = 0.055`, `g = 0.05` separates the two: `gordon_pv_checked` admits it and returns `200.0000457763672`, while `gordon_pv_strict_checked` refuses, because the `0.005` spread does not clear the one-point margin.

**What `Some` does and does not mean.** These guards test the rates only. They are **not** the hypothesis of the positivity properties, which additionally require `d > 0`, so `Some(v)` does **not** imply `v > 0`: `gordon_pv_checked(-1, 0.08, 0.03)` returns `Some(-20.000002)`, the same number the table above shows as the out-of-domain answer. Nor does the guard bound the magnitude of the quotient — `gordon_pv_checked(1, 1.4e-45, 0)` returns `Some(inf)`, and the strict margin does not prevent it either (`gordon_pv_strict_checked(3.0e38, 0.02, 0)` is `Some(inf)`). And the `NaN` refusal is a property of the two rate arguments: a `NaN` `r` or `NaN` `g` gives `None`, while `gordon_pv_checked(NaN, 0.08, 0.03)` returns `Some(NaN)`. A caller that needs `d > 0`, a finite result, or a non-`NaN` dividend must still establish it. economoist#38 asked for the rate domain; widening these guards is a separate change.

**Why the raw exports stay total.** The reason is mechanical, not stylistic. `grad` rejects an `Option` result — `grad requires a scalar floating output, got Option f32` — and the [sampled derivative check](#sampled-derivative-check) differentiates the imported `gordon_pv` with respect to `r`. The SMT goals above and the `demos/businesswrong.ch` gallery compare the raw value against `0.0` over the reals, and the [model catalog](../cnote-import-surface.json) publishes `gordon_pv` under a frozen schema. So the guard is added beside the closed form rather than inside it. A caller that has already established its rate domain keeps the total function; a caller taking `r` and `g` from data should use the checked export.

There is no checked counterpart to `gordon_pv_negated`: that export is a deliberately defective reference model for the gallery, and a domain guard would assert a correctness it is built not to have.

**The guards are written in their positive form, and that is load-bearing.** `if (r > g) then Some(...) else None` returns `None` when `r` is `NaN`, because every ordering comparison against `NaN` is false, so the guard fails closed. The negated spelling `if (r <= g) then None else Some(...)` states the same domain and returns `Some` for a `NaN` rate. `test_gordon_pv_checked_rejects_nan_rate` in [`tests/growth.ch`](../../tests/growth.ch) pins it: negating the guard fails that test and no other.

No SMT goal covers the checked exports. `properties/` states real-arithmetic facts about scalar expressions and no property in this package quantifies over an `Option`; the checked domains are covered by the concrete tests instead.

## Closed form and convergence

For nonnegative growth and positive return with `0 ≤ g < r`, the usual discounted-dividend series has ratio `(1 + g) / (1 + r)` between zero and one, so its sum is `d / (r - g)`. This is the economic rate domain recorded for the model in the [model catalog](../cnote-import-surface.json). The SMT goals establish facts about the **closed-form expression** under their own written guards; they do not check the infinite series or its convergence.

The guard `r > g` alone does not guarantee convergence for arbitrary real rates: it makes `r - g` positive, but the series also requires `r ≠ -1` and `|(1 + g) / (1 + r)| < 1`. The catalog's economic rate domain is narrower than the proof guards.

## Sampled derivative check

[`sampled/growth_sensitivity.ch`](../../sampled/growth_sensitivity.ch) differentiates the exported `gordon_pv` with respect to `r` and checks that the resulting value is negative at sampled inputs. The proof gate requests 500 samples with seed 0 inside the property's bounded guards; its wrong-sign companion is expected to return a counterexample. This is an execution check of the AD result, not a proof across the whole domain. It is separate from the real-arithmetic two-point comparison above. No sampled `dP/dg` property ships.

[`demos/businesswrong.ch`](../../demos/businesswrong.ch) includes a claim that fails when `g > r` and another that fails when a deliberately negated valuation replaces `gordon_pv` inside `r > g`. Each has a passing control.

The Gordon expression is scalar, so there is no state dimension to generalize. Its SMT results do not certify `f32` execution; the concrete values in [`tests/growth.ch`](../../tests/growth.ch) exercise that separately.
