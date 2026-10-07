module Economoist.Properties.Growth
import Economoist.Growth (gordon_pv, gordon_pv_strict)
-- The Gordon goals call the exported closed-form value gordon_pv. SMT checks
-- positivity and two-point comparisons over the reals under their written
-- guards. They do not establish convergence of a dividend series or any
-- claim about f32 rounding. Gordon has no state dimension. See
-- docs/book/src/models/growth.md.
-- Under d > 0 and r > g, the closed-form value d / (r - g) is positive.
@property gordon_positive forall(d: f32, r: f32, g: f32) where d > 0.0, r > g:
  (gordon_pv(d, r, g) > 0.0)
-- Increasing in the dividend. For a fixed required return and growth (r > g), a
-- larger next-period dividend gives a larger present value: d2 > d1 makes
-- gordon_pv strictly larger. The goal calls the export at both values.
@property gordon_increasing_in_d forall(d1: f32, d2: f32, r: f32, g: f32) where r > g, d2 > d1:
  (gordon_pv(d2, r, g) > gordon_pv(d1, r, g))
-- Decreasing in the required return. Raising r from r1 to r2 (r2 > r1) shrinks
-- the present value: gordon_pv at r2 is strictly below gordon_pv at r1. Two-call
-- comparison calls the export at both input points.
@property gordon_decreasing_in_r forall(d: f32, r1: f32, r2: f32, g: f32) where d > 0.0, r1 > g, r2 > r1:
  (gordon_pv(d, r2, g) < gordon_pv(d, r1, g))
-- Non-vacuity witnesses. Each asserts false under the same forall and guards as
-- its property above and must be refuted by SMT: cvc5 finds a
-- guard-satisfying model, proving the guards are jointly satisfiable and the
-- corresponding checked claim is not vacuous.
@property gordon_positive_guards_satisfiable forall(d: f32, r: f32, g: f32) where d > 0.0, r > g:
  false
@property gordon_increasing_in_d_guards_satisfiable forall(d1: f32, d2: f32, r: f32, g: f32) where r > g, d2 > d1:
  false
@property gordon_decreasing_in_r_guards_satisfiable forall(d: f32, r1: f32, r2: f32, g: f32) where d > 0.0, r1 > g, r2 > r1:
  false
-- Strict (margin-of-safety) positivity. Under D > 0 and the tighter spread
-- condition r > g + 0.01 (the discount spread clears a one-point safety margin),
-- the conservative present value gordon_pv_strict(d, r, g) is strictly positive.
-- Same division-form call as gordon_positive; the tighter guard IS the documented
-- domain of use, and its checked region {d > 0, r > g + 0.01} nests strictly
-- inside gordon_positive's {d > 0, r > g}.
@property gordon_strict_positive forall(d: f32, r: f32, g: f32) where d > 0.0, r > (g + 0.01):
  (gordon_pv_strict(d, r, g) > 0.0)
@property gordon_strict_positive_guards_satisfiable forall(d: f32, r: f32, g: f32) where d > 0.0, r > (g + 0.01):
  false
