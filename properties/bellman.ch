module Economoist.Properties.Bellman
import Economoist.Bellman (fmax, fabs)
-- Structural properties of one application of the Bellman optimality operator T,
-- proven at the SMT tier over the reals at the two shipped dimensions, 2 states x
-- 2 actions and 3 states x 2 actions. These are single-application facts: none of
-- them asserts value-iteration convergence or the existence of the fixed point,
-- and each is a fixed-dimension instance (n=2 or n=3 at m=2), not the general-n
-- theorem. See docs/models/bellman.md.
--
-- Each goal INLINES the operator arithmetic (the fmax(...) of the two actions)
-- rather than calling bellman_state0 / bellman_state1 / ..., because in chelis
-- 0.8.0 a goal that subtracts or compares two calls of the same
-- if/then/else-bodied def (bellman_state0(v...) - bellman_state0(w...)) collapses
-- the pair to a constant and would mask a false bound, false-proving it at the
-- SMT tier (chelis#426). The inlined arithmetic is term by term the body of the
-- matching exported bellman_state* def, which ships and is pinned numerically in
-- tests/bellman.ch.
-- Monotonicity (n=2). If the continuation value function v is dominated entrywise
-- by w (v0 <= w0 and v1 <= w1), then one Bellman step on v is at most one Bellman
-- step on w. The transition rows are guarded row-stochastic and the discount is a
-- strict contraction factor in (0, 1). The body is the (Tv)_0 arithmetic
-- (bellman_state0's body) inlined on each side.
@property bellman_monotone forall(v0: f32, v1: f32, w0: f32, w1: f32, r0: f32, p00: f32, p01: f32, r1: f32, p10: f32, p11: f32, g: f32) where (v0 <= w0), (v1 <= w1), (p00 >= 0.0), (p01 >= 0.0), (p10 >= 0.0), (p11 >= 0.0), ((p00 + p01) == 1.0), ((p10 + p11) == 1.0), (g > 0.0), (g < 1.0):
  (fmax((r0 + (g * ((p00 * v0) + (p01 * v1)))), (r1 + (g * ((p10 * v0) + (p11 * v1))))) <= fmax((r0 + (g * ((p00 * w0) + (p01 * w1)))), (r1 + (g * ((p10 * w0) + (p11 * w1))))))
-- Sup-norm bound (n=2). With each value entry in [-b, b] and each reward in
-- [-rmax, rmax], one Bellman step lands in [-(rmax + g * b), rmax + g * b]. The
-- bound is two-sided and proven as a single conjunction over the inlined (Tv)_0.
@property bellman_bounded forall(v0: f32, v1: f32, r0: f32, p00: f32, p01: f32, r1: f32, p10: f32, p11: f32, g: f32, b: f32, rmax: f32) where (v0 <= b), (v0 >= (0.0 - b)), (v1 <= b), (v1 >= (0.0 - b)), (r0 <= rmax), (r0 >= (0.0 - rmax)), (r1 <= rmax), (r1 >= (0.0 - rmax)), (b >= 0.0), (rmax >= 0.0), (p00 >= 0.0), (p01 >= 0.0), (p10 >= 0.0), (p11 >= 0.0), ((p00 + p01) == 1.0), ((p10 + p11) == 1.0), (g > 0.0), (g < 1.0):
  ((fmax((r0 + (g * ((p00 * v0) + (p01 * v1)))), (r1 + (g * ((p10 * v0) + (p11 * v1))))) <= (rmax + (g * b))) && (fmax((r0 + (g * ((p00 * v0) + (p01 * v1)))), (r1 + (g * ((p10 * v0) + (p11 * v1))))) >= (0.0 - (rmax + (g * b)))))
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
  ((fmax((r0 + (g * ((p00 * v0) + (p01 * v1)))), (r1 + (g * ((p10 * v0) + (p11 * v1))))) - fmax((r0 + (g * ((p00 * w0) + (p01 * w1)))), (r1 + (g * ((p10 * w0) + (p11 * w1)))))) <= (g * fmax(fabs((v0 - w0)), fabs((v1 - w1)))))
-- Output state 0, lower side. The symmetric lower bound on the same difference.
@property bellman_contraction_state0_lower forall(v0: f32, v1: f32, w0: f32, w1: f32, r0: f32, p00: f32, p01: f32, r1: f32, p10: f32, p11: f32, g: f32) where (p00 >= 0.0), (p01 >= 0.0), (p10 >= 0.0), (p11 >= 0.0), ((p00 + p01) == 1.0), ((p10 + p11) == 1.0), (g > 0.0), (g < 1.0):
  ((fmax((r0 + (g * ((p00 * v0) + (p01 * v1)))), (r1 + (g * ((p10 * v0) + (p11 * v1))))) - fmax((r0 + (g * ((p00 * w0) + (p01 * w1)))), (r1 + (g * ((p10 * w0) + (p11 * w1)))))) >= (0.0 - (g * fmax(fabs((v0 - w0)), fabs((v1 - w1))))))
-- Output state 1, upper side. (Tv)_1 - (Tw)_1 is at most g times the same
-- sup-norm distance, using output-state-1's rewards rr* and rows q*.
@property bellman_contraction_state1 forall(v0: f32, v1: f32, w0: f32, w1: f32, rr0: f32, q00: f32, q01: f32, rr1: f32, q10: f32, q11: f32, g: f32) where (q00 >= 0.0), (q01 >= 0.0), (q10 >= 0.0), (q11 >= 0.0), ((q00 + q01) == 1.0), ((q10 + q11) == 1.0), (g > 0.0), (g < 1.0):
  ((fmax((rr0 + (g * ((q00 * v0) + (q01 * v1)))), (rr1 + (g * ((q10 * v0) + (q11 * v1))))) - fmax((rr0 + (g * ((q00 * w0) + (q01 * w1)))), (rr1 + (g * ((q10 * w0) + (q11 * w1)))))) <= (g * fmax(fabs((v0 - w0)), fabs((v1 - w1)))))
-- Output state 1, lower side. The symmetric lower bound on the same difference.
@property bellman_contraction_state1_lower forall(v0: f32, v1: f32, w0: f32, w1: f32, rr0: f32, q00: f32, q01: f32, rr1: f32, q10: f32, q11: f32, g: f32) where (q00 >= 0.0), (q01 >= 0.0), (q10 >= 0.0), (q11 >= 0.0), ((q00 + q01) == 1.0), ((q10 + q11) == 1.0), (g > 0.0), (g < 1.0):
  ((fmax((rr0 + (g * ((q00 * v0) + (q01 * v1)))), (rr1 + (g * ((q10 * v0) + (q11 * v1))))) - fmax((rr0 + (g * ((q00 * w0) + (q01 * w1)))), (rr1 + (g * ((q10 * w0) + (q11 * w1)))))) >= (0.0 - (g * fmax(fabs((v0 - w0)), fabs((v1 - w1))))))
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
-- Three-state instance (3 states x 2 actions). Monotonicity and the sup-norm
-- bound are proven against the inlined (Tv)_0 arithmetic with a third state.
-- Each is still a single application of T at a fixed dimension, here n=3 at m=2,
-- not the general-n theorem and not convergence. The n=3 per-component
-- contraction is HELD OUT: its goal (the per-state difference bounded by
-- g * fmax3 over the three coordinate distances) does not lower to the SMT tier
-- at this dimension, so no green is claimed for it (see docs/models/bellman.md).
-- Monotonicity (n=3). If v is dominated entrywise by w over all three states,
-- one Bellman step on v is at most one Bellman step on w, given row stochastic
-- transitions over three states and a discount g in (0, 1).
@property bellman3_monotone forall(v0: f32, v1: f32, v2: f32, w0: f32, w1: f32, w2: f32, r0: f32, p00: f32, p01: f32, p02: f32, r1: f32, p10: f32, p11: f32, p12: f32, g: f32) where (v0 <= w0), (v1 <= w1), (v2 <= w2), (p00 >= 0.0), (p01 >= 0.0), (p02 >= 0.0), (p10 >= 0.0), (p11 >= 0.0), (p12 >= 0.0), (((p00 + p01) + p02) == 1.0), (((p10 + p11) + p12) == 1.0), (g > 0.0), (g < 1.0):
  (fmax((r0 + (g * (((p00 * v0) + (p01 * v1)) + (p02 * v2)))), (r1 + (g * (((p10 * v0) + (p11 * v1)) + (p12 * v2))))) <= fmax((r0 + (g * (((p00 * w0) + (p01 * w1)) + (p02 * w2)))), (r1 + (g * (((p10 * w0) + (p11 * w1)) + (p12 * w2))))))
-- Sup-norm bound (n=3). With each of three value entries in [-b, b] and each
-- reward in [-rmax, rmax], one Bellman step lands in [-(rmax + g * b),
-- rmax + g * b]. Two sided, proven as a single conjunction over the inlined step.
@property bellman3_bounded forall(v0: f32, v1: f32, v2: f32, r0: f32, p00: f32, p01: f32, p02: f32, r1: f32, p10: f32, p11: f32, p12: f32, g: f32, b: f32, rmax: f32) where (v0 <= b), (v0 >= (0.0 - b)), (v1 <= b), (v1 >= (0.0 - b)), (v2 <= b), (v2 >= (0.0 - b)), (r0 <= rmax), (r0 >= (0.0 - rmax)), (r1 <= rmax), (r1 >= (0.0 - rmax)), (b >= 0.0), (rmax >= 0.0), (p00 >= 0.0), (p01 >= 0.0), (p02 >= 0.0), (p10 >= 0.0), (p11 >= 0.0), (p12 >= 0.0), (((p00 + p01) + p02) == 1.0), (((p10 + p11) + p12) == 1.0), (g > 0.0), (g < 1.0):
  ((fmax((r0 + (g * (((p00 * v0) + (p01 * v1)) + (p02 * v2)))), (r1 + (g * (((p10 * v0) + (p11 * v1)) + (p12 * v2))))) <= (rmax + (g * b))) && (fmax((r0 + (g * (((p00 * v0) + (p01 * v1)) + (p02 * v2)))), (r1 + (g * (((p10 * v0) + (p11 * v1)) + (p12 * v2))))) >= (0.0 - (rmax + (g * b)))))
-- Non-vacuity witnesses (n=3). Each asserts false under the same guards as the
-- n=3 property above and must be refuted at the SMT tier, proving the guards are
-- jointly satisfiable and the green is not vacuous.
@property bellman3_monotone_guards_satisfiable forall(v0: f32, v1: f32, v2: f32, w0: f32, w1: f32, w2: f32, r0: f32, p00: f32, p01: f32, p02: f32, r1: f32, p10: f32, p11: f32, p12: f32, g: f32) where (v0 <= w0), (v1 <= w1), (v2 <= w2), (p00 >= 0.0), (p01 >= 0.0), (p02 >= 0.0), (p10 >= 0.0), (p11 >= 0.0), (p12 >= 0.0), (((p00 + p01) + p02) == 1.0), (((p10 + p11) + p12) == 1.0), (g > 0.0), (g < 1.0):
  false
@property bellman3_bounded_guards_satisfiable forall(v0: f32, v1: f32, v2: f32, r0: f32, p00: f32, p01: f32, p02: f32, r1: f32, p10: f32, p11: f32, p12: f32, g: f32, b: f32, rmax: f32) where (v0 <= b), (v0 >= (0.0 - b)), (v1 <= b), (v1 >= (0.0 - b)), (v2 <= b), (v2 >= (0.0 - b)), (r0 <= rmax), (r0 >= (0.0 - rmax)), (r1 <= rmax), (r1 >= (0.0 - rmax)), (b >= 0.0), (rmax >= 0.0), (p00 >= 0.0), (p01 >= 0.0), (p02 >= 0.0), (p10 >= 0.0), (p11 >= 0.0), (p12 >= 0.0), (((p00 + p01) + p02) == 1.0), (((p10 + p11) + p12) == 1.0), (g > 0.0), (g < 1.0):
  false
