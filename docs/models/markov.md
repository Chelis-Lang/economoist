# Markov transitions

[`Economoist.Markov`](../../src/markov.ch) defines one transition of a distribution across two or three states. For input masses `p` and transition matrix `T`, each output mass is the sum of the input masses weighted by the corresponding column of `T`. The package provides separate `Dist2` and `Dist3` types and `advance` functions for the two sizes.

## Checked properties

The goals in [`properties/markov.ch`](../../properties/markov.ch) call the exported `next_mass` or `mass3_next` functions. Chelis checks each goal over real arithmetic.

| Goal | Guards | Result for one transition |
| --- | --- | --- |
| `markov_mass_preserved`, `markov3_mass_preserved` | Input masses sum exactly to one; every transition row sums exactly to one | Output masses sum exactly to one |
| `markov_nonneg_preserved`, `markov3_nonneg_preserved` | Input masses and transition entries are nonnegative | Every output mass is nonnegative |

The mass goals do not need a nonnegativity guard. The nonnegativity goals do not need a row-sum guard. Each goal has a separate guard-satisfiability witness that the prover is expected to refute.

`Dist2` and `Dist3` have a different, guarded contract: their masses are nonnegative and their sum lies within `0.0001` of one. The constructor and `advance` producer obligations check that returned distributions satisfy this invariant. The type invariant allows a mass tolerance, whereas the separate mass-preservation goals above assume and prove exact sums.

## What `advance` admits

`advance` and `advance3` admit a transition when all three of these hold, and return `None` otherwise:

1. every transition entry is nonnegative;
2. every row sum lies within `0.0001` of one — the same `eps()` band the distribution invariant carries, not exact equality;
3. the masses the step computes sum to within `0.0001` of one.

Condition 2 is a tolerance on representation, not an allowance on row-stochasticity. A row whose own sum is more than `0.0001` from one is refused, and so is a row sitting exactly at that distance, because the `f32` sum of its entries falls an ulp outside the `f32` band endpoint. A transition matrix estimated from data may therefore still need normalizing before `advance` will admit it.

Condition 3 is what keeps the producer obligation discharging, and it is not redundant. Banding the row sums on their own breaks the obligation: a distribution summing to `1 + eps` under rows summing to `1 + eps` gives an output summing to `(1 + eps)²`, which is outside the band, and the prover returns an SMT counterexample. Checking the masses the step actually computes closes that gap by construction. It also means the mass-sum half of the invariant is tested at run time, on the value's own `f32` sum, and not only proved over the reals — which is what stops a chain of steps drifting out of the band unnoticed. Two limits on that sentence: output nonnegativity is not asserted by the guard at all, only derived over the reals; and the `f32` band is marginally wider than the real one the obligation proves, since `f32(1.0 - eps())` sits about `1.7e-8` below `1 - eps` exactly. The run-time check is a tolerance test, not a certificate — the reals-versus-floats caveat under **Scope** applies to it as much as to the goals.

Two consequences are worth stating plainly. The rows condition 2 newly admits are **guarded, not proved**: `markov_mass_preserved` still assumes exact row sums, so it says nothing about a banded row, and the safety of those rows rests on condition 3 holding at run time. And tolerance compounds, so a caller chaining `advance` can accumulate drift until condition 3 fails. Such a chain stops with `None` rather than carrying a distribution outside its own band, but whether a given matrix is admitted then depends on the history of the chain and not only on the matrix.

## Scope

These checks cover one transition at two states and one at three states. They do not establish a result for arbitrary state counts. They also do not prove the existence or uniqueness of a stationary distribution, convergence of repeated transitions, or ergodicity.

The source uses `f32` values, but an SMT result here is about the corresponding real-arithmetic expression. It is not a guarantee that every floating-point run preserves an exact sum. Staying inside the type's tolerance is a separate, run-time matter: `make_dist`, `make_dist3`, `advance` and `advance3` each check the band in `f32` before returning a value, which is why they return `Option`. The concrete cases in [`tests/markov.ch`](../../tests/markov.ch) exercise execution separately, including the transitions the guard refuses.
