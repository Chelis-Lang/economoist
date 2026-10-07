# Economoist

[Economoist](https://github.com/Chelis-Lang/economoist) is a Chelis library of
three small economic models, each a set of scalar `f32` functions:

- `Economoist.Markov`: one step of a two- or three-state Markov chain, with a
  guarded distribution type that refuses negative masses and totals more than
  0.0001 from one.
- `Economoist.Bellman`: one Bellman optimality update at two or three states
  with two actions per state.
- `Economoist.Growth`: the Gordon present value `D / (r - g)`, with checked
  variants that refuse a required return at or below the growth rate.

Each model comes with stated properties, and the two kinds of evidence behind
them are kept apart. The structural properties (mass preservation,
monotonicity, the contraction bound, Gordon positivity) are proved by the cvc5
SMT solver over real arithmetic, under their written assumptions. The one
sensitivity result, that the automatic-differentiation derivative of the
Gordon value with respect to `r` is negative, is validated by 500 seeded
random samples, not proved. Neither kind of result covers every `f32`
execution after rounding.

[Getting started](getting-started.md) adds the dependency and
runs a first program. The [model guide](models.md) lists each
model's functions and checked claims, and
[Boundaries](boundaries.md) states what those claims leave out.

## License

MIT. See the project's [LICENSE](https://github.com/Chelis-Lang/economoist/tree/main/LICENSE).
