# Gordon present value

The Gordon model values a stock whose dividend grows at a constant rate:

```text
P = D / (r - g)
```

`D` is the next-period dividend, `r` the required return per period, and `g`
the dividend growth rate per period. Rates are decimal fractions per period:
`0.05` is 5%. `P` is in the units of `D`. The formula is the sum of the
discounted dividend series when `0 <= g < r`; the usual economic domain is
`D > 0` and `0 <= g < r < 1`.

## Functions

| Function | Signature | Behavior |
| --- | --- | --- |
| `gordon_pv` | `(d: f32, r: f32, g: f32) -> f32` | `d / (r - g)` for any input |
| `gordon_pv_checked` | `(d: f32, r: f32, g: f32) -> Option[f32]` | `Some(d / (r - g))` when `r > g`, else `None` |
| `gordon_pv_strict_checked` | `(d: f32, r: f32, g: f32) -> Option[f32]` | `Some(d / (r - g))` when `r > g + 0.01`, else `None` |
| `gordon_pv_strict` | `(d: f32, r: f32, g: f32) -> f32` | Same formula as `gordon_pv`; its proved positivity assumes `r > g + 0.01` |
| `gordon_pv_negated` | `(d: f32, r: f32, g: f32) -> f32` | `-(d / (r - g))`, a deliberately wrong model used to demonstrate a counterexample; not for valuation |

Arithmetic is `f32`, about seven significant digits: `gordon_pv(1, 0.08, 0.03)`
comes back as `20.000002`, because `0.08 - 0.03` is not exactly `0.05` in `f32`. The `0.01` in the strict variant is one percentage point of
spread between `r` and `g` in the decimal units above.

## Example

```chelis
module Demo.Main
import Economoist.Growth (gordon_pv, gordon_pv_checked, gordon_pv_strict_checked)
price = gordon_pv(2.0f32, 0.1f32, 0.05f32)
inverted = gordon_pv(1.0f32, 0.03f32, 0.08f32)
equal_rates = gordon_pv(1.0f32, 0.05f32, 0.05f32)
checked_ok = gordon_pv_checked(1.0f32, 0.08f32, 0.03f32)
checked_inverted = gordon_pv_checked(1.0f32, 0.03f32, 0.08f32)
checked_nan_rate = gordon_pv_checked(1.0f32, (0.0f32 / 0.0f32), 0.03f32)
checked_negative_d = gordon_pv_checked(-1.0f32, 0.08f32, 0.03f32)
checked_tiny_spread = gordon_pv_checked(1.0f32, 1.4e-45f32, 0.0f32)
strict_ok = gordon_pv_strict_checked(1.0f32, 0.08f32, 0.03f32)
strict_inside_margin = gordon_pv_strict_checked(1.0f32, 0.085f32, 0.08f32)
strict_at_margin = gordon_pv_strict_checked(1.0f32, 0.06f32, 0.05f32)
```

`chelis eval --file src/main.ch` prints:

```text
price = 40.0
inverted = -20.000002
equal_rates = inf
checked_ok = Some(20.000002)
checked_inverted = None
checked_nan_rate = None
checked_negative_d = Some(-20.000002)
checked_tiny_spread = Some(inf)
strict_ok = Some(20.000002)
strict_inside_margin = None
strict_at_margin = None
```

## Failure behavior

`gordon_pv` never fails; it returns whatever `f32` division gives, and `f32`
division does not trap. With `r < g` the sign of the result is the opposite
of the sign of `d`: `gordon_pv(1, 0.03, 0.08)` is `-20.000002` and
`gordon_pv(-1, 0.03, 0.08)` is `20.000002`. With `r = g` the result is `inf`
for `d > 0`, `-inf` for `d < 0`, and `NaN` for `d = 0`. Use `gordon_pv` only
where the rate domain is already established, or where you need a plain `f32`
result, for example to differentiate it with
[`grad`](https://chelis.ch/docs/chelis/transforms/), which accepts only a scalar
floating-point result, not an `Option`.

The checked functions test one inequality on the rates and nothing else:

- A `NaN` rate is refused, because every comparison with `NaN` is false. A
  `NaN` dividend is not tested: `gordon_pv_checked(NaN, 0.08, 0.03)` returns
  `Some(NaN)`.
- The sign of `d` is not tested, so `Some` can hold a negative value, as in
  `checked_negative_d`.
- The size of the result is not bounded. A spread of one subnormal `f32`
  passes `r > g` and gives `Some(inf)`.
- The rates are not checked against the economic domain:
  `gordon_pv_checked(1, 2.0, 1.5)` is `Some(2.0)` with `r` above one, and
  `gordon_pv_checked(1, -2.0, -3.0)` is `Some(1.0)` for rates at which the
  dividend series diverges.
- `gordon_pv_strict_checked` requires the spread to exceed `0.01` strictly,
  with `g + 0.01` computed in `f32`. A spread of exactly one point, as in
  `strict_at_margin`, is refused.

To accept only economically meaningful valuations, call a checked function
(which enforces `r > g`) and also test `d > 0`, `0 <= g`, `r < 1` and that the
result is finite. If you call `gordon_pv` directly, test `r > g` as well.

## Proved and sampled results

These properties are proved by the cvc5 SMT solver over real arithmetic:

| Property | Assumptions | Result |
| --- | --- | --- |
| `gordon_positive` | `d > 0`, `r > g` | `gordon_pv(d, r, g) > 0` |
| `gordon_increasing_in_d` | `r > g`, `d2 > d1` | `gordon_pv(d2, r, g) > gordon_pv(d1, r, g)` |
| `gordon_decreasing_in_r` | `d > 0`, `r1 > g`, `r2 > r1` | `gordon_pv(d, r2, g) < gordon_pv(d, r1, g)` |
| `gordon_strict_positive` | `d > 0`, `r > g + 0.01` | `gordon_pv_strict(d, r, g) > 0` |

The derivative result is sampled, not proved. `gordon_dP_dr_negative_grad`
differentiates `gordon_pv` with respect to `r` using Chelis automatic
differentiation and checks that the derivative is negative at 500 `f32`
inputs drawn with a fixed seed from `0.5 < d < 9.5`, `0 < g < 4`,
`g < r < 9.5`. All 500 pass. This is numerical evidence over that box; the
proved statement about `r` is the two-point comparison
`gordon_decreasing_in_r`.

None of these results covers `f32` rounding, and none establishes that a
dividend series converges; they concern the closed-form expression.
