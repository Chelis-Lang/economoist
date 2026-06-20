# Bellman operator (2 states x 2 actions and 3 states x 2 actions)

`src/bellman.ch` defines one application of the Bellman optimality operator T of
a fixed small dynamic program, one exported scalar def per output value-vector
component, at two shipped dimensions: 2 states x 2 actions and 3 states x 2
actions. The exported per-output-state operators are

```
bellman_state0(v0, v1, r0, p00, p01, r1, p10, p11, g)
  = max(r0 + g * (p00 * v0 + p01 * v1),
        r1 + g * (p10 * v0 + p11 * v1))          -- (Tv)_0, n=2

bellman_state1(v0, v1, rr0, q00, q01, rr1, q10, q11, g)
  = max(rr0 + g * (q00 * v0 + q01 * v1),
        rr1 + g * (q10 * v0 + q11 * v1))          -- (Tv)_1, n=2

bellman_state0_n3(...)   -- (Tv)_0, n=3
bellman_state1_n3(...)   -- (Tv)_1, n=3
bellman_state2_n3(...)   -- (Tv)_2, n=3
```

each the max over the two actions of the immediate reward plus the discounted
expected continuation value under the chosen action's transition row out of that
output state. The per-output-state forms are identical term by term; they differ
only in which output state's rewards and transition rows they carry. The 3 state
forms add one extra state. All five operators ship and are pinned numerically in
`tests/bellman.ch`.

`properties/bellman.ch` proves the structural facts of this one step at the SMT
tier (cvc5, over the reals, zero fuzz, no contract). Each property goal INLINES
the operator arithmetic (it writes the `max(...)` of the two actions directly)
rather than calling the `bellman_state*` defs: in chelis 0.8.0 a goal that
subtracts or compares two calls of the same `if/then/else`-bodied def, such as
`bellman_state0(v...) - bellman_state0(w...)`, collapses the pair to a constant
and would mask a false bound, false-proving it at the SMT tier (chelis#426), so
the contraction and monotonicity goals are stated inline against the same
arithmetic the operators compute (the inlined goal is textually the operator
body). Each real property is paired with a `*_guards_satisfiable` witness that
cvc5 refutes, so the green is not vacuous.

Every green below is one application of T. Read each against the three
boundaries, which carry equal weight. A green here is a "C Proof" of the single
step it names and nothing past it.

## The three honesty boundaries

1. **Single step vs limit.** These are ONE application of the Bellman operator
   T. Value iteration convergence `v_{k+1} = T v_k -> v*`, the existence and
   uniqueness of the fixed point (the Banach argument), and any limit or
   stationarity claim are HELD OUT: they need induction over the iteration. The
   single application contraction proven here is a premise of the Banach
   theorem, not its conclusion. A green on the one step contraction is NOT a
   convergence theorem.

2. **Fixed dimension vs general n.** Each green is proven at two fixed
   dimensions that both ship, 2 states x 2 actions and 3 states x 2 actions, NOT
   for all state and action dimensions. "Bellman monotonicity proven" means
   these two small fixed dimension instances (`n=2` and `n=3` at `m=2`), each
   discharged as its own SMT green, not the universal theorem over all `n`
   states and `m` actions. The general all-`n`, all-`m` result is HELD OUT
   alongside convergence.

3. **Reals vs floats.** The proven fact is a statement of real arithmetic
   (`arith_model: "real"`, as discharged by cvc5 over the reals). It is NOT a
   statement about f32 float behavior. The f32 evaluation in `tests/bellman.ch`
   is a separate, unproven concern.

## What the sup-norm contraction headline means

The full sup-norm contraction over the output value vector is
`||Tv - Tw||_inf <= g * ||v - w||_inf`, which expands to: for EVERY output state
`s`, `|(Tv)_s - (Tw)_s| <= g * sup_j |v_j - w_j|`. At `n=2` this is exactly two
per-output-state facts (output state 0 and output state 1), each two-sided. Those
two per-output-state facts are what is proven here, each as its own SMT green:
`bellman_contraction_state0` / `_lower` and `bellman_contraction_state1` /
`_lower`. The full sup-norm contraction at `n=2` is then the MAX of these proven
per-output-state components (the max of two quantities that are each `<= X` is
itself `<= X`); it is a one-line arithmetic corollary of the four greens, not a
separate SMT green. A single per-output-state component (for example output state
0 alone) is NOT the full sup-norm contraction; it is one of the two components
the full contraction is the max over.

The full sup-norm written as one goal,
`max(|(Tv)_0 - (Tw)_0|, |(Tv)_1 - (Tw)_1|) <= g * sup`, does NOT lower to the
SMT tier (the outer max wraps arguments that each already contain a max over the
two actions, a nested-max site that does not lower, chelis#425), so it is not
itself shipped as a green. The honest headline is therefore the per-output-state
contraction at both output states, two-sided, with the full sup-norm stated as
their max.

## The two contraction guards: which is load-bearing for which claim

- `g in (0, 1)` is the contraction-MODULUS condition. The single-application
  bound `|(Tv)_s - (Tw)_s| <= g * sup` is the Lipschitz bound and holds for ANY
  `g >= 0`; what `g < 1` buys is that the modulus is strictly below one, the
  premise the Banach argument needs to iterate to a fixed point. `g < 1` is
  carried as a guard on every contraction property, and the demo
  `bellman_contraction_modulus_wrong` in `demos/businesswrong.ch` shows that
  dropping it to `g > 0` lets cvc5 return a discount `g >= 1` that satisfies the
  bound yet breaks the modulus-below-one claim.
- ROW-STOCHASTICITY (each action's transition row is nonneg and sums to one) is
  the load-bearing guard for the BOUND itself. Drop a row's `sum == 1.0` and a
  row summing above one lets the discounted expected continuation amplify the
  value gap, so the difference can exceed `g * sup`. The soundness twin
  `bellman_contraction_rowsum_wrong` in `demos/businesswrong.ch` refutes at the
  SMT tier with a decoded non-stochastic row; its control with both row sums
  restored passes.

## Proven properties (n=2, 2 states x 2 actions)

### bellman_monotone

If the continuation value function v is dominated entrywise by w
(`v0 <= w0` and `v1 <= w1`), then one Bellman step on v is at most one Bellman
step on w, given row stochastic transitions and a discount `g` in `(0, 1)`.

- Says: monotonicity of a single application of T, at 2 states x 2 actions,
  over the reals.
- Does not say: monotonicity of the value iterate `v_k`, of the limit `v*`, or
  of T at general dimension; and it makes no f32 claim.

### bellman_bounded

With every value entry in `[-b, b]` and every reward in `[-rmax, rmax]`, one
Bellman step lands in `[-(rmax + g * b), rmax + g * b]`. The bound is two sided
and proven as a single conjunction.

- Says: a sup norm bound on one application of T, at 2 states x 2 actions, over
  the reals.
- Does not say: a bound on the fixed point `v*` or on the iterate after many
  steps, nor a bound at general dimension; and it makes no f32 claim.

### bellman_contraction_state0 / _lower and bellman_contraction_state1 / _lower

For each output state `s` in `{0, 1}`, the difference between one Bellman step on
v and one Bellman step on w at that output state is bounded in absolute value by
`g` times the sup norm distance between v and w. The upper side
(`bellman_contraction_state0`, `bellman_contraction_state1`) and the lower side
(`..._lower`) are proven as separate greens; together the four are the
per-output-state g contraction at both output states, two-sided.

- Says: each output value-vector component `(Tv)_s` is a g contraction in the
  sup norm, at 2 states x 2 actions, over the reals; the full sup-norm
  contraction is the max of these two components (see above).
- Does not say: that the iteration converges, that a fixed point exists or is
  unique, or that T contracts at general dimension. The contraction is a
  premise of the Banach fixed point argument, not its conclusion; the
  convergence and fixed point results are held out and need induction. It makes
  no f32 claim, and a single component alone is not the full sup-norm
  contraction.

## Proven properties (n=3, 3 states x 2 actions)

### bellman3_monotone

If v is dominated entrywise by w over all three states
(`v0 <= w0`, `v1 <= w1`, `v2 <= w2`), then one Bellman step on v is at most one
Bellman step on w, given row stochastic transitions over three states and a
discount `g` in `(0, 1)`.

- Says: monotonicity of a single application of T, at 3 states x 2 actions, over
  the reals.
- Does not say: monotonicity of the value iterate `v_k`, of the limit `v*`, or
  of T at general dimension; and it makes no f32 claim.

### bellman3_bounded

With every value entry in `[-b, b]` and every reward in `[-rmax, rmax]`, one
Bellman step lands in `[-(rmax + g * b), rmax + g * b]`. The bound is two sided
and proven as a single conjunction.

- Says: a sup norm bound on one application of T, at 3 states x 2 actions, over
  the reals.
- Does not say: a bound on the fixed point `v*` or on the iterate after many
  steps, nor a bound at general dimension; and it makes no f32 claim.

### Held out at n=3: the per-output-state contraction

The n=3 per-output-state contraction (the per-state difference bounded by `g`
times `fmax3` over the three coordinate distances) is HELD OUT: at this dimension
its goal does not lower to the SMT tier (the three-state sup norm `fmax3` over
nonlinear arguments exceeds the lowering limit; cvc5 reports it unsupported, not
proven), so no green is claimed for it. The n=3 monotonicity and bound above are
the n=3 greens; the n=3 contraction joins convergence, the fixed point, and the
general-`n` theorem on the held-out list.
