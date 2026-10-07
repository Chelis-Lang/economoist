module Economoist.Bellman
export (bellman_state0, bellman_state1, bellman_state0_n3, bellman_state1_n3, bellman_state2_n3, fmax, fmax3, fabs)
-- One Bellman update at two or three states, with two actions per output
-- state. Each exported bellman_state* function returns the larger of its
-- actions' immediate reward plus discounted continuation value. The helpers
-- fmax, fmax3, and fabs are stable exported scalar functions used by the
-- checked Bellman goals; their if/then/else bodies make the selected maximum
-- and absolute value explicit.
--
-- The properties call these exports directly. Monotonicity and boundedness
-- are checked at output state 0; upper and lower contraction bounds are
-- checked at every shipped output state. They concern one application, at a
-- fixed dimension, over the reals. Iteration limits, a fixed point, arbitrary
-- state counts, and f32 rounding are outside those proofs; see
-- docs/book/src/models/bellman.md.
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
