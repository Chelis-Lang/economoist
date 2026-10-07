# Economoist model guide

## Models

| Model | Functions | Checked claims |
| --- | --- | --- |
| [Markov transitions](models/markov.md) | `make_dist`, `advance`, `next_mass` (two states); `make_dist3`, `advance3`, `mass3_next` (three states); `eps` | Exact mass preservation and nonnegativity for one transition; every value `make_dist` or `advance` returns satisfies the distribution invariant |
| [Bellman operator](models/bellman.md) | `bellman_state0`, `bellman_state1` (two states); `bellman_state0_n3`, `bellman_state1_n3`, `bellman_state2_n3` (three states); `fmax`, `fmax3`, `fabs` | Monotonicity and boundedness at output state 0; a two-sided contraction bound at every output state |
| [Gordon present value](models/growth.md) | `gordon_pv`, `gordon_pv_checked`, `gordon_pv_strict`, `gordon_pv_strict_checked`, `gordon_pv_negated` | Positivity, increase in `D`, decrease in `r`; a sampled sign check on `dP/dr` |

All arguments and results are `f32`. Distributions are returned as
`Option[Dist2]` or `Option[Dist3]`, and the checked Gordon functions return
`Option[f32]`; every other function returns a plain `f32` and accepts any
input.

## Proved and sampled results

The structural properties are proved by the cvc5 SMT solver, which treats each
`f32` expression as an expression over the real numbers. A proved property
holds for every real input that satisfies its assumptions, at the dimension it
names. It says nothing about `f32` rounding, repeated application, or other
state counts.

One result is sampled instead: the claim that the automatic-differentiation
derivative of `gordon_pv` with respect to `r` is negative. It is evaluated in
`f32` at 500 inputs drawn with a fixed seed from `0.5 < d < 9.5`,
`0 < g < 4`, `g < r < 9.5`, and passes at every sample. A sign-flipped twin of
the claim fails at its first sample. Sampling is numerical evidence over that
box, not a proof over it. The real-arithmetic counterpart, that a larger `r`
gives a smaller value, is proved separately as a two-point comparison.

Each proved property also has a non-vacuity check: the solver finds an input
that satisfies all of its assumptions, so the assumptions are not contradictory
and the property is not true by default.

Every function here is an ordinary export: a property you write in your own
project can import it and be checked with `chelis prove`, as
[Getting started](getting-started.md) shows.
