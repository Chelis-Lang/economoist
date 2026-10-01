module Economoist.Sampled.Growth_sensitivity
import Economoist.Growth (gordon_pv)
-- This check differentiates the imported gordon_pv export with respect
-- to r. It samples concrete f32 AD results within the written guards; a
-- passing check is fuzz-validated, not a proof for every input. The separate
-- two-point gordon_decreasing_in_r property proves its real-arithmetic
-- comparison. Both this check and its wrong-sign twin call the export
-- directly, so the package proof gate can verify the dependency edge.
-- Run with --tier fuzz-only --samples 500 --seed 0.
@property gordon_dP_dr_negative_grad forall(d: f32, r: f32, g: f32) where d > 0.5, d < 9.5, g > 0.0, g < 4.0, r > g, r < 9.5:
  (grad(fn (dd: f32, rr: f32, gg: f32) -> gordon_pv(dd, rr, gg), wrt=rr)(d, r, g) < 0.0)
-- Corrupted twin: asserts the AD derivative is positive, which is false under the guards; fuzz returns an in-box counterexample. It flips only the
-- sign, so a wrong sign is the sole difference from the positive check above.
@property gordon_dP_dr_negative_grad_wrong forall(d: f32, r: f32, g: f32) where d > 0.5, d < 9.5, g > 0.0, g < 4.0, r > g, r < 9.5:
  (grad(fn (dd: f32, rr: f32, gg: f32) -> gordon_pv(dd, rr, gg), wrt=rr)(d, r, g) > 0.0)
