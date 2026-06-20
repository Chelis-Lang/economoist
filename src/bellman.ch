module Economoist.Bellman
export (bellman_state0, bellman_state1, bellman_state0_n3, bellman_state1_n3, bellman_state2_n3, fmax, fmax3, fabs)
-- Economoist.Bellman: the Bellman optimality operator T of a fixed small dynamic
-- program, one exported scalar def per output value-vector component. Two
-- instances ship: 2 states x 2 actions (bellman_state0, bellman_state1) and 3
-- states x 2 actions (bellman_state0_n3, bellman_state1_n3, bellman_state2_n3).
-- All the per-output-state forms are identical term by term; they differ only in
-- which output state's rewards and transition rows they carry.
--
-- One application of T at output state s is the max over the two actions of the
-- immediate reward plus the discounted expected continuation value, where the
-- continuation expectation is taken under the chosen action's transition row out
-- of state s. Action a contributes (r_a + g * (p_a0 * v0 + p_a1 * v1 + ...)); T
-- picks the larger. (Tv)_s is the operator at output state s.
--
-- PROVEN here (single application of T, SMT, transcendental-free, over the
-- reals): structural facts of one Bellman step, proven at BOTH shipped
-- dimensions, 2 states x 2 actions and 3 states x 2 actions ---
--   bellman_monotone / bellman3_monotone     : T is monotone in the
--                          continuation value function.
--   bellman_bounded / bellman3_bounded         : one step is sup-norm bounded
--                          by rmax + g * b.
--   bellman_contraction_state0/_state1 (n=2)   : each output value-vector
--                          component (Tv)_s is a g-contraction in the sup norm
--                          (two-sided; upper and lower side each proven). The
--                          FULL sup-norm contraction over the output vector is
--                          the max of these per-component facts (see
--                          docs/models/bellman.md).
-- The property goals INLINE the operator body (they write the fmax(...)
-- arithmetic directly rather than calling these defs): in chelis 0.8.0 a goal
-- that subtracts or compares two calls of the same if/then/else-bodied def
-- collapses the pair to a constant and would mask a false bound, false-proving
-- it at the SMT tier (chelis#426), so the contraction and monotonicity goals are
-- stated inline against the same arithmetic these defs compute. The inlined goal
-- is textually the operator body (single-expression discipline); the exported
-- defs ship and are pinned numerically in tests/bellman.ch.
-- HELD OUT (see docs/models/bellman.md): value-iteration convergence
--   v_{k+1} = T v_k -> v*, existence and uniqueness of the fixed point (the
--   Banach argument), which need induction; the general all-n-state, all-m-
--   action theorem (the greens cover the two fixed instances n=2 and n=3 at
--   m=2, not the all-n,m result); the n=3 per-component contraction (its goal
--   does not lower at this tier, see docs); and any f32 float claim (the green
--   is real arithmetic).
-- Scalar binary max, scalar ternary max, and scalar absolute value, as
-- if/then/else over operator comparisons. fmax and fabs exist because chelis
-- 0.8.0 has no bound scalar max/abs builtin for f32 (a bare max/abs is an
-- unbound variable, chelis#424); written as if/then/else they lower to ITE in
-- QF_NRA so goals over them discharge at the SMT tier. fmax3 is the three-state
-- sup norm's max as one ITE-bodied def because a nested fmax(a, fmax(b, c))
-- written directly at a goal site does NOT lower to Tier B (chelis#425), so the
-- 3-state sup norm uses fmax3 rather than nesting fmax.
def fmax(a: f32, b: f32) -> f32 = if (a >= b) then a else b
def fmax3(a: f32, b: f32, c: f32) -> f32 = if (a >= b) then if (a >= c) then a else c else if (b >= c) then b else c
def fabs(x: f32) -> f32 = if (x >= 0.0) then x else (0.0 - x)
-- (Tv)_0, two-state form: max over actions of reward plus discounted expected
-- continuation under output-state-0's transition rows p0*, p1*.
def bellman_state0(v0: f32, v1: f32, r0: f32, p00: f32, p01: f32, r1: f32, p10: f32, p11: f32, g: f32) -> f32 = fmax((r0 + (g * ((p00 * v0) + (p01 * v1)))), (r1 + (g * ((p10 * v0) + (p11 * v1)))))
-- (Tv)_1, two-state form: same operator carrying output-state-1's rewards rr0,
-- rr1 and transition rows q0*, q1*. Identical term by term to (Tv)_0.
def bellman_state1(v0: f32, v1: f32, rr0: f32, q00: f32, q01: f32, rr1: f32, q10: f32, q11: f32, g: f32) -> f32 = fmax((rr0 + (g * ((q00 * v0) + (q01 * v1)))), (rr1 + (g * ((q10 * v0) + (q11 * v1)))))
-- (Tv)_0, three-state form: same operator carrying a third state. v0, v1, v2 are
-- the continuation values; r0/r1 the action rewards; p0* and p1* the two
-- transition rows out of state 0 over the three states. Identical term by term
-- to the two-state form, with one extra term per action's expectation.
def bellman_state0_n3(v0: f32, v1: f32, v2: f32, r0: f32, p00: f32, p01: f32, p02: f32, r1: f32, p10: f32, p11: f32, p12: f32, g: f32) -> f32 = fmax((r0 + (g * (((p00 * v0) + (p01 * v1)) + (p02 * v2)))), (r1 + (g * (((p10 * v0) + (p11 * v1)) + (p12 * v2)))))
-- (Tv)_1, three-state form: output-state-1's rewards rr0, rr1 and transition
-- rows q0*, q1* out of state 1 over the three states.
def bellman_state1_n3(v0: f32, v1: f32, v2: f32, rr0: f32, q00: f32, q01: f32, q02: f32, rr1: f32, q10: f32, q11: f32, q12: f32, g: f32) -> f32 = fmax((rr0 + (g * (((q00 * v0) + (q01 * v1)) + (q02 * v2)))), (rr1 + (g * (((q10 * v0) + (q11 * v1)) + (q12 * v2)))))
-- (Tv)_2, three-state form: output-state-2's rewards rs0, rs1 and transition
-- rows s0*, s1* out of state 2 over the three states.
def bellman_state2_n3(v0: f32, v1: f32, v2: f32, rs0: f32, s00: f32, s01: f32, s02: f32, rs1: f32, s10: f32, s11: f32, s12: f32, g: f32) -> f32 = fmax((rs0 + (g * (((s00 * v0) + (s01 * v1)) + (s02 * v2)))), (rs1 + (g * (((s10 * v0) + (s11 * v1)) + (s12 * v2)))))
