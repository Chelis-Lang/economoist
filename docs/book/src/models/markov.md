# Markov transitions

`Economoist.Markov` advances a probability distribution over two or three
states by one step of a Markov chain. With current masses `p` and a
transition matrix `T`, where `tij` is the probability of moving from state `i`
to state `j`, the next mass of state `j` is `sum over i of p_i * tij`: the
masses weighted by column `j` of `T`.

## Functions

| Function | Signature | Returns |
| --- | --- | --- |
| `eps` | `() -> f32` | `0.0001`, the tolerance on every mass and row sum |
| `make_dist` | `(p0, p1) -> Option[Dist2]` | `Some` when both masses are `>= 0` and their sum is in `[1 - eps(), 1 + eps()]`, else `None` |
| `advance` | `(d: Dist2, t00, t01, t10, t11) -> Option[Dist2]` | The next distribution, or `None` when the step is refused (below) |
| `next_mass` | `(p, q, ta, tb) -> f32` | `p * ta + q * tb`, one output mass, unguarded |
| `make_dist3` | `(p0, p1, p2) -> Option[Dist3]` | As `make_dist`, for three masses |
| `advance3` | `(d: Dist3, t00, t01, t02, t10, t11, t12, t20, t21, t22) -> Option[Dist3]` | As `advance`, for three states |
| `mass3_next` | `(p0, p1, p2, ta, tb, tc) -> f32` | `p0 * ta + p1 * tb + p2 * tc`, one output mass, unguarded |

Every argument is `f32`. The transition entries are passed row by row:
`t00, t01` is the row out of state 0 and `t10, t11` the row out of state 1, so
each row should sum to one. `next_mass` and `mass3_next` take one column, the
entries into a single target state: the next mass of state 0 is
`next_mass(p0, p1, t00, t10)` and of state 1 is `next_mass(p0, p1, t01, t11)`.
`advance` computes its result with exactly these calls.

## Example

```chelis
module Demo.Main
import Economoist.Markov (make_dist, advance, next_mass, make_dist3, advance3, mass3_next)
start = make_dist(0.6f32, 0.4f32)
stepped = match make_dist(0.6f32, 0.4f32) with {
  | Some(d) => advance(d, 0.9f32, 0.1f32, 0.5f32, 0.5f32)
  | None => None
}
mass0 = next_mass(0.6f32, 0.4f32, 0.9f32, 0.5f32)
mass1 = next_mass(0.6f32, 0.4f32, 0.1f32, 0.5f32)
off_band = make_dist(0.6f32, 0.5f32)
row_too_heavy = match make_dist(0.6f32, 0.4f32) with {
  | Some(d) => advance(d, 0.5f32, 0.6f32, 0.5f32, 0.5f32)
  | None => None
}
drifted = match make_dist(0.99992f32, 0.0f32) with {
  | Some(d) => advance(d, 0.99992f32, 0.0f32, 0.0f32, 1.0f32)
  | None => None
}
stepped3 = match make_dist3(0.2f32, 0.3f32, 0.5f32) with {
  | Some(d) => advance3(d, 0.8f32, 0.1f32, 0.1f32, 0.2f32, 0.6f32, 0.2f32, 0.0f32, 0.3f32, 0.7f32)
  | None => None
}
mass3_0 = mass3_next(0.2f32, 0.3f32, 0.5f32, 0.8f32, 0.2f32, 0.0f32)
```

`chelis eval --file src/main.ch` prints:

```text
start = Some(Dist2(0.6, 0.4))
stepped = Some(Dist2(0.74, 0.26))
mass0 = 0.74
mass1 = 0.26
off_band = None
row_too_heavy = None
drifted = None
stepped3 = Some(Dist3(0.22000001, 0.35000002, 0.43))
mass3_0 = 0.22000001
```

State 0 keeps 90% of its mass and state 1 sends half of its mass to state 0,
so state 0 goes from 0.6 to `0.6 * 0.9 + 0.4 * 0.5 = 0.74`. `off_band` sums
to 1.1 and `row_too_heavy` has a row summing to 1.1, so both are refused.
`drifted` is explained under the step's refusal rules below.

## Reading a distribution

`Dist2` and `Dist3` are opaque. The evaluator prints their masses, but code
outside `Economoist.Markov` cannot read `d.p0`; the
compiler rejects it with "field access on opaque type `Dist2` outside its
defining module". The only way to obtain a `Dist2` is `make_dist` or
`advance`, which is what guarantees the invariant: every `Dist2` has masses
`>= 0` summing to within `eps()` of one, and likewise for `Dist3`.

To use the masses numerically, keep the inputs and compute the same values
with `next_mass` or `mass3_next`, as `mass0` and `mass1` do above; `advance`
uses those functions, so the numbers agree. Use `advance` to decide whether a
step is admitted and `next_mass` for the values.

## When `advance` refuses a step

`advance` and `advance3` return `None` unless all three of these hold:

1. every transition entry is `>= 0`;
2. every row sum lies in `[1 - eps(), 1 + eps()]`, with the sum taken in `f32`;
3. the output masses the step computes sum to a value in the same band.

Condition 2 tolerates `f32` rounding in a matrix that is stochastic in
decimal. The row `0.1773, 0.6378, 0.1849` sums to exactly one in decimal but
to `0.99999994` in `f32`, and is admitted. A row more than `0.0001` from one
is refused: `1.00005, 0` is admitted and `1.0002, 0` is not. A row at exactly
`0.0001` from one in decimal may land on either side of the band edge,
depending on how its entries round to `f32`. Normalize a matrix estimated
from data before passing it.

Condition 3 catches tolerance that compounds. In `drifted`, the starting
masses sum to 0.99992 and the row out of state 0 sums to 0.99992. Each is
inside the band, but their product puts the output total near 0.99984, so the
step is refused. Repeated calls to `advance` can accumulate drift the same
way, so whether a step is admitted depends on the distribution earlier steps
produced as well as on the matrix.

There is no separate check that output masses are nonnegative, because they
cannot be negative: the input masses are nonnegative by the type invariant,
condition 1 makes the entries nonnegative, and products and sums of
nonnegative numbers are nonnegative. A `NaN` entry fails condition 1, since every comparison with `NaN` is
false, and the step is refused.

`next_mass` and `mass3_next` check nothing. They return the weighted sum for
any inputs, including negative or non-stochastic ones.

## Checked properties

These properties are proved by the cvc5 SMT solver over real arithmetic, for
one transition, against `next_mass` and `mass3_next`:

| Property | Assumptions | Result |
| --- | --- | --- |
| `markov_mass_preserved` (two states), `markov3_mass_preserved` (three states) | Input masses sum exactly to one; every row sums exactly to one | Output masses sum exactly to one |
| `markov_nonneg_preserved`, `markov3_nonneg_preserved` | Input masses and transition entries are `>= 0` | Every output mass is `>= 0` |

Mass preservation and nonnegativity have separate assumptions; neither follows
from the other. The mass result assumes exact row sums, so it does not cover
rows admitted only through the `eps()` tolerance. For those, the run-time
condition 3 is what keeps a returned distribution in the band.

The solver also checks that `make_dist`, `make_dist3`, `advance` and
`advance3` never return a value that violates the `Dist2` or `Dist3`
invariant, again over real arithmetic.

## Scope

The results cover one transition at two states and one at three. They do not
establish anything for other state counts, the existence or uniqueness of a
stationary distribution, convergence of repeated transitions, or ergodicity.
A proof over the reals does not guarantee that every `f32` run preserves an
exact sum; the run-time band in conditions 2 and 3 is what bounds the `f32`
result.
