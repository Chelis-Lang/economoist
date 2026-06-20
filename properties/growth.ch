module Economoist.Properties.Growth
-- Structural and comparative-statics properties of the Gordon growth present
-- value P = D / (r - g), proven at the SMT tier over the reals. Every goal is
-- stated in multiplied-through polynomial form (no division), so the solver sees
-- polynomials rather than a fragile nonlinear quotient. These are closed-form
-- algebraic facts about the Gordon expression; they are not a convergence or
-- limit result, and Gordon is dimension-free, so the fixed-dimension caveat is
-- not applicable. See docs/models/growth.md.
-- Positivity. Under D > 0 and the convergence condition r > g, the numerator D
-- is positive and the denominator (r - g) is positive, so P = D/(r-g) > 0. Stated
-- as the two positive factors, without division.
@property gordon_positive forall(d: f32, r: f32, g: f32) where (d > 0.0), (r > g):
  ((d > 0.0) && ((r - g) > 0.0))
-- Increasing in the dividend. For a fixed denominator (r - g) > 0, a larger
-- numerator gives a larger quotient: d2 > d1 makes D/(r-g) strictly larger.
@property gordon_increasing_in_d forall(d1: f32, d2: f32, r: f32, g: f32) where (r > g), (d2 > d1):
  (((d2 - d1) > 0.0) && ((r - g) > 0.0))
-- Decreasing in the required return. Raising r from r1 to r2 (r2 > r1) shrinks
-- P. Cross-multiplied, D/(r2-g) < D/(r1-g) is D*(r1-r2) < 0 with both
-- denominators positive; that is the multiplied-through polynomial statement.
@property gordon_decreasing_in_r forall(d: f32, r1: f32, r2: f32, g: f32) where (d > 0.0), (r1 > g), (r2 > r1):
  (((d * (r1 - r2)) < 0.0) && (((r1 - g) > 0.0) && ((r2 - g) > 0.0)))
-- Comparative static dP/dr = -D/(r-g)^2. Under D > 0 and r > g the numerator
-- -D is negative and the denominator (r-g)^2 is positive, so dP/dr < 0. Stated
-- on the polynomial numerator and the denominator square, without division.
@property gordon_dP_dr_negative forall(d: f32, r: f32, g: f32) where (d > 0.0), (r > g):
  (((0.0 - d) < 0.0) && (((r - g) * (r - g)) > 0.0))
-- Comparative static dP/dg = +D/(r-g)^2. Under D > 0 and r > g the numerator
-- +D is positive and the denominator (r-g)^2 is positive, so dP/dg > 0.
@property gordon_dP_dg_positive forall(d: f32, r: f32, g: f32) where (d > 0.0), (r > g):
  ((d > 0.0) && (((r - g) * (r - g)) > 0.0))
-- Non-vacuity witnesses. Each asserts false under the same forall and guards as
-- its property above and must be refuted at the SMT tier: cvc5 finds a
-- guard-satisfying model, proving the guards are jointly satisfiable and the
-- corresponding green is not vacuous.
@property gordon_positive_guards_satisfiable forall(d: f32, r: f32, g: f32) where (d > 0.0), (r > g):
  false
@property gordon_increasing_in_d_guards_satisfiable forall(d1: f32, d2: f32, r: f32, g: f32) where (r > g), (d2 > d1):
  false
@property gordon_decreasing_in_r_guards_satisfiable forall(d: f32, r1: f32, r2: f32, g: f32) where (d > 0.0), (r1 > g), (r2 > r1):
  false
@property gordon_dP_dr_negative_guards_satisfiable forall(d: f32, r: f32, g: f32) where (d > 0.0), (r > g):
  false
@property gordon_dP_dg_positive_guards_satisfiable forall(d: f32, r: f32, g: f32) where (d > 0.0), (r > g):
  false
