# Bellman operator

[`Economoist.Bellman`](../../src/bellman.ch) computes one Bellman optimality update. At each output state, it takes the larger of two action values: immediate reward plus discounted expected continuation value. The package implements this for two states and three states, with two actions per state. The outputs are separate functions, such as `bellman_state0` and `bellman_state0_n3`.

## Checked properties

[`properties/bellman.ch`](../../properties/bellman.ch) checks the exported functions under nonnegative transition entries, transition rows summing to one, and a discount `0 < g < 1`. Each property concerns **one application** of the operator. Both state sizes have these goals:

| Goal at two states | Goal at three states | What it checks |
| --- | --- | --- |
| `bellman_monotone` | `bellman3_monotone` | For output **state 0**, entrywise `v ≤ w` implies `(Tv)₀ ≤ (Tw)₀`. |
| `bellman_bounded` | `bellman3_bounded` | For output **state 0**, if `b, rmax ≥ 0`, continuation values lie in `[-b, b]`, and both action rewards lie in `[-rmax, rmax]`, then `(Tv)₀` lies in `[-(rmax + g b), rmax + g b]`. |
| `bellman_contraction_state0`, `bellman_contraction_state1` and their `_lower` goals | `bellman_contraction_state0_n3`, `bellman_contraction_state1_n3`, `bellman_contraction_state2_n3` and their `_lower` goals | At **every shipped output state**, the upper and lower goals together give `|(Tv)ₛ - (Tw)ₛ| ≤ g ‖v-w‖∞`. |

The monotonicity and boundedness goals name only state 0 at each size. The source has no separate SMT goals for those claims at the other output states. The contraction goals do cover every output state at each size; taking the maximum of their per-state bounds gives the full vector sup-norm bound at that fixed size. The combined inequality is an arithmetic consequence of the checked goals, not a separate prover record. Each checked goal has a guard-satisfiability witness that is expected to produce a counterexample.

The discount guard has two roles. Nonnegative, row-stochastic action transitions support the difference bound. `g < 1` makes its factor strictly less than one. The selected examples in [`demos/businesswrong.ch`](../../demos/businesswrong.ch) show a missing row-sum guard can break the bound, while `g ≥ 1` breaks the strict-modulus condition even when the bound itself holds.

## Scope

The checked contraction applies once, at two or three states with two actions. It does not prove convergence of value iteration, existence or uniqueness of a fixed point, or the same result for arbitrary state and action counts. The separate state-0 monotonicity and boundedness checks must not be read as vector-wide prover results.

SMT interprets these `f32` expressions over the reals. It does not certify the corresponding floating-point executions. [`tests/bellman.ch`](../../tests/bellman.ch) checks concrete values separately.
