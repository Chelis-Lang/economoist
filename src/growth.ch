module Economoist.Growth
export (gordon_pv)
-- Economoist.Growth: the Gordon growth model present value of a perpetuity whose
-- cash flow grows at a constant rate. With next-period dividend D, required
-- return r, and growth rate g (all under the convergence condition r > g), the
-- present value of the growing perpetuity is the closed form P = D / (r - g).
--
-- This is a closed-form algebraic value in three scalars (D, r, g). There is no
-- state dimension and no iteration: the geometric series has already been summed
-- to its closed form, so the fixed-dimension (general-n) caveat that applies to
-- the Markov and Bellman instances is NOT APPLICABLE here. The two caveats that
-- do apply are the convergence-class condition (the closed form is the limit of
-- the discounted sum only when r > g; the guards carry exactly that) and the
-- reals-vs-floats boundary (the proven facts are real arithmetic, not f32).
--
-- PROVEN here (SMT, transcendental-free, over the reals; see
-- docs/models/growth.md), stated in multiplied-through polynomial form so the
-- solver sees polynomials rather than a division:
--   gordon_positive          : under D > 0 and r > g the value P = D/(r-g) > 0.
--   gordon_increasing_in_d    : P is increasing in the dividend D.
--   gordon_decreasing_in_r    : P is decreasing in the required return r.
--   gordon_dP_dr_negative     : the comparative static dP/dr = -D/(r-g)^2 < 0.
--   gordon_dP_dg_positive     : the comparative static dP/dg = +D/(r-g)^2 > 0.
-- HELD OUT: these are facts about the closed-form expression itself, not about
--   the convergence of the underlying discounted sum to that closed form (a
--   limit result, which needs the geometric-series argument and is held out).
--   No f32 float claim is made: the green is real arithmetic.
def gordon_pv(d: f32, r: f32, g: f32) -> f32 = (d / (r - g))
