module Economoist.Bellman
export (bellman_state0, fmax, fabs)
-- Economoist.Bellman: the Bellman optimality operator T at state 0 of a fixed
-- small dynamic program (2 states, 2 actions; the 3-state form is identical
-- term by term).
--
-- One application of T at state 0 is the max over the two actions of the
-- immediate reward plus the discounted expected continuation value, where the
-- continuation expectation is taken under the chosen action's transition row.
-- Action a contributes (r_a + g * (p_a0 * v0 + p_a1 * v1)); T picks the larger.
--
-- PROVEN here (single application of T, SMT, transcendental-free, over the
-- reals): structural facts of one Bellman step against bellman_state0 ---
--   bellman_monotone     : T is monotone in the continuation value function.
--   bellman_bounded       : one step is sup-norm bounded by rmax + g * b.
--   bellman_contraction* : one step is a g-contraction in the sup norm
--                          (two-sided, the upper and lower side each proven).
-- HELD OUT (see docs/models/bellman.md): value-iteration convergence
--   v_{k+1} = T v_k -> v*, existence and uniqueness of the fixed point (the
--   Banach argument), which need induction; the general n-state, m-action
--   theorem (this is the 2 x 2, mirrored 3-state, instance, not the all-n,m
--   result); and any f32 float claim (the green is real arithmetic).
-- Scalar binary max and scalar absolute value, as if/then/else over operator
-- comparisons. chelis 0.8.0 has no bare scalar max/abs builtin; these helpers
-- lower to ITE in QF_NRA so goals over them discharge at the SMT tier.
def fmax(a: f32, b: f32) -> f32 = if (a >= b) then a else b
def fabs(x: f32) -> f32 = if (x >= 0.0) then x else (0.0 - x)
def bellman_state0(v0: f32, v1: f32, r0: f32, p00: f32, p01: f32, r1: f32, p10: f32, p11: f32, g: f32) -> f32 = fmax((r0 + (g * ((p00 * v0) + (p01 * v1)))), (r1 + (g * ((p10 * v0) + (p11 * v1)))))
