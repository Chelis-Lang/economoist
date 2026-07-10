module Economoist.Properties.Bellman
import Economoist.Bellman (bellman_state0, bellman_state1, bellman_state0_n3, bellman_state1_n3, bellman_state2_n3, fmax, fmax3, fabs)
-- Structural properties of one application of the Bellman optimality operator T,
-- proven at the SMT tier over the reals at the two shipped dimensions, 2 states x
-- 2 actions and 3 states x 2 actions. These are single-application facts: none of
-- them asserts value-iteration convergence or the existence of the fixed point,
-- and each is a fixed-dimension instance (n=2 or n=3 at m=2), not the general-n
-- theorem. See docs/models/bellman.md.
--
-- Each goal CALLS the exported bellman_state* operator directly (monotonicity and
-- the sup-norm bound call it once; the per-state contraction subtracts two calls
-- at shifted continuation values). Comparing or subtracting two calls of the same
-- if/then/else-bodied operator lowered soundly at chelis 0.10.0 (chelis#426
-- fixed; re-verified at 0.14.0 by cnote.dischargeability p04, and the regression
-- control pair bellman_call_collapse_wrong/_control in demos/businesswrong.ch
-- guards the fix), so the goals reference the shipped operator rather than
-- inlining its arithmetic. The exported defs are pinned numerically in
-- tests/bellman.ch.
-- HELD OUT (see docs/models/bellman.md): value-iteration convergence
--   v_{k+1} = T v_k -> v*, existence and uniqueness of the fixed point (the
--   Banach argument), which need induction; the general all-n-state, all-m-
--   action theorem (the greens cover the two fixed instances n=2 and n=3 at
--   m=2, not the all-n,m result); and any f32 float claim (the green is real
--   arithmetic).
-- Monotonicity (n=2). If the continuation value function v is dominated entrywise
-- by w (v0 <= w0 and v1 <= w1), then one Bellman step on v is at most one Bellman
-- step on w. Two calls of (Tv)_0 at v and at w.
@property bellman_monotone forall(v0: f32, v1: f32, w0: f32, w1: f32, r0: f32, p00: f32, p01: f32, r1: f32, p10: f32, p11: f32, g: f32) where (v0 <= w0), (v1 <= w1), (p00 >= 0.0), (p01 >= 0.0), (p10 >= 0.0), (p11 >= 0.0), ((p00 + p01) == 1.0), ((p10 + p11) == 1.0), (g > 0.0), (g < 1.0):
  (bellman_state0(v0, v1, r0, p00, p01, r1, p10, p11, g) <= bellman_state0(w0, w1, r0, p00, p01, r1, p10, p11, g))
-- Sup-norm bound (n=2). With each value entry in [-b, b] and each reward in
-- [-rmax, rmax], one Bellman step lands in [-(rmax + g * b), rmax + g * b]. The
-- bound is two-sided and proven as a single conjunction over one call of (Tv)_0.
@property bellman_bounded forall(v0: f32, v1: f32, r0: f32, p00: f32, p01: f32, r1: f32, p10: f32, p11: f32, g: f32, b: f32, rmax: f32) where (v0 <= b), (v0 >= (0.0 - b)), (v1 <= b), (v1 >= (0.0 - b)), (r0 <= rmax), (r0 >= (0.0 - rmax)), (r1 <= rmax), (r1 >= (0.0 - rmax)), (b >= 0.0), (rmax >= 0.0), (p00 >= 0.0), (p01 >= 0.0), (p10 >= 0.0), (p11 >= 0.0), ((p00 + p01) == 1.0), ((p10 + p11) == 1.0), (g > 0.0), (g < 1.0):
  ((bellman_state0(v0, v1, r0, p00, p01, r1, p10, p11, g) <= (rmax + (g * b))) && (bellman_state0(v0, v1, r0, p00, p01, r1, p10, p11, g) >= (0.0 - (rmax + (g * b)))))
-- Per-output-state contraction (n=2). The full sup-norm contraction
-- ||Tv - Tw||_inf <= g * ||v - w||_inf requires, for EVERY output state s,
-- |(Tv)_s - (Tw)_s| <= g * sup_j|v_j - w_j|. That per-component fact is proven
-- here at each output state, upper and lower side; the full sup-norm contraction
-- is the max of these per-component facts (see docs/models/bellman.md), not a
-- separate green. Each component is a premise of the Banach fixed-point argument,
-- not its conclusion.
-- Output state 0, upper side. (Tv)_0 - (Tw)_0 is at most g times the sup-norm
-- distance between v and w, using output-state-0's rewards r* and rows p*.
@property bellman_contraction_state0 forall(v0: f32, v1: f32, w0: f32, w1: f32, r0: f32, p00: f32, p01: f32, r1: f32, p10: f32, p11: f32, g: f32) where (p00 >= 0.0), (p01 >= 0.0), (p10 >= 0.0), (p11 >= 0.0), ((p00 + p01) == 1.0), ((p10 + p11) == 1.0), (g > 0.0), (g < 1.0):
  ((bellman_state0(v0, v1, r0, p00, p01, r1, p10, p11, g) - bellman_state0(w0, w1, r0, p00, p01, r1, p10, p11, g)) <= (g * fmax(fabs((v0 - w0)), fabs((v1 - w1)))))
-- Output state 0, lower side. The symmetric lower bound on the same difference.
@property bellman_contraction_state0_lower forall(v0: f32, v1: f32, w0: f32, w1: f32, r0: f32, p00: f32, p01: f32, r1: f32, p10: f32, p11: f32, g: f32) where (p00 >= 0.0), (p01 >= 0.0), (p10 >= 0.0), (p11 >= 0.0), ((p00 + p01) == 1.0), ((p10 + p11) == 1.0), (g > 0.0), (g < 1.0):
  ((bellman_state0(v0, v1, r0, p00, p01, r1, p10, p11, g) - bellman_state0(w0, w1, r0, p00, p01, r1, p10, p11, g)) >= (0.0 - (g * fmax(fabs((v0 - w0)), fabs((v1 - w1))))))
-- Output state 1, upper side. (Tv)_1 - (Tw)_1 is at most g times the same
-- sup-norm distance, using output-state-1's rewards rr* and rows q*.
@property bellman_contraction_state1 forall(v0: f32, v1: f32, w0: f32, w1: f32, rr0: f32, q00: f32, q01: f32, rr1: f32, q10: f32, q11: f32, g: f32) where (q00 >= 0.0), (q01 >= 0.0), (q10 >= 0.0), (q11 >= 0.0), ((q00 + q01) == 1.0), ((q10 + q11) == 1.0), (g > 0.0), (g < 1.0):
  ((bellman_state1(v0, v1, rr0, q00, q01, rr1, q10, q11, g) - bellman_state1(w0, w1, rr0, q00, q01, rr1, q10, q11, g)) <= (g * fmax(fabs((v0 - w0)), fabs((v1 - w1)))))
-- Output state 1, lower side. The symmetric lower bound on the same difference.
@property bellman_contraction_state1_lower forall(v0: f32, v1: f32, w0: f32, w1: f32, rr0: f32, q00: f32, q01: f32, rr1: f32, q10: f32, q11: f32, g: f32) where (q00 >= 0.0), (q01 >= 0.0), (q10 >= 0.0), (q11 >= 0.0), ((q00 + q01) == 1.0), ((q10 + q11) == 1.0), (g > 0.0), (g < 1.0):
  ((bellman_state1(v0, v1, rr0, q00, q01, rr1, q10, q11, g) - bellman_state1(w0, w1, rr0, q00, q01, rr1, q10, q11, g)) >= (0.0 - (g * fmax(fabs((v0 - w0)), fabs((v1 - w1))))))
-- Non-vacuity witnesses. Each asserts false under the same guards as the property
-- above and must be refuted at the SMT tier: cvc5 finds a guard-satisfying model,
-- proving the guards are jointly satisfiable and the green above is not vacuous.
@property bellman_monotone_guards_satisfiable forall(v0: f32, v1: f32, w0: f32, w1: f32, r0: f32, p00: f32, p01: f32, r1: f32, p10: f32, p11: f32, g: f32) where (v0 <= w0), (v1 <= w1), (p00 >= 0.0), (p01 >= 0.0), (p10 >= 0.0), (p11 >= 0.0), ((p00 + p01) == 1.0), ((p10 + p11) == 1.0), (g > 0.0), (g < 1.0):
  false
@property bellman_bounded_guards_satisfiable forall(v0: f32, v1: f32, r0: f32, p00: f32, p01: f32, r1: f32, p10: f32, p11: f32, g: f32, b: f32, rmax: f32) where (v0 <= b), (v0 >= (0.0 - b)), (v1 <= b), (v1 >= (0.0 - b)), (r0 <= rmax), (r0 >= (0.0 - rmax)), (r1 <= rmax), (r1 >= (0.0 - rmax)), (b >= 0.0), (rmax >= 0.0), (p00 >= 0.0), (p01 >= 0.0), (p10 >= 0.0), (p11 >= 0.0), ((p00 + p01) == 1.0), ((p10 + p11) == 1.0), (g > 0.0), (g < 1.0):
  false
@property bellman_contraction_state0_guards_satisfiable forall(v0: f32, v1: f32, w0: f32, w1: f32, r0: f32, p00: f32, p01: f32, r1: f32, p10: f32, p11: f32, g: f32) where (p00 >= 0.0), (p01 >= 0.0), (p10 >= 0.0), (p11 >= 0.0), ((p00 + p01) == 1.0), ((p10 + p11) == 1.0), (g > 0.0), (g < 1.0):
  false
@property bellman_contraction_state0_lower_guards_satisfiable forall(v0: f32, v1: f32, w0: f32, w1: f32, r0: f32, p00: f32, p01: f32, r1: f32, p10: f32, p11: f32, g: f32) where (p00 >= 0.0), (p01 >= 0.0), (p10 >= 0.0), (p11 >= 0.0), ((p00 + p01) == 1.0), ((p10 + p11) == 1.0), (g > 0.0), (g < 1.0):
  false
@property bellman_contraction_state1_guards_satisfiable forall(v0: f32, v1: f32, w0: f32, w1: f32, rr0: f32, q00: f32, q01: f32, rr1: f32, q10: f32, q11: f32, g: f32) where (q00 >= 0.0), (q01 >= 0.0), (q10 >= 0.0), (q11 >= 0.0), ((q00 + q01) == 1.0), ((q10 + q11) == 1.0), (g > 0.0), (g < 1.0):
  false
@property bellman_contraction_state1_lower_guards_satisfiable forall(v0: f32, v1: f32, w0: f32, w1: f32, rr0: f32, q00: f32, q01: f32, rr1: f32, q10: f32, q11: f32, g: f32) where (q00 >= 0.0), (q01 >= 0.0), (q10 >= 0.0), (q11 >= 0.0), ((q00 + q01) == 1.0), ((q10 + q11) == 1.0), (g > 0.0), (g < 1.0):
  false
-- Three-state instance (3 states x 2 actions). Monotonicity, the sup-norm bound,
-- and the per-output-state contraction are proven against the exported
-- bellman_state*_n3 operators. Each is still a single application of T at a fixed
-- dimension, here n=3 at m=2, not the general-n theorem and not convergence.
-- The n=3 per-component contraction uses the fmax3 ternary sup on the right
-- (chelis#425 candidate-fixed: the nested-max goal site lowers at 0.14.0, verified
-- by cnote.dischargeability p15) and the two-call operator subtraction on the left
-- (chelis#426 fixed): both surfaces now discharge, so the n=3 contraction ships
-- green rather than held out.
-- Monotonicity (n=3). If v is dominated entrywise by w over all three states,
-- one Bellman step on v is at most one Bellman step on w.
@property bellman3_monotone forall(v0: f32, v1: f32, v2: f32, w0: f32, w1: f32, w2: f32, r0: f32, p00: f32, p01: f32, p02: f32, r1: f32, p10: f32, p11: f32, p12: f32, g: f32) where (v0 <= w0), (v1 <= w1), (v2 <= w2), (p00 >= 0.0), (p01 >= 0.0), (p02 >= 0.0), (p10 >= 0.0), (p11 >= 0.0), (p12 >= 0.0), (((p00 + p01) + p02) == 1.0), (((p10 + p11) + p12) == 1.0), (g > 0.0), (g < 1.0):
  (bellman_state0_n3(v0, v1, v2, r0, p00, p01, p02, r1, p10, p11, p12, g) <= bellman_state0_n3(w0, w1, w2, r0, p00, p01, p02, r1, p10, p11, p12, g))
-- Sup-norm bound (n=3). With each of three value entries in [-b, b] and each
-- reward in [-rmax, rmax], one Bellman step lands in [-(rmax + g * b),
-- rmax + g * b]. Two sided, proven as a single conjunction over one call.
@property bellman3_bounded forall(v0: f32, v1: f32, v2: f32, r0: f32, p00: f32, p01: f32, p02: f32, r1: f32, p10: f32, p11: f32, p12: f32, g: f32, b: f32, rmax: f32) where (v0 <= b), (v0 >= (0.0 - b)), (v1 <= b), (v1 >= (0.0 - b)), (v2 <= b), (v2 >= (0.0 - b)), (r0 <= rmax), (r0 >= (0.0 - rmax)), (r1 <= rmax), (r1 >= (0.0 - rmax)), (b >= 0.0), (rmax >= 0.0), (p00 >= 0.0), (p01 >= 0.0), (p02 >= 0.0), (p10 >= 0.0), (p11 >= 0.0), (p12 >= 0.0), (((p00 + p01) + p02) == 1.0), (((p10 + p11) + p12) == 1.0), (g > 0.0), (g < 1.0):
  ((bellman_state0_n3(v0, v1, v2, r0, p00, p01, p02, r1, p10, p11, p12, g) <= (rmax + (g * b))) && (bellman_state0_n3(v0, v1, v2, r0, p00, p01, p02, r1, p10, p11, p12, g) >= (0.0 - (rmax + (g * b)))))
-- Per-output-state contraction (n=3), output state 0, upper side. (Tv)_0 - (Tw)_0
-- is at most g times the three-coordinate sup-norm distance, taken with fmax3.
@property bellman_contraction_state0_n3 forall(v0: f32, v1: f32, v2: f32, w0: f32, w1: f32, w2: f32, r0: f32, p00: f32, p01: f32, p02: f32, r1: f32, p10: f32, p11: f32, p12: f32, g: f32) where (p00 >= 0.0), (p01 >= 0.0), (p02 >= 0.0), (p10 >= 0.0), (p11 >= 0.0), (p12 >= 0.0), (((p00 + p01) + p02) == 1.0), (((p10 + p11) + p12) == 1.0), (g > 0.0), (g < 1.0):
  ((bellman_state0_n3(v0, v1, v2, r0, p00, p01, p02, r1, p10, p11, p12, g) - bellman_state0_n3(w0, w1, w2, r0, p00, p01, p02, r1, p10, p11, p12, g)) <= (g * fmax3(fabs((v0 - w0)), fabs((v1 - w1)), fabs((v2 - w2)))))
-- Output state 0, lower side (n=3).
@property bellman_contraction_state0_n3_lower forall(v0: f32, v1: f32, v2: f32, w0: f32, w1: f32, w2: f32, r0: f32, p00: f32, p01: f32, p02: f32, r1: f32, p10: f32, p11: f32, p12: f32, g: f32) where (p00 >= 0.0), (p01 >= 0.0), (p02 >= 0.0), (p10 >= 0.0), (p11 >= 0.0), (p12 >= 0.0), (((p00 + p01) + p02) == 1.0), (((p10 + p11) + p12) == 1.0), (g > 0.0), (g < 1.0):
  ((bellman_state0_n3(v0, v1, v2, r0, p00, p01, p02, r1, p10, p11, p12, g) - bellman_state0_n3(w0, w1, w2, r0, p00, p01, p02, r1, p10, p11, p12, g)) >= (0.0 - (g * fmax3(fabs((v0 - w0)), fabs((v1 - w1)), fabs((v2 - w2))))))
-- Non-vacuity witnesses (n=3).
@property bellman3_monotone_guards_satisfiable forall(v0: f32, v1: f32, v2: f32, w0: f32, w1: f32, w2: f32, r0: f32, p00: f32, p01: f32, p02: f32, r1: f32, p10: f32, p11: f32, p12: f32, g: f32) where (v0 <= w0), (v1 <= w1), (v2 <= w2), (p00 >= 0.0), (p01 >= 0.0), (p02 >= 0.0), (p10 >= 0.0), (p11 >= 0.0), (p12 >= 0.0), (((p00 + p01) + p02) == 1.0), (((p10 + p11) + p12) == 1.0), (g > 0.0), (g < 1.0):
  false
@property bellman3_bounded_guards_satisfiable forall(v0: f32, v1: f32, v2: f32, r0: f32, p00: f32, p01: f32, p02: f32, r1: f32, p10: f32, p11: f32, p12: f32, g: f32, b: f32, rmax: f32) where (v0 <= b), (v0 >= (0.0 - b)), (v1 <= b), (v1 >= (0.0 - b)), (v2 <= b), (v2 >= (0.0 - b)), (r0 <= rmax), (r0 >= (0.0 - rmax)), (r1 <= rmax), (r1 >= (0.0 - rmax)), (b >= 0.0), (rmax >= 0.0), (p00 >= 0.0), (p01 >= 0.0), (p02 >= 0.0), (p10 >= 0.0), (p11 >= 0.0), (p12 >= 0.0), (((p00 + p01) + p02) == 1.0), (((p10 + p11) + p12) == 1.0), (g > 0.0), (g < 1.0):
  false
@property bellman_contraction_state0_n3_guards_satisfiable forall(v0: f32, v1: f32, v2: f32, w0: f32, w1: f32, w2: f32, r0: f32, p00: f32, p01: f32, p02: f32, r1: f32, p10: f32, p11: f32, p12: f32, g: f32) where (p00 >= 0.0), (p01 >= 0.0), (p02 >= 0.0), (p10 >= 0.0), (p11 >= 0.0), (p12 >= 0.0), (((p00 + p01) + p02) == 1.0), (((p10 + p11) + p12) == 1.0), (g > 0.0), (g < 1.0):
  false
@property bellman_contraction_state0_n3_lower_guards_satisfiable forall(v0: f32, v1: f32, v2: f32, w0: f32, w1: f32, w2: f32, r0: f32, p00: f32, p01: f32, p02: f32, r1: f32, p10: f32, p11: f32, p12: f32, g: f32) where (p00 >= 0.0), (p01 >= 0.0), (p02 >= 0.0), (p10 >= 0.0), (p11 >= 0.0), (p12 >= 0.0), (((p00 + p01) + p02) == 1.0), (((p10 + p11) + p12) == 1.0), (g > 0.0), (g < 1.0):
  false
-- Output state 1, upper side (n=3): output-state-1's rewards rr* and rows q*.
@property bellman_contraction_state1_n3 forall(v0: f32, v1: f32, v2: f32, w0: f32, w1: f32, w2: f32, rr0: f32, q00: f32, q01: f32, q02: f32, rr1: f32, q10: f32, q11: f32, q12: f32, g: f32) where (q00 >= 0.0), (q01 >= 0.0), (q02 >= 0.0), (q10 >= 0.0), (q11 >= 0.0), (q12 >= 0.0), (((q00 + q01) + q02) == 1.0), (((q10 + q11) + q12) == 1.0), (g > 0.0), (g < 1.0):
  ((bellman_state1_n3(v0, v1, v2, rr0, q00, q01, q02, rr1, q10, q11, q12, g) - bellman_state1_n3(w0, w1, w2, rr0, q00, q01, q02, rr1, q10, q11, q12, g)) <= (g * fmax3(fabs((v0 - w0)), fabs((v1 - w1)), fabs((v2 - w2)))))
-- Output state 1, lower side (n=3).
@property bellman_contraction_state1_n3_lower forall(v0: f32, v1: f32, v2: f32, w0: f32, w1: f32, w2: f32, rr0: f32, q00: f32, q01: f32, q02: f32, rr1: f32, q10: f32, q11: f32, q12: f32, g: f32) where (q00 >= 0.0), (q01 >= 0.0), (q02 >= 0.0), (q10 >= 0.0), (q11 >= 0.0), (q12 >= 0.0), (((q00 + q01) + q02) == 1.0), (((q10 + q11) + q12) == 1.0), (g > 0.0), (g < 1.0):
  ((bellman_state1_n3(v0, v1, v2, rr0, q00, q01, q02, rr1, q10, q11, q12, g) - bellman_state1_n3(w0, w1, w2, rr0, q00, q01, q02, rr1, q10, q11, q12, g)) >= (0.0 - (g * fmax3(fabs((v0 - w0)), fabs((v1 - w1)), fabs((v2 - w2))))))
-- Output state 2, upper side (n=3): output-state-2's rewards rs* and rows s*.
@property bellman_contraction_state2_n3 forall(v0: f32, v1: f32, v2: f32, w0: f32, w1: f32, w2: f32, rs0: f32, s00: f32, s01: f32, s02: f32, rs1: f32, s10: f32, s11: f32, s12: f32, g: f32) where (s00 >= 0.0), (s01 >= 0.0), (s02 >= 0.0), (s10 >= 0.0), (s11 >= 0.0), (s12 >= 0.0), (((s00 + s01) + s02) == 1.0), (((s10 + s11) + s12) == 1.0), (g > 0.0), (g < 1.0):
  ((bellman_state2_n3(v0, v1, v2, rs0, s00, s01, s02, rs1, s10, s11, s12, g) - bellman_state2_n3(w0, w1, w2, rs0, s00, s01, s02, rs1, s10, s11, s12, g)) <= (g * fmax3(fabs((v0 - w0)), fabs((v1 - w1)), fabs((v2 - w2)))))
-- Output state 2, lower side (n=3).
@property bellman_contraction_state2_n3_lower forall(v0: f32, v1: f32, v2: f32, w0: f32, w1: f32, w2: f32, rs0: f32, s00: f32, s01: f32, s02: f32, rs1: f32, s10: f32, s11: f32, s12: f32, g: f32) where (s00 >= 0.0), (s01 >= 0.0), (s02 >= 0.0), (s10 >= 0.0), (s11 >= 0.0), (s12 >= 0.0), (((s00 + s01) + s02) == 1.0), (((s10 + s11) + s12) == 1.0), (g > 0.0), (g < 1.0):
  ((bellman_state2_n3(v0, v1, v2, rs0, s00, s01, s02, rs1, s10, s11, s12, g) - bellman_state2_n3(w0, w1, w2, rs0, s00, s01, s02, rs1, s10, s11, s12, g)) >= (0.0 - (g * fmax3(fabs((v0 - w0)), fabs((v1 - w1)), fabs((v2 - w2))))))
@property bellman_contraction_state1_n3_guards_satisfiable forall(v0: f32, v1: f32, v2: f32, w0: f32, w1: f32, w2: f32, rr0: f32, q00: f32, q01: f32, q02: f32, rr1: f32, q10: f32, q11: f32, q12: f32, g: f32) where (q00 >= 0.0), (q01 >= 0.0), (q02 >= 0.0), (q10 >= 0.0), (q11 >= 0.0), (q12 >= 0.0), (((q00 + q01) + q02) == 1.0), (((q10 + q11) + q12) == 1.0), (g > 0.0), (g < 1.0):
  false
@property bellman_contraction_state1_n3_lower_guards_satisfiable forall(v0: f32, v1: f32, v2: f32, w0: f32, w1: f32, w2: f32, rr0: f32, q00: f32, q01: f32, q02: f32, rr1: f32, q10: f32, q11: f32, q12: f32, g: f32) where (q00 >= 0.0), (q01 >= 0.0), (q02 >= 0.0), (q10 >= 0.0), (q11 >= 0.0), (q12 >= 0.0), (((q00 + q01) + q02) == 1.0), (((q10 + q11) + q12) == 1.0), (g > 0.0), (g < 1.0):
  false
@property bellman_contraction_state2_n3_guards_satisfiable forall(v0: f32, v1: f32, v2: f32, w0: f32, w1: f32, w2: f32, rs0: f32, s00: f32, s01: f32, s02: f32, rs1: f32, s10: f32, s11: f32, s12: f32, g: f32) where (s00 >= 0.0), (s01 >= 0.0), (s02 >= 0.0), (s10 >= 0.0), (s11 >= 0.0), (s12 >= 0.0), (((s00 + s01) + s02) == 1.0), (((s10 + s11) + s12) == 1.0), (g > 0.0), (g < 1.0):
  false
@property bellman_contraction_state2_n3_lower_guards_satisfiable forall(v0: f32, v1: f32, v2: f32, w0: f32, w1: f32, w2: f32, rs0: f32, s00: f32, s01: f32, s02: f32, rs1: f32, s10: f32, s11: f32, s12: f32, g: f32) where (s00 >= 0.0), (s01 >= 0.0), (s02 >= 0.0), (s10 >= 0.0), (s11 >= 0.0), (s12 >= 0.0), (((s00 + s01) + s02) == 1.0), (((s10 + s11) + s12) == 1.0), (g > 0.0), (g < 1.0):
  false
