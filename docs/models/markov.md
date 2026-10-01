# Markov transitions

[`Economoist.Markov`](../../src/markov.ch) defines one transition of a distribution across two or three states. For input masses `p` and transition matrix `T`, each output mass is the sum of the input masses weighted by the corresponding column of `T`. The package provides separate `Dist2` and `Dist3` types and `advance` functions for the two sizes.

## Checked properties

The goals in [`properties/markov.ch`](../../properties/markov.ch) call the exported `next_mass` or `mass3_next` functions. Chelis checks each goal over real arithmetic.

| Goal | Guards | Result for one transition |
| --- | --- | --- |
| `markov_mass_preserved`, `markov3_mass_preserved` | Input masses sum exactly to one; every transition row sums exactly to one | Output masses sum exactly to one |
| `markov_nonneg_preserved`, `markov3_nonneg_preserved` | Input masses and transition entries are nonnegative | Every output mass is nonnegative |

The mass goals do not need a nonnegativity guard. The nonnegativity goals do not need a row-sum guard. Each goal has a separate guard-satisfiability witness that the prover is expected to refute.

`Dist2` and `Dist3` have a different, guarded contract: their masses are nonnegative and their sum lies within `0.0001` of one. The constructor and `advance` producer obligations check that returned distributions satisfy this invariant. `advance` requires nonnegative transition entries with rows summing exactly to one; an invalid row returns `None`. The type invariant allows a mass tolerance, whereas the separate mass-preservation goals above assume and prove exact sums.

## Scope

These checks cover one transition at two states and one at three states. They do not establish a result for arbitrary state counts. They also do not prove the existence or uniqueness of a stationary distribution, convergence of repeated transitions, or ergodicity.

The source uses `f32` values, but an SMT result here is about the corresponding real-arithmetic expression. It is not a guarantee that every floating-point run preserves an exact sum or stays inside the type's tolerance. The concrete cases in [`tests/markov.ch`](../../tests/markov.ch) exercise execution separately.
