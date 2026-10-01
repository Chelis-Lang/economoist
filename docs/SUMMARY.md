# Economoist model guide

Economoist checks specific claims about three models. Each page names the guards, the result checked, and what lies outside that result. The [README](../README.md#run-from-a-source-checkout) has a source-checkout workflow.

## Models

- [Markov chains](models/markov.md) — one transition at two and three states: distribution-type obligations, exact mass preservation, and nonnegative output masses under their respective guards.
- [Bellman operator](models/bellman.md) — one update at two and three states with two actions: state-0 monotonicity and boundedness, plus a two-sided contraction bound at every shipped output state.
- [Gordon present value](models/growth.md) — positivity and two-point comparisons for `D / (r - g)`, a stricter discount-spread variant, and a separate sampled AD check.

## Reading proof results

`chelis prove` checks one file or package. The checked `properties/` goals and the distribution-type obligations in `src/` use SMT over the reals. In JSON output, a passing checked goal reports `status: "passed"`, `proof_tier: "smt"`, `arith_model: "real"`, and `samples: 0`. It applies under its written `where` guards. It does not establish floating-point behavior, iteration limits, or results at dimensions absent from the source.

Each `properties/` file also contains `*_guards_satisfiable` witnesses. They assert `false` under the corresponding guards. A counterexample shows those guards admit an input, so a raw `chelis prove` run can exit nonzero even when the package is healthy. `demos/businesswrong.ch` likewise has selected false claims paired with passing controls. A counterexample to a false claim means the negated goal is satisfiable.

`sampled/growth_sensitivity.ch` checks the sign of an AD derivative at generated inputs. It uses sampling rather than SMT proof; its `_wrong` companion is expected to fail with a counterexample. Run `.venv/bin/python scripts/prove_gate.py` from the checkout to check all these expected outcomes together. The gate prints a text verdict and exits zero only when they match.

For concrete model values, run `chelis test tests/`. The complete local workflow is `.venv/bin/python scripts/run_local_gate.py`.
