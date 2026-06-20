# Bellman operator (state 0, 2 states x 2 actions)

`src/bellman.ch` defines one application of the Bellman optimality operator T at
state 0 of a fixed small dynamic program: 2 states, 2 actions. The exported
operator is

```
bellman_state0(v0, v1, r0, p00, p01, r1, p10, p11, g)
  = max(r0 + g * (p00 * v0 + p01 * v1),
        r1 + g * (p10 * v0 + p11 * v1))
```

the max over the two actions of the immediate reward plus the discounted
expected continuation value under the chosen action's transition row. The 3
state form is identical term by term.

`properties/bellman.ch` proves four structural facts of this one step at the SMT
tier (cvc5, over the reals, zero fuzz, no contract). Each is paired with a
`*_guards_satisfiable` witness that cvc5 refutes, so the green is not vacuous.
`tests/bellman.ch` is a separate f32 evaluation check of the same operator on a
concrete instance.

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

2. **Fixed dimension vs general n.** Each green is proven at 2 states x 2
   actions (mirrored to 3 states), NOT for all state and action dimensions.
   "Bellman monotonicity proven" means the small fixed dimension instance, not
   the universal theorem over all `n` states and `m` actions. The general n, m
   result is HELD OUT alongside convergence.

3. **Reals vs floats.** The proven fact is a statement of real arithmetic
   (`arith_model: "real"`, as discharged by cvc5 over the reals). It is NOT a
   statement about f32 float behavior. The f32 evaluation in `tests/bellman.ch`
   is a separate, unproven concern.

## Proven properties

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

### bellman_contraction and bellman_contraction_lower

The difference between one Bellman step on v and one Bellman step on w is bounded
in absolute value by `g` times the sup norm distance between v and w. The upper
side (`bellman_contraction`) and the lower side (`bellman_contraction_lower`)
are proven as separate greens; together they are the full single application
g contraction in the sup norm.

- Says: a single application of T contracts by factor `g` in the sup norm, at
  2 states x 2 actions, over the reals.
- Does not say: that the iteration converges, that a fixed point exists or is
  unique, or that T contracts at general dimension. This contraction is a
  premise of the Banach fixed point argument, not its conclusion; the
  convergence and fixed point results are held out and need induction. It makes
  no f32 claim.
