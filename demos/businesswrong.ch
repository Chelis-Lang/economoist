module Economoist.Demos.Businesswrong
import Economoist.Markov (next_mass)
import Economoist.Bellman (fmax, fabs)
-- Business-wrong economic demos: importable content with stable IDs for C Note.
-- Each demo pairs a corrupted model (a *_wrong property that must be refuted,
-- exhibiting a decoded counterexample at the SMT tier) with its corrected
-- control (a *_control property that passes). These are the soundness-dependence
-- twins: corrupting an assumed invariant flips the verdict, proving each green
-- genuinely rests on its hypothesis.
--
-- Run: chelis prove demos/businesswrong.ch --json --tier auto
-- Demo 1: a transition whose rows do not sum to one fails mass preservation.
-- The wrong model drops the second row-stochasticity guard; cvc5 exhibits a
-- transition row that does not sum to one and a distribution whose total mass is
-- not preserved. The control reinstates the guard and preserves mass exactly.
@property markov_mass_wrong forall(p0: f32, p1: f32, t00: f32, t01: f32, t10: f32, t11: f32) where ((p0 + p1) == 1.0), ((t00 + t01) == 1.0):
  ((next_mass(p0, p1, t00, t10) + next_mass(p0, p1, t01, t11)) == 1.0)
@property markov_mass_control forall(p0: f32, p1: f32, t00: f32, t01: f32, t10: f32, t11: f32) where ((p0 + p1) == 1.0), ((t00 + t01) == 1.0), ((t10 + t11) == 1.0):
  ((next_mass(p0, p1, t00, t10) + next_mass(p0, p1, t01, t11)) == 1.0)
-- Demo 2: a Gordon model with growth at or above the discount gives a
-- non-positive or undefined present value. The wrong model assumes growth at or
-- above the discount; the positivity condition is then violated. The control
-- assumes the discount strictly exceeds growth.
@property gordon_positive_wrong forall(d: f32, r: f32, g: f32) where (d > 0.0), (g >= r):
  ((d > 0.0) && ((r - g) > 0.0))
@property gordon_positive_control forall(d: f32, r: f32, g: f32) where (d > 0.0), (r > g):
  ((d > 0.0) && ((r - g) > 0.0))
-- Demo 3: a discount factor outside (0, 1) breaks the contraction MODULUS. The
-- single-application Lipschitz bound |(Tv)_0 - (Tw)_0| <= g * sup|v - w| holds
-- for ANY g >= 0, so this demo is NOT a probe of the bound; it is a probe of the
-- modulus-below-one claim. The wrong model asks for the bound AND g < 1 while
-- guarding only g > 0, so cvc5 returns a discount g >= 1 that satisfies the bound
-- yet refutes the conjunction: with g >= 1 the step is not a genuine contraction.
-- The control keeps the discount strictly inside (0, 1) and both conjuncts hold.
-- The (Tv)_0 arithmetic is inlined on each side (see properties/bellman.ch for
-- why a bellman_state0(v...) - bellman_state0(w...) call form would mask).
@property bellman_contraction_modulus_wrong forall(v0: f32, v1: f32, w0: f32, w1: f32, r0: f32, p00: f32, p01: f32, r1: f32, p10: f32, p11: f32, g: f32) where (p00 >= 0.0), (p01 >= 0.0), (p10 >= 0.0), (p11 >= 0.0), ((p00 + p01) == 1.0), ((p10 + p11) == 1.0), (g > 0.0):
  (((fmax((r0 + (g * ((p00 * v0) + (p01 * v1)))), (r1 + (g * ((p10 * v0) + (p11 * v1))))) - fmax((r0 + (g * ((p00 * w0) + (p01 * w1)))), (r1 + (g * ((p10 * w0) + (p11 * w1)))))) <= (g * fmax(fabs((v0 - w0)), fabs((v1 - w1))))) && (g < 1.0))
@property bellman_contraction_modulus_control forall(v0: f32, v1: f32, w0: f32, w1: f32, r0: f32, p00: f32, p01: f32, r1: f32, p10: f32, p11: f32, g: f32) where (p00 >= 0.0), (p01 >= 0.0), (p10 >= 0.0), (p11 >= 0.0), ((p00 + p01) == 1.0), ((p10 + p11) == 1.0), (g > 0.0), (g < 1.0):
  (((fmax((r0 + (g * ((p00 * v0) + (p01 * v1)))), (r1 + (g * ((p10 * v0) + (p11 * v1))))) - fmax((r0 + (g * ((p00 * w0) + (p01 * w1)))), (r1 + (g * ((p10 * w0) + (p11 * w1)))))) <= (g * fmax(fabs((v0 - w0)), fabs((v1 - w1))))) && (g < 1.0))
-- Demo 4: dropping row-stochasticity breaks the contraction BOUND itself. This
-- is the soundness-dependence probe for the per-output-state contraction. The
-- load-bearing guard for |(Tv)_0 - (Tw)_0| <= g * sup|v - w| is that each
-- action's transition row is nonneg and sums to one: a row summing above one
-- lets the discounted expected continuation amplify the value gap, so the
-- difference can exceed g * sup. The wrong model drops the second row's
-- sum == 1.0 guard (keeping nonnegativity and the first row's sum); cvc5 returns
-- a non-stochastic row (its two entries sum above one) for which the bound fails.
-- The control reinstates both row sums and the bound holds.
@property bellman_contraction_rowsum_wrong forall(v0: f32, v1: f32, w0: f32, w1: f32, r0: f32, p00: f32, p01: f32, r1: f32, p10: f32, p11: f32, g: f32) where (p00 >= 0.0), (p01 >= 0.0), (p10 >= 0.0), (p11 >= 0.0), ((p00 + p01) == 1.0), (g > 0.0), (g < 1.0):
  ((fmax((r0 + (g * ((p00 * v0) + (p01 * v1)))), (r1 + (g * ((p10 * v0) + (p11 * v1))))) - fmax((r0 + (g * ((p00 * w0) + (p01 * w1)))), (r1 + (g * ((p10 * w0) + (p11 * w1)))))) <= (g * fmax(fabs((v0 - w0)), fabs((v1 - w1)))))
@property bellman_contraction_rowsum_control forall(v0: f32, v1: f32, w0: f32, w1: f32, r0: f32, p00: f32, p01: f32, r1: f32, p10: f32, p11: f32, g: f32) where (p00 >= 0.0), (p01 >= 0.0), (p10 >= 0.0), (p11 >= 0.0), ((p00 + p01) == 1.0), ((p10 + p11) == 1.0), (g > 0.0), (g < 1.0):
  ((fmax((r0 + (g * ((p00 * v0) + (p01 * v1)))), (r1 + (g * ((p10 * v0) + (p11 * v1))))) - fmax((r0 + (g * ((p00 * w0) + (p01 * w1)))), (r1 + (g * ((p10 * w0) + (p11 * w1)))))) <= (g * fmax(fabs((v0 - w0)), fabs((v1 - w1)))))
