module Economoist.Demos.Businesswrong
import Economoist.Markov (next_mass, mass3_next)
import Economoist.Growth (gordon_pv, gordon_pv_strict, gordon_pv_negated)
import Economoist.Bellman (bellman_state0, bellman_state0_n3, fmax, fmax3, fabs)
-- Counterexamples to economically false claims, each paired with a
-- passing control. The proof gate requires every *_wrong claim to refute
-- and every *_control claim to pass under real-arithmetic SMT. These are
-- one-step examples where the model has state; the Markov and Bellman
-- examples use fixed dimensions. Concrete f32 behavior is checked
-- separately. Property names are stable C Note IDs.
-- Run: chelis prove demos/businesswrong.ch --json --tier auto
-- Demo 1: a transition whose rows do not sum to one fails mass preservation.
-- The wrong model drops the second row-stochasticity guard; cvc5 exhibits a
-- transition row that does not sum to one and a distribution whose total mass is
-- not preserved. The control reinstates the guard and preserves mass exactly.
@property markov_mass_wrong forall(p0: f32, p1: f32, t00: f32, t01: f32, t10: f32, t11: f32) where (p0 + p1) == 1.0, (t00 + t01) == 1.0:
  ((next_mass(p0, p1, t00, t10) + next_mass(p0, p1, t01, t11)) == 1.0)
@property markov_mass_control forall(p0: f32, p1: f32, t00: f32, t01: f32, t10: f32, t11: f32) where (p0 + p1) == 1.0, (t00 + t01) == 1.0, (t10 + t11) == 1.0:
  ((next_mass(p0, p1, t00, t10) + next_mass(p0, p1, t01, t11)) == 1.0)
-- Demo 2 (out-of-region break): a Gordon model evaluated with growth at or above
-- the discount is outside the validity region r > g, where the present value is
-- non-positive or undefined. The wrong property asserts positivity of gordon_pv
-- under g >= r; cvc5 returns a witness with growth above the discount for which
-- the present value is negative. The control keeps r > g (in region) and passes.
-- This is the OUT-OF-REGION exemplar: the model is correct, the inputs leave its
-- validity region.
@property gordon_positive_wrong forall(d: f32, r: f32, g: f32) where d > 0.0, g > r:
  (gordon_pv(d, r, g) > 0.0)
@property gordon_positive_control forall(d: f32, r: f32, g: f32) where d > 0.0, r > g:
  (gordon_pv(d, r, g) > 0.0)
-- Demo 3 (in-region defect): the DEFECTIVE gordon_pv_negated model (a mispriced
-- perpetuity returning the negative of the correct present value) breaks the
-- positivity canon invariant INSIDE its validity region r > g. The wrong property
-- asserts positivity of the defective model under the correct guards d > 0, r > g;
-- cvc5 returns an in-region witness for which the negated value is negative. The
-- control asserts the same invariant of the sound gordon_pv and passes. This is
-- the IN-REGION-DEFECT exemplar: the inputs are in region, the model is wrong.
@property gordon_pv_corrupted_wrong forall(d: f32, r: f32, g: f32) where d > 0.0, r > g:
  (gordon_pv_negated(d, r, g) > 0.0)
@property gordon_pv_corrupted_control forall(d: f32, r: f32, g: f32) where d > 0.0, r > g:
  (gordon_pv(d, r, g) > 0.0)
-- Demo 3b (out-of-region break, strict variant): the conservative
-- gordon_pv_strict model priced with growth above the discount is outside its
-- strict validity region r > g + 0.01 (and outside r > g entirely). The wrong
-- property asserts positivity under g > r; cvc5 returns a witness with the growth
-- above the discount for which the present value is negative. The control keeps
-- the strict margin r > g + 0.01 and passes. This is the out-of-region twin for
-- the strict positivity invariant whose proven region nests inside the standard
-- one.
@property gordon_strict_positive_wrong forall(d: f32, r: f32, g: f32) where d > 0.0, g > r:
  (gordon_pv_strict(d, r, g) > 0.0)
@property gordon_strict_positive_control forall(d: f32, r: f32, g: f32) where d > 0.0, r > (g + 0.01):
  (gordon_pv_strict(d, r, g) > 0.0)
-- Demo 4: without v <= w, the difference of two calls of the Bellman
-- operator can be positive, so the wrong bound must refute. With entrywise
-- domination, the control proves. This pair also guards two-call ITE
-- lowering (chelis#426).
@property bellman_call_collapse_wrong forall(v0: f32, v1: f32, w0: f32, w1: f32, r0: f32, p00: f32, p01: f32, r1: f32, p10: f32, p11: f32, g: f32) where p00 >= 0.0, p01 >= 0.0, p10 >= 0.0, p11 >= 0.0, (p00 + p01) == 1.0, (p10 + p11) == 1.0, g > 0.0, g < 1.0:
  ((bellman_state0(v0, v1, r0, p00, p01, r1, p10, p11, g) - bellman_state0(w0, w1, r0, p00, p01, r1, p10, p11, g)) <= 0.0)
@property bellman_call_collapse_control forall(v0: f32, v1: f32, w0: f32, w1: f32, r0: f32, p00: f32, p01: f32, r1: f32, p10: f32, p11: f32, g: f32) where v0 <= w0, v1 <= w1, p00 >= 0.0, p01 >= 0.0, p10 >= 0.0, p11 >= 0.0, (p00 + p01) == 1.0, (p10 + p11) == 1.0, g > 0.0, g < 1.0:
  ((bellman_state0(v0, v1, r0, p00, p01, r1, p10, p11, g) - bellman_state0(w0, w1, r0, p00, p01, r1, p10, p11, g)) <= 0.0)
-- Demo 5: a discount factor outside (0, 1) breaks the contraction MODULUS. The
-- single-application Lipschitz bound |(Tv)_0 - (Tw)_0| <= g * sup|v - w| holds for
-- ANY g >= 0, so this demo is NOT a probe of the bound; it is a probe of the
-- modulus-below-one claim. The wrong model asks for the bound AND g < 1 while
-- guarding only g > 0, so cvc5 returns a discount g >= 1 that satisfies the bound
-- yet refutes the conjunction. The control keeps the discount strictly inside
-- (0, 1). Both call bellman_state0 directly.
@property bellman_contraction_modulus_wrong forall(v0: f32, v1: f32, w0: f32, w1: f32, r0: f32, p00: f32, p01: f32, r1: f32, p10: f32, p11: f32, g: f32) where p00 >= 0.0, p01 >= 0.0, p10 >= 0.0, p11 >= 0.0, (p00 + p01) == 1.0, (p10 + p11) == 1.0, g > 0.0:
  (((bellman_state0(v0, v1, r0, p00, p01, r1, p10, p11, g) - bellman_state0(w0, w1, r0, p00, p01, r1, p10, p11, g)) <= (g * fmax(fabs((v0 - w0)), fabs((v1 - w1))))) && (g < 1.0))
@property bellman_contraction_modulus_control forall(v0: f32, v1: f32, w0: f32, w1: f32, r0: f32, p00: f32, p01: f32, r1: f32, p10: f32, p11: f32, g: f32) where p00 >= 0.0, p01 >= 0.0, p10 >= 0.0, p11 >= 0.0, (p00 + p01) == 1.0, (p10 + p11) == 1.0, g > 0.0, g < 1.0:
  (((bellman_state0(v0, v1, r0, p00, p01, r1, p10, p11, g) - bellman_state0(w0, w1, r0, p00, p01, r1, p10, p11, g)) <= (g * fmax(fabs((v0 - w0)), fabs((v1 - w1))))) && (g < 1.0))
-- Demo 6: dropping row-stochasticity breaks the contraction BOUND itself. The
-- bound |(Tv)_0 - (Tw)_0| <= g * sup|v - w| requires each action's
-- transition row to be nonnegative and sum to one. The wrong model drops the second
-- row's sum == 1.0 guard; cvc5 returns a non-stochastic row (its entries sum above
-- one) for which the bound fails. The control reinstates both row sums. Both call
-- bellman_state0 directly.
@property bellman_contraction_rowsum_wrong forall(v0: f32, v1: f32, w0: f32, w1: f32, r0: f32, p00: f32, p01: f32, r1: f32, p10: f32, p11: f32, g: f32) where p00 >= 0.0, p01 >= 0.0, p10 >= 0.0, p11 >= 0.0, (p00 + p01) == 1.0, g > 0.0, g < 1.0:
  ((bellman_state0(v0, v1, r0, p00, p01, r1, p10, p11, g) - bellman_state0(w0, w1, r0, p00, p01, r1, p10, p11, g)) <= (g * fmax(fabs((v0 - w0)), fabs((v1 - w1)))))
@property bellman_contraction_rowsum_control forall(v0: f32, v1: f32, w0: f32, w1: f32, r0: f32, p00: f32, p01: f32, r1: f32, p10: f32, p11: f32, g: f32) where p00 >= 0.0, p01 >= 0.0, p10 >= 0.0, p11 >= 0.0, (p00 + p01) == 1.0, (p10 + p11) == 1.0, g > 0.0, g < 1.0:
  ((bellman_state0(v0, v1, r0, p00, p01, r1, p10, p11, g) - bellman_state0(w0, w1, r0, p00, p01, r1, p10, p11, g)) <= (g * fmax(fabs((v0 - w0)), fabs((v1 - w1)))))
-- Demo 7: the Gordon decreasing-in-r monotonicity loses its soundness when the
-- second return is not actually larger. The wrong model drops the r2 > r1 guard
-- (keeping only r2 > g), so cvc5 returns r2 < r1 for which the present value at r2
-- is NOT below the value at r1. The control reinstates r2 > r1 and the strict
-- decrease holds. Both reference gordon_pv.
@property gordon_decreasing_in_r_wrong forall(d: f32, r1: f32, r2: f32, g: f32) where d > 0.0, r1 > g, r2 > g:
  (gordon_pv(d, r2, g) < gordon_pv(d, r1, g))
@property gordon_decreasing_in_r_control forall(d: f32, r1: f32, r2: f32, g: f32) where d > 0.0, r1 > g, r2 > r1:
  (gordon_pv(d, r2, g) < gordon_pv(d, r1, g))
-- Demo 8: the n=3 mass-preservation identity fails when a transition
-- row is not stochastic. The wrong model drops the third row's sum == 1.0 guard;
-- cvc5 returns a non-stochastic third row for which the three output masses do not
-- sum to one. The control reinstates all three row sums. Both reference mass3_next.
@property markov3_mass_wrong forall(p0: f32, p1: f32, p2: f32, t00: f32, t01: f32, t02: f32, t10: f32, t11: f32, t12: f32, t20: f32, t21: f32, t22: f32) where ((p0 + p1) + p2) == 1.0, ((t00 + t01) + t02) == 1.0, ((t10 + t11) + t12) == 1.0:
  (((mass3_next(p0, p1, p2, t00, t10, t20) + mass3_next(p0, p1, p2, t01, t11, t21)) + mass3_next(p0, p1, p2, t02, t12, t22)) == 1.0)
@property markov3_mass_control forall(p0: f32, p1: f32, p2: f32, t00: f32, t01: f32, t02: f32, t10: f32, t11: f32, t12: f32, t20: f32, t21: f32, t22: f32) where ((p0 + p1) + p2) == 1.0, ((t00 + t01) + t02) == 1.0, ((t10 + t11) + t12) == 1.0, ((t20 + t21) + t22) == 1.0:
  (((mass3_next(p0, p1, p2, t00, t10, t20) + mass3_next(p0, p1, p2, t01, t11, t21)) + mass3_next(p0, p1, p2, t02, t12, t22)) == 1.0)
-- Demo 9: the n=3 per-state contraction requires the same row guards
-- as the n=2 case: each transition row is nonnegative and sums to one. The wrong
-- model drops the second row's sum == 1.0 guard; cvc5 returns a non-stochastic row
-- for which the n=3 contraction bound fails. The control reinstates both row sums.
-- Both call bellman_state0_n3 directly with the fmax3 three-coordinate sup.
@property bellman_contraction_rowsum_n3_wrong forall(v0: f32, v1: f32, v2: f32, w0: f32, w1: f32, w2: f32, r0: f32, p00: f32, p01: f32, p02: f32, r1: f32, p10: f32, p11: f32, p12: f32, g: f32) where p00 >= 0.0, p01 >= 0.0, p02 >= 0.0, p10 >= 0.0, p11 >= 0.0, p12 >= 0.0, ((p00 + p01) + p02) == 1.0, g > 0.0, g < 1.0:
  ((bellman_state0_n3(v0, v1, v2, r0, p00, p01, p02, r1, p10, p11, p12, g) - bellman_state0_n3(w0, w1, w2, r0, p00, p01, p02, r1, p10, p11, p12, g)) <= (g * fmax3(fabs((v0 - w0)), fabs((v1 - w1)), fabs((v2 - w2)))))
@property bellman_contraction_rowsum_n3_control forall(v0: f32, v1: f32, v2: f32, w0: f32, w1: f32, w2: f32, r0: f32, p00: f32, p01: f32, p02: f32, r1: f32, p10: f32, p11: f32, p12: f32, g: f32) where p00 >= 0.0, p01 >= 0.0, p02 >= 0.0, p10 >= 0.0, p11 >= 0.0, p12 >= 0.0, ((p00 + p01) + p02) == 1.0, ((p10 + p11) + p12) == 1.0, g > 0.0, g < 1.0:
  ((bellman_state0_n3(v0, v1, v2, r0, p00, p01, p02, r1, p10, p11, p12, g) - bellman_state0_n3(w0, w1, w2, r0, p00, p01, p02, r1, p10, p11, p12, g)) <= (g * fmax3(fabs((v0 - w0)), fabs((v1 - w1)), fabs((v2 - w2)))))
