module Economoist.Properties.Bellman
import Economoist.Bellman (bellman_state0, fmax, fabs)
-- Structural properties of one application of the Bellman optimality operator T
-- at state 0, proven at the SMT tier over the reals against the exported
-- bellman_state0 operator. These are single-application facts: none of them
-- asserts value-iteration convergence or the existence of the fixed point, and
-- each is the fixed 2-state x 2-action instance, not the general-n theorem. See
-- docs/models/bellman.md.
-- Monotonicity. If the continuation value function v is dominated entrywise by
-- w (v0 <= w0 and v1 <= w1), then one Bellman step on v is at most one Bellman
-- step on w. The transition rows are guarded row-stochastic and the discount is
-- a strict contraction factor in (0, 1).
@property bellman_monotone forall(v0: f32, v1: f32, w0: f32, w1: f32, r0: f32, p00: f32, p01: f32, r1: f32, p10: f32, p11: f32, g: f32) where (v0 <= w0), (v1 <= w1), (p00 >= 0.0), (p01 >= 0.0), (p10 >= 0.0), (p11 >= 0.0), ((p00 + p01) == 1.0), ((p10 + p11) == 1.0), (g > 0.0), (g < 1.0):
  (bellman_state0(v0, v1, r0, p00, p01, r1, p10, p11, g) <= bellman_state0(w0, w1, r0, p00, p01, r1, p10, p11, g))
-- Sup-norm bound. With each value entry in [-b, b] and each reward in
-- [-rmax, rmax], one Bellman step lands in [-(rmax + g * b), rmax + g * b]. The
-- bound is two-sided and proven as a single conjunction.
@property bellman_bounded forall(v0: f32, v1: f32, r0: f32, p00: f32, p01: f32, r1: f32, p10: f32, p11: f32, g: f32, b: f32, rmax: f32) where (v0 <= b), (v0 >= (0.0 - b)), (v1 <= b), (v1 >= (0.0 - b)), (r0 <= rmax), (r0 >= (0.0 - rmax)), (r1 <= rmax), (r1 >= (0.0 - rmax)), (b >= 0.0), (rmax >= 0.0), (p00 >= 0.0), (p01 >= 0.0), (p10 >= 0.0), (p11 >= 0.0), ((p00 + p01) == 1.0), ((p10 + p11) == 1.0), (g > 0.0), (g < 1.0):
  ((bellman_state0(v0, v1, r0, p00, p01, r1, p10, p11, g) <= (rmax + (g * b))) && (bellman_state0(v0, v1, r0, p00, p01, r1, p10, p11, g) >= (0.0 - (rmax + (g * b)))))
-- Contraction (upper side). One Bellman step on v exceeds one Bellman step on w
-- by at most g times the sup-norm distance between v and w. With the lower side
-- below, this is the full single-application g-contraction in the sup norm: it
-- is a premise of the Banach fixed-point argument, not its conclusion.
@property bellman_contraction forall(v0: f32, v1: f32, w0: f32, w1: f32, r0: f32, p00: f32, p01: f32, r1: f32, p10: f32, p11: f32, g: f32) where (p00 >= 0.0), (p01 >= 0.0), (p10 >= 0.0), (p11 >= 0.0), ((p00 + p01) == 1.0), ((p10 + p11) == 1.0), (g > 0.0), (g < 1.0):
  ((bellman_state0(v0, v1, r0, p00, p01, r1, p10, p11, g) - bellman_state0(w0, w1, r0, p00, p01, r1, p10, p11, g)) <= (g * fmax(fabs((v0 - w0)), fabs((v1 - w1)))))
-- Contraction (lower side). The symmetric lower bound on the same difference.
@property bellman_contraction_lower forall(v0: f32, v1: f32, w0: f32, w1: f32, r0: f32, p00: f32, p01: f32, r1: f32, p10: f32, p11: f32, g: f32) where (p00 >= 0.0), (p01 >= 0.0), (p10 >= 0.0), (p11 >= 0.0), ((p00 + p01) == 1.0), ((p10 + p11) == 1.0), (g > 0.0), (g < 1.0):
  ((bellman_state0(v0, v1, r0, p00, p01, r1, p10, p11, g) - bellman_state0(w0, w1, r0, p00, p01, r1, p10, p11, g)) >= (0.0 - (g * fmax(fabs((v0 - w0)), fabs((v1 - w1))))))
-- Non-vacuity witnesses. Each asserts false under the same guards as the
-- property above and must be refuted at the SMT tier: cvc5 finds a
-- guard-satisfying model, proving the guards are jointly satisfiable and the
-- green above is not vacuous.
@property bellman_monotone_guards_satisfiable forall(v0: f32, v1: f32, w0: f32, w1: f32, r0: f32, p00: f32, p01: f32, r1: f32, p10: f32, p11: f32, g: f32) where (v0 <= w0), (v1 <= w1), (p00 >= 0.0), (p01 >= 0.0), (p10 >= 0.0), (p11 >= 0.0), ((p00 + p01) == 1.0), ((p10 + p11) == 1.0), (g > 0.0), (g < 1.0):
  false
@property bellman_bounded_guards_satisfiable forall(v0: f32, v1: f32, r0: f32, p00: f32, p01: f32, r1: f32, p10: f32, p11: f32, g: f32, b: f32, rmax: f32) where (v0 <= b), (v0 >= (0.0 - b)), (v1 <= b), (v1 >= (0.0 - b)), (r0 <= rmax), (r0 >= (0.0 - rmax)), (r1 <= rmax), (r1 >= (0.0 - rmax)), (b >= 0.0), (rmax >= 0.0), (p00 >= 0.0), (p01 >= 0.0), (p10 >= 0.0), (p11 >= 0.0), ((p00 + p01) == 1.0), ((p10 + p11) == 1.0), (g > 0.0), (g < 1.0):
  false
@property bellman_contraction_guards_satisfiable forall(v0: f32, v1: f32, w0: f32, w1: f32, r0: f32, p00: f32, p01: f32, r1: f32, p10: f32, p11: f32, g: f32) where (p00 >= 0.0), (p01 >= 0.0), (p10 >= 0.0), (p11 >= 0.0), ((p00 + p01) == 1.0), ((p10 + p11) == 1.0), (g > 0.0), (g < 1.0):
  false
@property bellman_contraction_lower_guards_satisfiable forall(v0: f32, v1: f32, w0: f32, w1: f32, r0: f32, p00: f32, p01: f32, r1: f32, p10: f32, p11: f32, g: f32) where (p00 >= 0.0), (p01 >= 0.0), (p10 >= 0.0), (p11 >= 0.0), ((p00 + p01) == 1.0), ((p10 + p11) == 1.0), (g > 0.0), (g < 1.0):
  false
