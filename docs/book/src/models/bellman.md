# Bellman operator

`Economoist.Bellman` computes one Bellman optimality update for a Markov
decision process with two or three states and two actions per state. Given a
value vector `v` (one value per state) and a discount `g`, the Bellman
operator `T` produces a new vector `Tv` whose entry for state `s` is

```text
(Tv)_s = max over actions a of ( reward(s, a) + g * sum over j of P(j | s, a) * v_j )
```

the best action's immediate reward plus the discounted expected value of the
state it leads to. Each output state is a separate function; call one per
state to build the whole of `Tv`.

## Functions

| Function | Arguments | Returns |
| --- | --- | --- |
| `bellman_state0`, `bellman_state1` | `(v0, v1, ra, a0, a1, rb, b0, b1, g)` | `(Tv)_0` or `(Tv)_1` at two states |
| `bellman_state0_n3`, `bellman_state1_n3`, `bellman_state2_n3` | `(v0, v1, v2, ra, a0, a1, a2, rb, b0, b1, b2, g)` | `(Tv)_0`, `(Tv)_1` or `(Tv)_2` at three states |
| `fmax` | `(a, b)` | `a` if `a >= b`, else `b` |
| `fmax3` | `(a, b, c)` | `fmax`'s rule applied pairwise: `a` if `a >= b` and `a >= c`, else `b` if `b >= c`, else `c` |
| `fabs` | `(x)` | `x` if `x >= 0`, else `-x` |

Every comparison with `NaN` is false, so these helpers do not propagate `NaN`
consistently: `fmax(NaN, 1)` is `1` but `fmax(1, NaN)` is `NaN`;
`fmax3(NaN, 1, 2)` and `fmax3(3, NaN, 2)` are both `2`, and
`fmax3(3, 1, NaN)` is `NaN`. Check inputs for `NaN` before calling.

All arguments and results are `f32`. The argument names in the table are
placeholders for the layout, which is the same for every state function:

- `v0, v1` (and `v2`): the current values of states 0, 1 (and 2).
- `ra, a0, a1` (and `a2`): the first action's reward in this state, then its
  transition row, the probabilities of moving from this state to states 0, 1
  (and 2).
- `rb, b0, b1` (and `b2`): the same for the second action.
- `g`: the discount factor.

The two rows in one call are the two actions' rows out of the state being
updated, not rows out of states 0 and 1. To compute `(Tv)_1`, pass state 1's
rewards and state 1's two outgoing rows to `bellman_state1`.

The functions check nothing. They return a value for any `f32` inputs,
including rows that do not sum to one and a discount of 1 or more, and the
proved properties below say nothing about such inputs. Validate the rows and
`0 < g < 1` before calling.

## Example

Two states, discount 0.9, current values `v = (10, 20)`. In state 0 the first
action pays 1 and stays with probability 0.9; the second pays 0 and moves to
state 1 with probability 0.8. In state 1 the first action pays 2 and splits
evenly; the second pays 1 and stays.

```chelis
module Demo.Main
import Economoist.Bellman (bellman_state0, bellman_state1, bellman_state0_n3, fmax, fabs)
tv0 = bellman_state0(10.0f32, 20.0f32, 1.0f32, 0.9f32, 0.1f32, 0.0f32, 0.2f32, 0.8f32, 0.9f32)
tv1 = bellman_state1(10.0f32, 20.0f32, 2.0f32, 0.5f32, 0.5f32, 1.0f32, 0.0f32, 1.0f32, 0.9f32)
tw0 = bellman_state0(11.0f32, 20.0f32, 1.0f32, 0.9f32, 0.1f32, 0.0f32, 0.2f32, 0.8f32, 0.9f32)
gap0 = fabs((tw0 - tv0))
bound0 = (0.9f32 * fmax(fabs((11.0f32 - 10.0f32)), fabs((20.0f32 - 20.0f32))))
tv0_n3 = bellman_state0_n3(10.0f32, 20.0f32, 5.0f32, 1.0f32, 0.8f32, 0.1f32, 0.1f32, 0.0f32, 0.2f32, 0.3f32, 0.5f32, 0.9f32)
```

`chelis eval --file src/main.ch` prints:

```text
tv0 = 16.199999
tv1 = 19.0
tw0 = 16.380001
gap0 = 0.18000221
bound0 = 0.9
tv0_n3 = 10.45
```

In state 0 the first action is worth `1 + 0.9 * (0.9 * 10 + 0.1 * 20) = 10.9`
and the second `0 + 0.9 * (0.2 * 10 + 0.8 * 20) = 16.2`, so
`(Tv)_0 = 16.2` (`16.199999` after `f32` rounding). With `tv1`, one update
takes `v = (10, 20)` to `Tv = (16.2, 19)`. Raising `v0` to 11 moves `(Tv)_0`
by 0.18, inside the contraction bound `0.9 * 1 = 0.9` described next.

## Checked properties

The notation below uses `v <= w` for entrywise comparison (`v_j <= w_j` for
every state `j`) and `||v - w||_inf` for the largest entrywise gap,
`max over j of |v_j - w_j|`; the properties compute it with `fmax`, `fmax3`
and `fabs`.

Every property assumes that each transition row has entries `>= 0` that sum to
exactly one, and that `0 < g < 1`. All are proved by the cvc5 SMT solver over
real arithmetic, for one application of `T`:

| Two states | Three states | Result |
| --- | --- | --- |
| `bellman_monotone` | `bellman3_monotone` | Monotonicity at output state 0: `v <= w` implies `(Tv)_0 <= (Tw)_0`. |
| `bellman_bounded` | `bellman3_bounded` | Boundedness at output state 0: if `b, rmax >= 0`, every `v_j` is in `[-b, b]` and both rewards are in `[-rmax, rmax]`, then `(Tv)_0` is in `[-(rmax + g * b), rmax + g * b]`. |
| `bellman_contraction_state0`, `bellman_contraction_state1`, each with a `_lower` twin | `bellman_contraction_state0_n3`, `bellman_contraction_state1_n3`, `bellman_contraction_state2_n3`, each with a `_lower` twin | Contraction at every output state `s`: `(Tv)_s - (Tw)_s` is at most `g * \|\|v - w\|\|_inf` (upper property) and at least its negative (`_lower`). |

Monotonicity and boundedness are proved for output state 0 only. The
contraction bound is proved for every output state at both sizes, and taking
the maximum over `s` gives the vector form
`||Tv - Tw||_inf <= g * ||v - w||_inf` at two and at three states.

The row assumptions are what make the contraction bound hold. With a row that
sums to more than one, the solver finds values where the bound fails; with
`g >= 1` the bound can hold but its factor is no longer below one. The
[counterexamples page](../business-wrong.md) shows both.

For the three-state properties, run `chelis prove --tier smt-only --smt-timeout 20000`.
With the default tier and timeout, the solver can report them as unsupported
instead of proved.

## Scope

The contraction is proved for one application of `T`, at two or three states
with two actions. It does not prove that value iteration converges, that a
fixed point exists or is unique, or the same results for other state or
action counts. The monotonicity and boundedness results cover output state 0,
not the whole vector.

The solver treats these `f32` expressions as real arithmetic. The results do
not certify `f32` rounding: in the example, the computed `gap0` is
`0.18000221`, not exactly `0.18`.
