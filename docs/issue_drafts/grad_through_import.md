# Draft: grad does not lower through a cross-module import call

Resolved by economoist#13 at the pinned Chelis 0.17.1 release.

**Summary.** `grad(fn (...) -> imported_fn(...), wrt=...)` inside a `@property`
goal does not make progress when `imported_fn` is a function imported from another
module of the same package: `chelis prove` hangs (no verdict, no error) rather
than either lowering the AD transform or reporting `unsupported`. The identical
grad expression with the callee's body INLINED lowers and fuzz-validates in well
under a second per sample.

**Impact on downstream shells.** Economoist's sampled AD-sensitivity lane
(`sampled/growth_sensitivity.ch`, `gordon_dP_dr_negative_grad`) wants to
differentiate the exported `Economoist.Growth.gordon_pv`. Because grad-through-
import hangs, the property inlines gordon_pv's shipped single-expression body
`(d / (r - g))` instead (single-expression discipline; the body is textually the
export). The manifest marks the binding `references_output_fn: "equivalent-form"`
and cites this draft, per the anti-vacuity contract clause that permits the
equivalent form only with a probe citation showing the direct form does not
discharge. The oracle harness pins the inline body against gordon_pv's numeric
goldens so the equivalent form cannot drift from the export.

**Reproducer (chelis 0.14.0, release binary).** In a package with an exported
`gordon_pv(d, r, g) = d / (r - g)`, prove:

```
@property gd forall(d: f32, r: f32, g: f32) where (d > 0.5), (r > g), (r < 9.5):
  (grad(fn (dd: f32, rr: f32, gg: f32) -> gordon_pv(dd, rr, gg), wrt=rr)(d, r, g) < 0.0)
```

`chelis prove ... --tier fuzz-only --samples 50` does not return within 60s. The
same goal with `gordon_pv(dd, rr, gg)` replaced by the inline body
`(dd / (rr - gg))` returns `passed`/`fuzz` in well under a second.

**Ask.** Either lower grad through cross-module import calls, or report
`unsupported`/`error` promptly instead of hanging, so a downstream AD invariant
can reference the exported function directly (or fail fast and cite it).

**Resolution.** A 0.17.1 two-module re-probe returned promptly with a fuzz
verdict and a compiler-emitted goal containing the imported function. The
sampled Gordon property now imports and differentiates
`Economoist.Growth.gordon_pv` directly. Its satisfying and corrupt sign twin
use that direct binding. Package-scale latency remains separately tracked by
chelis#924; scalar-grad SMT remains separately tracked by chelis#923.
