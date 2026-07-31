# Draft: induction and fixed-point proof tier

## Summary

Economoist proves one-step Bellman monotonicity and contraction at fixed
dimensions. It deliberately does not generalize those results to convergence,
uniqueness of a fixed point, stationarity, ergodicity, or arbitrary state
dimension. Those claims require induction or a fixed-point argument beyond the
current quantifier-free SMT surface.

## Re-probe trigger

Revisit when Chelis adds an induction, recursive-proof, or proof-assistant tier.
At that point, promote only claims discharged by that tier and retain the
fixed-dimension/reals boundaries where they still apply.
