# Draft: grad-based sensitivity goals do not lower to the SMT tier

Not yet filed upstream (draft; cite this path until a chelis#NNN is assigned).

**Summary.** A `@property` goal whose body contains `grad(...)` (automatic
differentiation of a scalar expression) does not lower to Tier B (cvc5); at
`--tier auto` it degrades to fuzz sampling. There is no way to obtain an
unqualified SMT green for an AD-derivative sign fact; the honest tier is
`fuzz_validated`.

**Impact on downstream shells.** Economoist's Gordon sensitivity dP/dr < 0 is a
genuine comparative-static fact, but as a `grad` goal it only fuzz-validates. It
therefore ships in the sampled lane (`fuzz_validated`, amber), NOT in the
proven `properties/` boundary. The same economic content IS available as an
unqualified SMT green via the two-point form `gordon_decreasing_in_r`
(`gordon_pv(d, r2, g) < gordon_pv(d, r1, g)`), which proves over the reals; the
grad lane is the AD confirmation at a point, not a proof.

**Reproducer (chelis 0.14.0).** `grad(fn (dd, rr, gg) -> (dd / (rr - gg)),
wrt=rr)(d, r, g) < 0.0` under `d>0.5, r>g` reports `proof_tier: fuzz`,
`composite_verdict: fuzz_validated` at `--tier auto`, and `unsupported` at
`--tier smt-only`.

**Ask.** Lower differentiable-closed-form grad goals to cvc5 (the derivative of a
rational is a rational, cvc5-expressible), so AD-sensitivity signs can be proven
over the reals rather than sampled.

**Filing condition / tier-upgrade trigger.** When grad goals lower to SMT, the
manifest invariant `econ.inv.gordon_dP_dr_negative_grad.v1` is re-probed
(`run_dischargeability_probes.py --check` flips p05 to FIX), its
`expected_tier_per_pin` is bumped from `fuzz_validated` to `proven`, and the gate
is retuned -- a de-narrowing event, not a rewrite.
