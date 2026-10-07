# Counterexample examples

Each model's results hold only under their assumptions. The pairs below show
what happens when one assumption is dropped: the claim without it fails and
the cvc5 solver returns a counterexample, while a control with the assumption
restored is proved. A counterexample here shows that the assumption is needed;
it is not a defect in the model.

## Run a pair yourself

A property in your own project can import the Economoist functions and be
checked with `chelis prove`.
[Getting started](getting-started.md) runs the Gordon pair
this way:

```chelis
module Demo.Main
import Economoist.Growth (gordon_pv)
@property gordon_positive_wrong forall(d: f32, r: f32, g: f32) where d > 0.0, g > r:
  (gordon_pv(d, r, g) > 0.0)
@property gordon_positive_control forall(d: f32, r: f32, g: f32) where d > 0.0, r > g:
  (gordon_pv(d, r, g) > 0.0)
```

```text
property failure: gordon_positive_wrong
  --> src/main.ch
property: gordon_positive_control -- 0/0 passed
1 passed, 1 failed, 0 unsupported, 0 errors
```

`chelis prove --json` adds the counterexample to the failed property's
record. The solver works over the reals, so it prints fractions in SMT form:
`(/ 3 2)` is 1.5 and `(- 1.0)` is -1.

## The pairs

Each claim below drops one assumption from a proved property.
The counterexample is the one cvc5 returned with Chelis 0.19.1.

| Claim | Assumption removed | Counterexample | What goes wrong |
| --- | --- | --- | --- |
| Markov mass preservation, two states | Row 1 sums to one | `p = (0, 1)`, row 0 `(1, 0)`, row 1 `(0, 0)` | Output masses sum to 0 |
| Markov mass preservation, three states | Row 2 sums to one | `p = (1, 1, -1)`, rows `(1, 1, -1)`, `(1, 0, 0)`, `(0, 0, 0)` | Output masses sum to 2 |
| Gordon positivity | `r > g` (replaced by `g > r`) | `d = 1, r = -1, g = 0` | `P = -1` |
| Gordon strict positivity | `r > g + 0.01` (replaced by `g > r`) | `d = 1, r = -1, g = 0` | `P = -1` |
| Gordon decreasing in `r` | `r2 > r1` | `d = 0.125, g = 1, r1 = 1.25, r2 = 7/6` | `r2` is below `r1`, and `P` is 0.75 at `r2` against 0.5 at `r1` |
| Bellman contraction, two states | Second action's row sums to one | Second row `(1, 1)`, `g = 0.5` | The update moves by more than `g` times the value gap |
| Bellman contraction, three states | Second action's row sums to one | A second row summing to 2, `g = 0.5` | As above |
| Bellman contraction factor below one | `g < 1` | `g = 1.5` | The bound holds, but with factor 1.5 it is not a contraction |
| Bellman monotonicity | `v <= w` | `v = (-0.5, -1)`, `w = (-1, -1)`, `g = 0.5` | `(Tv)_0 > (Tw)_0` |

Two notes on reading the table. The Markov mass failure needs only a row that
does not sum to one; the three-state counterexample happens to use negative masses
as well, which is allowed because the claim, like the proved property, does not assume nonnegativity.
The modulus row is not a failure of the bound itself: the per-state bound
holds for any `g >= 0`, and what breaks is the claim that its factor is below
one.

One further pair tests a wrong model rather than a missing assumption.
`gordon_pv_negated` returns `-(d / (r - g))`. Under the correct assumptions
`d > 0` and `r > g`, its positivity claim fails at `d = 1, r = 1, g = 0`,
where it returns `-1`, while the same claim about `gordon_pv` is proved. This
is the shape of a defect inside the valid domain, as opposed to inputs outside
it.

The assumptions behind each model are on the
[Markov](models/markov.md),
[Bellman](models/bellman.md) and
[Gordon](models/growth.md) pages.
