# Economoist

A Chelis shell of verified economic and dynamic-programming models. Every
economic property is a genuine unqualified SMT green: proven at the SMT tier by
cvc5 over the reals, with zero fuzz samples and no contract assumption. This is
the strongest proven story in the stack, and the academic-launch surface for
"C Proof".

## Models

- [Markov chains](models/markov.md): a finite-state transition operator;
  simplex preservation under one step.
- [Bellman operator](models/bellman.md): monotonicity, boundedness, and the
  single-application contraction of the dynamic-programming operator.
- [Growth and present value](models/growth.md): the Gordon model's positivity
  and monotonicity, and the AD comparative statics whose signs are proven.

## Business-wrong demos

[`demos/businesswrong.ch`](../demos/businesswrong.ch) ships, for each structural
property, a corrupted twin that is refuted at the SMT tier with a decoded
counterexample, beside its passing control: a transition whose rows do not sum to
one, a Gordon model with growth at or above the discount, and a discount outside
the open interval from zero to one that breaks the contraction modulus. These are
the soundness-dependence twins, importable with stable IDs for C Note.

## Surfaces

- [Capability surface](CHELIS_SURFACE.md): what chelis and chelis-std provide to
  this domain, with `@pin` and `@upstream` markers.
- [Upstream bugs](UPSTREAM_BUGS.md): tracked gaps and their re-probe cadence.
- [C Note import surface](cnote-import-surface.json): the frozen machine-readable
  surface the academic Economics gallery vendors.

## The honesty boundaries

Every model states three held-out boundaries with equal weight: limit and
fixed-point results (convergence) need induction and are out; the structural
greens are the small-fixed-dimension instance, not the general-n theorem; and the
proofs are over the reals, not f32 float behavior.

## Gates

- `python3 scripts/prove_gate.py`: the SMT-green gate (every economic property
  proven, witnesses and twins refute, controls pass, name and doc lints clean).
- `python3 scripts/oracle_harness.py`: shell numerics versus recorded
  analytic-mirror goldens, plus the executable test suite.
- `python3 scripts/run_local_gate.py`: the full local gate.
