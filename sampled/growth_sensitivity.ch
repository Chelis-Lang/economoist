module Economoist.Sampled.Growth_sensitivity
import Economoist.Growth (gordon_pv)
-- SAMPLED lane (module prefix Economoist.Sampled): weaker-tier library invariants
-- that are honest amber, NOT unqualified SMT greens. The properties/ tree keeps
-- the pure-SMT-green boundary that is this shell's identity; anything that only
-- validates by fuzz sampling lives here, gated separately (proof_tier == "fuzz",
-- status == "passed", expected_tier fuzz_validated). See AGENTS.md and
-- docs/contracts/characterization_contract_v1.md for the split rationale.
--
-- Gordon sensitivity dP/dr, by automatic differentiation. grad differentiates
-- the exported gordon_pv function with respect to the required return r; the
-- sign of the result confirms the same comparative static the
-- two-point SMT green gordon_decreasing_in_r proves over the reals (P is
-- decreasing in r). This is an f32 AD value validated by fuzz over the guard box,
-- NOT a proof: it is amber and carries a tier_upgrade_trigger.
--
-- ANTI-VACUITY, direct: both the satisfying property and its corrupt sign twin
-- differentiate the imported Economoist.Growth.gordon_pv export.
-- Economoist#13 verified this direct binding at the 0.17.1 pin. Chelis#924's
-- package-context cache ships in the pinned release; no downstream copy or
-- reconstructed expression stands between the property and the shipped model.
-- Guards sit inside the prover fuzz box [-10,10]^n with comfortable acceptance
-- (cnote.dischargeability p05/p11). Run at --tier fuzz-only --samples 500 --seed 0.
-- dP/dr < 0: the AD derivative of the Gordon body wrt r is negative throughout
-- the convergence region r > g. Fuzz-validated (amber).
@property gordon_dP_dr_negative_grad forall(d: f32, r: f32, g: f32) where (d > 0.5), (d < 9.5), (g > 0.0), (g < 4.0), (r > g), (r < 9.5):
  (grad(fn (dd: f32, rr: f32, gg: f32) -> gordon_pv(dd, rr, gg), wrt=rr)(d, r, g) < 0.0)
-- Corrupted twin: asserts the AD derivative is positive, which is false in the
-- convergence region; fuzz returns an in-box counterexample. It flips only the
-- sign, so a wrong sign is the sole difference from the green above.
@property gordon_dP_dr_negative_grad_wrong forall(d: f32, r: f32, g: f32) where (d > 0.5), (d < 9.5), (g > 0.0), (g < 4.0), (r > g), (r < 9.5):
  (grad(fn (dd: f32, rr: f32, gg: f32) -> gordon_pv(dd, rr, gg), wrt=rr)(d, r, g) > 0.0)
