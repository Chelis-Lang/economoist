module Economoist.Demos.Businesswrong
import Economoist.Markov (next_mass)
import Economoist.Bellman (bellman_state0, fmax, fabs)
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
-- Demo 3: a discount factor outside (0, 1) breaks the Bellman contraction. The
-- single-application bound holds, but the modulus is no longer a genuine
-- contraction: the wrong model allows the discount to reach or exceed one, so
-- the contraction-modulus claim is refuted with a discount at or above one. The
-- control keeps the discount strictly inside (0, 1).
@property bellman_contraction_modulus_wrong forall(v0: f32, v1: f32, w0: f32, w1: f32, r0: f32, p00: f32, p01: f32, r1: f32, p10: f32, p11: f32, g: f32) where (p00 >= 0.0), (p01 >= 0.0), (p10 >= 0.0), (p11 >= 0.0), ((p00 + p01) == 1.0), ((p10 + p11) == 1.0), (g > 0.0):
  (((bellman_state0(v0, v1, r0, p00, p01, r1, p10, p11, g) - bellman_state0(w0, w1, r0, p00, p01, r1, p10, p11, g)) <= (g * fmax(fabs((v0 - w0)), fabs((v1 - w1))))) && (g < 1.0))
@property bellman_contraction_modulus_control forall(v0: f32, v1: f32, w0: f32, w1: f32, r0: f32, p00: f32, p01: f32, r1: f32, p10: f32, p11: f32, g: f32) where (p00 >= 0.0), (p01 >= 0.0), (p10 >= 0.0), (p11 >= 0.0), ((p00 + p01) == 1.0), ((p10 + p11) == 1.0), (g > 0.0), (g < 1.0):
  (((bellman_state0(v0, v1, r0, p00, p01, r1, p10, p11, g) - bellman_state0(w0, w1, r0, p00, p01, r1, p10, p11, g)) <= (g * fmax(fabs((v0 - w0)), fabs((v1 - w1))))) && (g < 1.0))
