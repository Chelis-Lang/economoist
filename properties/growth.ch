module Economoist.Properties.Growth
import Economoist.Growth (gordon_pv)
-- Structural and comparative-statics properties of the Gordon growth present
-- value P = D / (r - g), proven at the SMT tier over the reals. Every goal
-- REFERENCES the exported gordon_pv operator (positivity calls it once;
-- comparative statics compare two calls at shifted inputs), so each green is a
-- fact about the shipped model, not a restatement of its guards. The
-- division-form goals lower to cvc5 and discharge as unqualified greens
-- (verified at chelis 0.14.0; cnote.dischargeability p01/p02/p03). These are
-- closed-form algebraic facts about the Gordon expression, not a convergence or
-- limit result, and Gordon is dimension-free, so the fixed-dimension caveat is
-- not applicable. See docs/models/growth.md.
-- Positivity. Under D > 0 and the convergence condition r > g the present value
-- P = gordon_pv(d, r, g) = D / (r - g) is strictly positive. Proven by calling
-- the operator directly (cnote.dischargeability p01: the division form proves).
@property gordon_positive forall(d: f32, r: f32, g: f32) where (d > 0.0), (r > g):
  (gordon_pv(d, r, g) > 0.0)
-- Increasing in the dividend. For a fixed required return and growth (r > g), a
-- larger next-period dividend gives a larger present value: d2 > d1 makes
-- gordon_pv strictly larger. Two-call output-referencing form (p03 proves).
@property gordon_increasing_in_d forall(d1: f32, d2: f32, r: f32, g: f32) where (r > g), (d2 > d1):
  (gordon_pv(d2, r, g) > gordon_pv(d1, r, g))
-- Decreasing in the required return. Raising r from r1 to r2 (r2 > r1) shrinks
-- the present value: gordon_pv at r2 is strictly below gordon_pv at r1. Two-call
-- output-referencing form (p02 proves).
@property gordon_decreasing_in_r forall(d: f32, r1: f32, r2: f32, g: f32) where (d > 0.0), (r1 > g), (r2 > r1):
  (gordon_pv(d, r2, g) < gordon_pv(d, r1, g))
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
