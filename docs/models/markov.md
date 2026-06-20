# Markov chains (Economoist.Markov)

A finite-state Markov transition operator over a fixed small state space. A
distribution on the simplex is a vector of nonnegative masses summing to one. A
row-stochastic transition has nonnegative rows that each sum to one. The next
distribution is the transition applied to the current one.

## Proven (single application, SMT tier, cvc5, over the reals)

Each result below is discharged at `proof_tier:"smt"` with `arith_model:"real"`,
zero fuzz samples, and no contract assumption.

- `invariant:Dist2:advance` (the producer obligation for `advance`): applying a
  row-stochastic transition to a distribution on the simplex yields a
  distribution on the simplex. Nonnegativity preserved and total mass preserved
  are proven together inside the simplex invariant.
- `invariant:Dist2:make_dist`: the guarded constructor produces a valid simplex
  distribution.
- `markov_mass_preserved`: the output masses sum to one, as an exact
  real-arithmetic identity.
- `markov_nonneg_preserved`: the output masses are nonnegative.

Each proven property carries a `*_guards_satisfiable` non-vacuity witness that is
refuted at the SMT tier, so cvc5 exhibits a guard-satisfying model and the green
is not vacuous.

## Held out (not proven here)

These three boundaries are stated with equal weight. A single-step green is not
any of them.

1. Limit results need induction. The existence and uniqueness of a stationary
   distribution, convergence to stationarity, and ergodicity are limits of the
   iterated transition. They need an inductive or fixed-point argument and are
   out of scope for direct SMT. The single-step preservation green does not imply
   them.
2. General state dimension is held out alongside the limit results. The proofs
   here are the n equals two instance (the n equals three form is identical entry
   by entry). They are not the all-n theorem. "Simplex preservation proven" means
   proven at the small fixed dimension, not for every state space size; the
   general-n result, like convergence, is not reachable by SMT at fixed size.
3. Reals, not floats. What is proven is the real-arithmetic fact
   (`arith_model:"real"`). The exact mass identity `markov_mass_preserved` holds
   over the reals. The `Dist2` invariant carries an f32 epsilon band on the sum
   because the runtime is f32; that band is the runtime invariant, distinct from
   the exact real-arithmetic identity the prover discharges. The proof is about
   the real-arithmetic model, not f32 float behavior.
