module Economoist.Growth
export (gordon_pv, gordon_pv_strict, gordon_pv_negated)
-- Gordon closed-form value P = D / (r - g), with next-period dividend D,
-- required return r, and growth rate g. Under D > 0 and r > g the value is
-- positive. The checked two-point comparisons show it increases with D
-- and decreases with r under their written guards. These are real-arithmetic
-- facts about the exported expression, not f32 guarantees or proofs that a
-- dividend series converges. For the usual nonnegative-growth, positive-return
-- series, 0 <= g < r supplies a convergent economic rate domain; the general
-- real-rate series also needs r != -1 and |(1+g)/(1+r)| < 1. See
-- docs/models/growth.md.
--
-- gordon_pv_strict uses the same formula with a stated r > g + 0.01 domain.
-- gordon_pv_negated is an intentionally defective model whose false
-- positivity claim must refute inside the valid region.
def gordon_pv(d: f32, r: f32, g: f32) -> f32 = (d / (r - g))
-- The conservative (margin-of-safety) Gordon variant. Numerically identical to
-- gordon_pv -- the present value of the same growing perpetuity -- but it is the
-- model a cautious analyst uses when the discount spread r - g must clear a
-- safety margin before the valuation is trusted. Its documented domain of use is
-- the strict region r > g + 0.01 (the spread clears a one-point margin), which is
-- a proper subset of the closed form's positive-denominator region r > g.
-- The strict model's checked positivity region nests inside the standard
-- model's checked positivity region. Both exports use the same formula;
-- the tighter spread is a domain-of-use choice. See docs/models/growth.md.
def gordon_pv_strict(d: f32, r: f32, g: f32) -> f32 = (d / (r - g))
-- A DEFECTIVE reference model: a mispriced perpetuity that returns the negative
-- of the correct Gordon present value. It is a first-class model in the manifest
-- (defective: true) whose canon positivity invariant breaks IN its stated
-- validity region (under D > 0 and r > g the correct value is positive, so this
-- negated value is negative). It exists to exercise the in-region-defect break
-- class of the characterization surface: the break has an f32-confirmed in-domain
-- witness (demos/businesswrong.ch gordon_pv_corrupted_wrong), distinct from the
-- out-of-region break gordon_positive_wrong (which flips the r > g guard instead
-- of corrupting the model). It is NOT a claim about economics; it is a deliberate
-- defect the gallery must characterize as broken.
def gordon_pv_negated(d: f32, r: f32, g: f32) -> f32 = (0.0 - (d / (r - g)))
