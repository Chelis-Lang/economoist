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
tier (cvc5, over the reals, zero fuzz, no contract). Each property goal now CALLS
the exported `bellman_state0`/`bellman_state1` (and the `_n3` variants) DIRECTLY
at the goal site -- for example `bellman_state0(v...) - bellman_state0(w...)` for
a contraction -- so the green is a fact about the shipped operator, not a
separate restatement. An earlier cut had to INLINE the operator arithmetic
instead: in chelis 0.8.0 a goal that subtracted or compared two calls of the same
`if/then/else`-bodied def collapsed the pair to the all-arguments-equal corner
and false-proved a false bound at the SMT tier (chelis#426). That soundness bug
was fixed upstream at chelis 0.10.0 and re-verified at the 0.14.0 pin via probe
p04 (the satisfying two-call goal proves; the corrupted twin refutes with a
counterexample), so the goals call the operators directly and the former
`unsound_pattern_lint` was removed. A regression control pair
`bellman_call_collapse_wrong` / `bellman_call_collapse_control` in `demos/` keeps
the fixed behavior under watch. Each real property is paired with a
`*_guards_satisfiable` witness that cvc5 refutes, so the green is not vacuous.

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
`max(|(Tv)_0 - (Tw)_0|, |(Tv)_1 - (Tw)_1|) <= g * sup`, is not itself shipped as
a separate green: the full sup-norm is the max of the per-output-state
components, a one-line arithmetic corollary of the two per-state greens rather
than an independent SMT goal. The honest headline is therefore the
per-output-state contraction at both output states, two-sided, with the full
sup-norm stated as their max. (The nested-`fmax` lowering gap that once forced
this framing, chelis#425, was fixed in 0.14.0; the n=3 per-output-state
contraction with the `fmax3` three-coordinate sup now lowers and ships as a green
-- see the n=3 section below.)

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

### bellman_contraction_state{0,1,2}_n3 / _lower

For each output state `s` in `{0, 1, 2}`, the difference between one Bellman step
on v and one Bellman step on w at that output state is bounded in absolute value
by `g` times the sup-norm distance between v and w over the three coordinates.
The upper side (`bellman_contraction_state0_n3`, `_state1_n3`, `_state2_n3`) and
the lower side (`..._lower`) are proven as separate greens -- six unqualified SMT
greens in all, each paired with a `*_guards_satisfiable` witness that refutes.
The goal calls `bellman_state0_n3(v...) - bellman_state0_n3(w...)` (two-call
subtraction, sound since chelis#426) on the left and the `fmax3` three-coordinate
sup `g * fmax3(|v0-w0|, |v1-w1|, |v2-w2|)` on the right.

- Says: each output value-vector component `(Tv)_s` is a g contraction in the sup
  norm, at 3 states x 2 actions, over the reals; the full n=3 sup-norm
  contraction is the max of these three per-state components, as at n=2.
- Does not say: that the iteration converges, that a fixed point exists or is
  unique, or that T contracts at general dimension. The convergence, fixed point,
  and general-`n` results are held out and need induction. It makes no f32 claim.

### De-narrowed at n=3: the per-output-state contraction now ships

The n=3 per-output-state contraction (each per-state difference bounded by `g`
times `fmax3` over the three coordinate distances) was PREVIOUSLY HELD OUT
because its goal did not lower to the SMT tier (the three-state sup norm `fmax3`
over nonlinear arguments exceeded the lowering limit; cvc5 reported it
unsupported, not proven). At 0.14.0 chelis#425 was fixed: the goal now
lowers and all six greens ship (`bellman_contraction_state{0,1,2}_n3` and their
`_lower` twins), verified via probe p15 and per-surface (all three output states,
upper and lower, prove; the six witnesses refute). It is therefore no longer on
the held-out list.

Still HELD OUT at every dimension, including n=3: value-iteration convergence
`v_{k+1} = T v_k -> v*`, the existence and uniqueness of the fixed point (the
Banach conclusion), and the general-`n`, general-`m` theorem. These need
induction or a fixed-point argument and are not reachable by SMT at a fixed size;
the single-application contraction proven here is a premise of the Banach
theorem, not its conclusion.
