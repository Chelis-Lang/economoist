module Economoist.Properties.Bellman
import Economoist.Bellman (bellman_state0, bellman_state1, bellman_state0_n3, bellman_state1_n3, bellman_state2_n3, fmax, fmax3, fabs)
-- One Bellman update at two or three states with two actions. Every goal
-- calls an exported bellman_state* function. Monotonicity and boundedness
-- concern output state 0; both sides of the contraction bound are checked
-- at every shipped output state. The bounds imply a vector sup-norm bound
-- at each fixed size; they do not prove convergence, a fixed point, or a
-- result for arbitrary state and action counts.
-- SMT interprets these f32 expressions over the reals. The unguarded
-- bellman_call_collapse_wrong twin in demos/businesswrong.ch must refute,
-- checking that two calls of one ITE-bodied operator do not collapse.
-- Monotonicity (n=2). If the continuation value function v is dominated entrywise
-- by w (v0 <= w0 and v1 <= w1), then one Bellman step on v is at most one Bellman
-- step on w. Two calls of (Tv)_0 at v and at w.
@property bellman_monotone forall(v0: f32, v1: f32, w0: f32, w1: f32, r0: f32, p00: f32, p01: f32, r1: f32, p10: f32, p11: f32, g: f32) where v0 <= w0, v1 <= w1, p00 >= 0.0, p01 >= 0.0, p10 >= 0.0, p11 >= 0.0, (p00 + p01) == 1.0, (p10 + p11) == 1.0, g > 0.0, g < 1.0:
  (bellman_state0(v0, v1, r0, p00, p01, r1, p10, p11, g) <= bellman_state0(w0, w1, r0, p00, p01, r1, p10, p11, g))
-- Sup-norm bound (n=2). With each value entry in [-b, b] and each reward in
-- [-rmax, rmax], one Bellman step lands in [-(rmax + g * b), rmax + g * b]. The
-- bound is two-sided and proven as a single conjunction over one call of (Tv)_0.
@property bellman_bounded forall(v0: f32, v1: f32, r0: f32, p00: f32, p01: f32, r1: f32, p10: f32, p11: f32, g: f32, b: f32, rmax: f32) where v0 <= b, v0 >= (0.0 - b), v1 <= b, v1 >= (0.0 - b), r0 <= rmax, r0 >= (0.0 - rmax), r1 <= rmax, r1 >= (0.0 - rmax), b >= 0.0, rmax >= 0.0, p00 >= 0.0, p01 >= 0.0, p10 >= 0.0, p11 >= 0.0, (p00 + p01) == 1.0, (p10 + p11) == 1.0, g > 0.0, g < 1.0:
  ((bellman_state0(v0, v1, r0, p00, p01, r1, p10, p11, g) <= (rmax + (g * b))) && (bellman_state0(v0, v1, r0, p00, p01, r1, p10, p11, g) >= (0.0 - (rmax + (g * b)))))
-- Per-output-state contraction (n=2). The full sup-norm contraction
-- ||Tv - Tw||_inf <= g * ||v - w||_inf requires, for EVERY output state s,
-- |(Tv)_s - (Tw)_s| <= g * sup_j|v_j - w_j|. That per-component fact is proven
-- here at each output state, upper and lower side; the full sup-norm contraction
-- is the max of these per-component facts (see docs/book/src/models/bellman.md), not a
-- separate prover record. Each component is a premise of the Banach fixed-point argument,
-- not its conclusion.
-- Output state 0, upper side. (Tv)_0 - (Tw)_0 is at most g times the sup-norm
-- distance between v and w, using output-state-0's rewards r* and rows p*.
@property bellman_contraction_state0 forall(v0: f32, v1: f32, w0: f32, w1: f32, r0: f32, p00: f32, p01: f32, r1: f32, p10: f32, p11: f32, g: f32) where p00 >= 0.0, p01 >= 0.0, p10 >= 0.0, p11 >= 0.0, (p00 + p01) == 1.0, (p10 + p11) == 1.0, g > 0.0, g < 1.0:
  ((bellman_state0(v0, v1, r0, p00, p01, r1, p10, p11, g) - bellman_state0(w0, w1, r0, p00, p01, r1, p10, p11, g)) <= (g * fmax(fabs((v0 - w0)), fabs((v1 - w1)))))
-- Output state 0, lower side. The symmetric lower bound on the same difference.
@property bellman_contraction_state0_lower forall(v0: f32, v1: f32, w0: f32, w1: f32, r0: f32, p00: f32, p01: f32, r1: f32, p10: f32, p11: f32, g: f32) where p00 >= 0.0, p01 >= 0.0, p10 >= 0.0, p11 >= 0.0, (p00 + p01) == 1.0, (p10 + p11) == 1.0, g > 0.0, g < 1.0:
  ((bellman_state0(v0, v1, r0, p00, p01, r1, p10, p11, g) - bellman_state0(w0, w1, r0, p00, p01, r1, p10, p11, g)) >= (0.0 - (g * fmax(fabs((v0 - w0)), fabs((v1 - w1))))))
-- Output state 1, upper side. (Tv)_1 - (Tw)_1 is at most g times the same
-- sup-norm distance, using output-state-1's rewards rr* and rows q*.
@property bellman_contraction_state1 forall(v0: f32, v1: f32, w0: f32, w1: f32, rr0: f32, q00: f32, q01: f32, rr1: f32, q10: f32, q11: f32, g: f32) where q00 >= 0.0, q01 >= 0.0, q10 >= 0.0, q11 >= 0.0, (q00 + q01) == 1.0, (q10 + q11) == 1.0, g > 0.0, g < 1.0:
  ((bellman_state1(v0, v1, rr0, q00, q01, rr1, q10, q11, g) - bellman_state1(w0, w1, rr0, q00, q01, rr1, q10, q11, g)) <= (g * fmax(fabs((v0 - w0)), fabs((v1 - w1)))))
-- Output state 1, lower side. The symmetric lower bound on the same difference.
@property bellman_contraction_state1_lower forall(v0: f32, v1: f32, w0: f32, w1: f32, rr0: f32, q00: f32, q01: f32, rr1: f32, q10: f32, q11: f32, g: f32) where q00 >= 0.0, q01 >= 0.0, q10 >= 0.0, q11 >= 0.0, (q00 + q01) == 1.0, (q10 + q11) == 1.0, g > 0.0, g < 1.0:
  ((bellman_state1(v0, v1, rr0, q00, q01, rr1, q10, q11, g) - bellman_state1(w0, w1, rr0, q00, q01, rr1, q10, q11, g)) >= (0.0 - (g * fmax(fabs((v0 - w0)), fabs((v1 - w1))))))
-- Non-vacuity witnesses. Each asserts false under the same guards as the property
-- above and must be refuted by SMT: cvc5 finds a guard-satisfying model,
-- proving the guards are jointly satisfiable and the checked claim is not vacuous.
@property bellman_monotone_guards_satisfiable forall(v0: f32, v1: f32, w0: f32, w1: f32, r0: f32, p00: f32, p01: f32, r1: f32, p10: f32, p11: f32, g: f32) where v0 <= w0, v1 <= w1, p00 >= 0.0, p01 >= 0.0, p10 >= 0.0, p11 >= 0.0, (p00 + p01) == 1.0, (p10 + p11) == 1.0, g > 0.0, g < 1.0:
  false
@property bellman_bounded_guards_satisfiable forall(v0: f32, v1: f32, r0: f32, p00: f32, p01: f32, r1: f32, p10: f32, p11: f32, g: f32, b: f32, rmax: f32) where v0 <= b, v0 >= (0.0 - b), v1 <= b, v1 >= (0.0 - b), r0 <= rmax, r0 >= (0.0 - rmax), r1 <= rmax, r1 >= (0.0 - rmax), b >= 0.0, rmax >= 0.0, p00 >= 0.0, p01 >= 0.0, p10 >= 0.0, p11 >= 0.0, (p00 + p01) == 1.0, (p10 + p11) == 1.0, g > 0.0, g < 1.0:
  false
@property bellman_contraction_state0_guards_satisfiable forall(v0: f32, v1: f32, w0: f32, w1: f32, r0: f32, p00: f32, p01: f32, r1: f32, p10: f32, p11: f32, g: f32) where p00 >= 0.0, p01 >= 0.0, p10 >= 0.0, p11 >= 0.0, (p00 + p01) == 1.0, (p10 + p11) == 1.0, g > 0.0, g < 1.0:
  false
@property bellman_contraction_state0_lower_guards_satisfiable forall(v0: f32, v1: f32, w0: f32, w1: f32, r0: f32, p00: f32, p01: f32, r1: f32, p10: f32, p11: f32, g: f32) where p00 >= 0.0, p01 >= 0.0, p10 >= 0.0, p11 >= 0.0, (p00 + p01) == 1.0, (p10 + p11) == 1.0, g > 0.0, g < 1.0:
  false
@property bellman_contraction_state1_guards_satisfiable forall(v0: f32, v1: f32, w0: f32, w1: f32, rr0: f32, q00: f32, q01: f32, rr1: f32, q10: f32, q11: f32, g: f32) where q00 >= 0.0, q01 >= 0.0, q10 >= 0.0, q11 >= 0.0, (q00 + q01) == 1.0, (q10 + q11) == 1.0, g > 0.0, g < 1.0:
  false
@property bellman_contraction_state1_lower_guards_satisfiable forall(v0: f32, v1: f32, w0: f32, w1: f32, rr0: f32, q00: f32, q01: f32, rr1: f32, q10: f32, q11: f32, g: f32) where q00 >= 0.0, q01 >= 0.0, q10 >= 0.0, q11 >= 0.0, (q00 + q01) == 1.0, (q10 + q11) == 1.0, g > 0.0, g < 1.0:
  false
-- Three-state goals use the same one-step guards and call the exported
-- three-state operators. The contraction bounds use fmax3 for the largest
-- coordinate difference. Monotonicity and boundedness concern state 0.
-- Monotonicity (n=3). If v is dominated entrywise by w over all three states,
-- one Bellman step on v is at most one Bellman step on w.
@property bellman3_monotone forall(v0: f32, v1: f32, v2: f32, w0: f32, w1: f32, w2: f32, r0: f32, p00: f32, p01: f32, p02: f32, r1: f32, p10: f32, p11: f32, p12: f32, g: f32) where v0 <= w0, v1 <= w1, v2 <= w2, p00 >= 0.0, p01 >= 0.0, p02 >= 0.0, p10 >= 0.0, p11 >= 0.0, p12 >= 0.0, ((p00 + p01) + p02) == 1.0, ((p10 + p11) + p12) == 1.0, g > 0.0, g < 1.0:
  (bellman_state0_n3(v0, v1, v2, r0, p00, p01, p02, r1, p10, p11, p12, g) <= bellman_state0_n3(w0, w1, w2, r0, p00, p01, p02, r1, p10, p11, p12, g))
-- Sup-norm bound (n=3). With each of three value entries in [-b, b] and each
-- reward in [-rmax, rmax], one Bellman step lands in [-(rmax + g * b),
-- rmax + g * b]. Two sided, proven as a single conjunction over one call.
@property bellman3_bounded forall(v0: f32, v1: f32, v2: f32, r0: f32, p00: f32, p01: f32, p02: f32, r1: f32, p10: f32, p11: f32, p12: f32, g: f32, b: f32, rmax: f32) where v0 <= b, v0 >= (0.0 - b), v1 <= b, v1 >= (0.0 - b), v2 <= b, v2 >= (0.0 - b), r0 <= rmax, r0 >= (0.0 - rmax), r1 <= rmax, r1 >= (0.0 - rmax), b >= 0.0, rmax >= 0.0, p00 >= 0.0, p01 >= 0.0, p02 >= 0.0, p10 >= 0.0, p11 >= 0.0, p12 >= 0.0, ((p00 + p01) + p02) == 1.0, ((p10 + p11) + p12) == 1.0, g > 0.0, g < 1.0:
  ((bellman_state0_n3(v0, v1, v2, r0, p00, p01, p02, r1, p10, p11, p12, g) <= (rmax + (g * b))) && (bellman_state0_n3(v0, v1, v2, r0, p00, p01, p02, r1, p10, p11, p12, g) >= (0.0 - (rmax + (g * b)))))
-- Per-output-state contraction (n=3), output state 0, upper side. (Tv)_0 - (Tw)_0
-- is at most g times the three-coordinate sup-norm distance, taken with fmax3.
@property bellman_contraction_state0_n3 forall(v0: f32, v1: f32, v2: f32, w0: f32, w1: f32, w2: f32, r0: f32, p00: f32, p01: f32, p02: f32, r1: f32, p10: f32, p11: f32, p12: f32, g: f32) where p00 >= 0.0, p01 >= 0.0, p02 >= 0.0, p10 >= 0.0, p11 >= 0.0, p12 >= 0.0, ((p00 + p01) + p02) == 1.0, ((p10 + p11) + p12) == 1.0, g > 0.0, g < 1.0:
  ((bellman_state0_n3(v0, v1, v2, r0, p00, p01, p02, r1, p10, p11, p12, g) - bellman_state0_n3(w0, w1, w2, r0, p00, p01, p02, r1, p10, p11, p12, g)) <= (g * fmax3(fabs((v0 - w0)), fabs((v1 - w1)), fabs((v2 - w2)))))
-- Output state 0, lower side (n=3).
@property bellman_contraction_state0_n3_lower forall(v0: f32, v1: f32, v2: f32, w0: f32, w1: f32, w2: f32, r0: f32, p00: f32, p01: f32, p02: f32, r1: f32, p10: f32, p11: f32, p12: f32, g: f32) where p00 >= 0.0, p01 >= 0.0, p02 >= 0.0, p10 >= 0.0, p11 >= 0.0, p12 >= 0.0, ((p00 + p01) + p02) == 1.0, ((p10 + p11) + p12) == 1.0, g > 0.0, g < 1.0:
  ((bellman_state0_n3(v0, v1, v2, r0, p00, p01, p02, r1, p10, p11, p12, g) - bellman_state0_n3(w0, w1, w2, r0, p00, p01, p02, r1, p10, p11, p12, g)) >= (0.0 - (g * fmax3(fabs((v0 - w0)), fabs((v1 - w1)), fabs((v2 - w2))))))
-- Non-vacuity witnesses (n=3).
@property bellman3_monotone_guards_satisfiable forall(v0: f32, v1: f32, v2: f32, w0: f32, w1: f32, w2: f32, r0: f32, p00: f32, p01: f32, p02: f32, r1: f32, p10: f32, p11: f32, p12: f32, g: f32) where v0 <= w0, v1 <= w1, v2 <= w2, p00 >= 0.0, p01 >= 0.0, p02 >= 0.0, p10 >= 0.0, p11 >= 0.0, p12 >= 0.0, ((p00 + p01) + p02) == 1.0, ((p10 + p11) + p12) == 1.0, g > 0.0, g < 1.0:
  false
@property bellman3_bounded_guards_satisfiable forall(v0: f32, v1: f32, v2: f32, r0: f32, p00: f32, p01: f32, p02: f32, r1: f32, p10: f32, p11: f32, p12: f32, g: f32, b: f32, rmax: f32) where v0 <= b, v0 >= (0.0 - b), v1 <= b, v1 >= (0.0 - b), v2 <= b, v2 >= (0.0 - b), r0 <= rmax, r0 >= (0.0 - rmax), r1 <= rmax, r1 >= (0.0 - rmax), b >= 0.0, rmax >= 0.0, p00 >= 0.0, p01 >= 0.0, p02 >= 0.0, p10 >= 0.0, p11 >= 0.0, p12 >= 0.0, ((p00 + p01) + p02) == 1.0, ((p10 + p11) + p12) == 1.0, g > 0.0, g < 1.0:
  false
@property bellman_contraction_state0_n3_guards_satisfiable forall(v0: f32, v1: f32, v2: f32, w0: f32, w1: f32, w2: f32, r0: f32, p00: f32, p01: f32, p02: f32, r1: f32, p10: f32, p11: f32, p12: f32, g: f32) where p00 >= 0.0, p01 >= 0.0, p02 >= 0.0, p10 >= 0.0, p11 >= 0.0, p12 >= 0.0, ((p00 + p01) + p02) == 1.0, ((p10 + p11) + p12) == 1.0, g > 0.0, g < 1.0:
  false
@property bellman_contraction_state0_n3_lower_guards_satisfiable forall(v0: f32, v1: f32, v2: f32, w0: f32, w1: f32, w2: f32, r0: f32, p00: f32, p01: f32, p02: f32, r1: f32, p10: f32, p11: f32, p12: f32, g: f32) where p00 >= 0.0, p01 >= 0.0, p02 >= 0.0, p10 >= 0.0, p11 >= 0.0, p12 >= 0.0, ((p00 + p01) + p02) == 1.0, ((p10 + p11) + p12) == 1.0, g > 0.0, g < 1.0:
  false
-- Output state 1, upper side (n=3): output-state-1's rewards rr* and rows q*.
@property bellman_contraction_state1_n3 forall(v0: f32, v1: f32, v2: f32, w0: f32, w1: f32, w2: f32, rr0: f32, q00: f32, q01: f32, q02: f32, rr1: f32, q10: f32, q11: f32, q12: f32, g: f32) where q00 >= 0.0, q01 >= 0.0, q02 >= 0.0, q10 >= 0.0, q11 >= 0.0, q12 >= 0.0, ((q00 + q01) + q02) == 1.0, ((q10 + q11) + q12) == 1.0, g > 0.0, g < 1.0:
  ((bellman_state1_n3(v0, v1, v2, rr0, q00, q01, q02, rr1, q10, q11, q12, g) - bellman_state1_n3(w0, w1, w2, rr0, q00, q01, q02, rr1, q10, q11, q12, g)) <= (g * fmax3(fabs((v0 - w0)), fabs((v1 - w1)), fabs((v2 - w2)))))
-- Output state 1, lower side (n=3).
@property bellman_contraction_state1_n3_lower forall(v0: f32, v1: f32, v2: f32, w0: f32, w1: f32, w2: f32, rr0: f32, q00: f32, q01: f32, q02: f32, rr1: f32, q10: f32, q11: f32, q12: f32, g: f32) where q00 >= 0.0, q01 >= 0.0, q02 >= 0.0, q10 >= 0.0, q11 >= 0.0, q12 >= 0.0, ((q00 + q01) + q02) == 1.0, ((q10 + q11) + q12) == 1.0, g > 0.0, g < 1.0:
  ((bellman_state1_n3(v0, v1, v2, rr0, q00, q01, q02, rr1, q10, q11, q12, g) - bellman_state1_n3(w0, w1, w2, rr0, q00, q01, q02, rr1, q10, q11, q12, g)) >= (0.0 - (g * fmax3(fabs((v0 - w0)), fabs((v1 - w1)), fabs((v2 - w2))))))
-- Output state 2, upper side (n=3): output-state-2's rewards rs* and rows s*.
@property bellman_contraction_state2_n3 forall(v0: f32, v1: f32, v2: f32, w0: f32, w1: f32, w2: f32, rs0: f32, s00: f32, s01: f32, s02: f32, rs1: f32, s10: f32, s11: f32, s12: f32, g: f32) where s00 >= 0.0, s01 >= 0.0, s02 >= 0.0, s10 >= 0.0, s11 >= 0.0, s12 >= 0.0, ((s00 + s01) + s02) == 1.0, ((s10 + s11) + s12) == 1.0, g > 0.0, g < 1.0:
  ((bellman_state2_n3(v0, v1, v2, rs0, s00, s01, s02, rs1, s10, s11, s12, g) - bellman_state2_n3(w0, w1, w2, rs0, s00, s01, s02, rs1, s10, s11, s12, g)) <= (g * fmax3(fabs((v0 - w0)), fabs((v1 - w1)), fabs((v2 - w2)))))
-- Output state 2, lower side (n=3).
@property bellman_contraction_state2_n3_lower forall(v0: f32, v1: f32, v2: f32, w0: f32, w1: f32, w2: f32, rs0: f32, s00: f32, s01: f32, s02: f32, rs1: f32, s10: f32, s11: f32, s12: f32, g: f32) where s00 >= 0.0, s01 >= 0.0, s02 >= 0.0, s10 >= 0.0, s11 >= 0.0, s12 >= 0.0, ((s00 + s01) + s02) == 1.0, ((s10 + s11) + s12) == 1.0, g > 0.0, g < 1.0:
  ((bellman_state2_n3(v0, v1, v2, rs0, s00, s01, s02, rs1, s10, s11, s12, g) - bellman_state2_n3(w0, w1, w2, rs0, s00, s01, s02, rs1, s10, s11, s12, g)) >= (0.0 - (g * fmax3(fabs((v0 - w0)), fabs((v1 - w1)), fabs((v2 - w2))))))
@property bellman_contraction_state1_n3_guards_satisfiable forall(v0: f32, v1: f32, v2: f32, w0: f32, w1: f32, w2: f32, rr0: f32, q00: f32, q01: f32, q02: f32, rr1: f32, q10: f32, q11: f32, q12: f32, g: f32) where q00 >= 0.0, q01 >= 0.0, q02 >= 0.0, q10 >= 0.0, q11 >= 0.0, q12 >= 0.0, ((q00 + q01) + q02) == 1.0, ((q10 + q11) + q12) == 1.0, g > 0.0, g < 1.0:
  false
@property bellman_contraction_state1_n3_lower_guards_satisfiable forall(v0: f32, v1: f32, v2: f32, w0: f32, w1: f32, w2: f32, rr0: f32, q00: f32, q01: f32, q02: f32, rr1: f32, q10: f32, q11: f32, q12: f32, g: f32) where q00 >= 0.0, q01 >= 0.0, q02 >= 0.0, q10 >= 0.0, q11 >= 0.0, q12 >= 0.0, ((q00 + q01) + q02) == 1.0, ((q10 + q11) + q12) == 1.0, g > 0.0, g < 1.0:
  false
@property bellman_contraction_state2_n3_guards_satisfiable forall(v0: f32, v1: f32, v2: f32, w0: f32, w1: f32, w2: f32, rs0: f32, s00: f32, s01: f32, s02: f32, rs1: f32, s10: f32, s11: f32, s12: f32, g: f32) where s00 >= 0.0, s01 >= 0.0, s02 >= 0.0, s10 >= 0.0, s11 >= 0.0, s12 >= 0.0, ((s00 + s01) + s02) == 1.0, ((s10 + s11) + s12) == 1.0, g > 0.0, g < 1.0:
  false
@property bellman_contraction_state2_n3_lower_guards_satisfiable forall(v0: f32, v1: f32, v2: f32, w0: f32, w1: f32, w2: f32, rs0: f32, s00: f32, s01: f32, s02: f32, rs1: f32, s10: f32, s11: f32, s12: f32, g: f32) where s00 >= 0.0, s01 >= 0.0, s02 >= 0.0, s10 >= 0.0, s11 >= 0.0, s12 >= 0.0, ((s00 + s01) + s02) == 1.0, ((s10 + s11) + s12) == 1.0, g > 0.0, g < 1.0:
  false
