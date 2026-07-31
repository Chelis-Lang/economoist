# Draft: grad-based sensitivity goals do not lower to the SMT tier

Filed as chelis#923 and released in Chelis 0.17.2.
The official Economoist 0.17.4 compatibility-asset probe returns the expected
direct-import verdict through the shipped SMT-enabled binary.

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

**Pre-release resolution.** Chelis#923 adds fail-closed Tier-B lowering for the supported
single-target scalar gradient and compiler/backend parity tests. Economoist
keeps `econ.inv.gordon_dP_dr_negative_grad.v1` in the sampled lane by design:
that lane checks the concrete `f32` AD transform, whereas
`gordon_decreasing_in_r` already states the real-arithmetic theorem in the
unqualified SMT-green lane. This is a semantic lane split, not a reason to
promote the concrete `f32` sampled record. The published-release re-probe
passed, so this file is retained only as the historical issue record.
