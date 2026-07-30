# Draft: grad prove hangs in package context (independent of imports)

Reclassified under chelis#924. The fix is included in the prepared Chelis
Chelis 0.17.2 release; the 0.17.3 asset-level rerun remains pending.

**Summary.** A `@property` goal containing `grad(...)` over an INLINE closed-form
body (no imports at all) proves fine as a standalone file but HANGS when the same
file is proven inside a package (a directory whose `reef.toml` auto-detects the
file as package source). This is distinct from `grad_through_import.md`: there the
grad differentiates an imported call; here the grad body is already inlined and
imports nothing, yet in-package proving still does not terminate. The trigger is
package auto-detection changing the prove pipeline, not import resolution.

**Impact on downstream shells.** Economoist's sampled AD lane
(`sampled/growth_sensitivity.ch`) inlines gordon_pv's shipped body specifically
to avoid the grad-through-import hang, and is listed in `reef.toml`
`additional_sources`. Even so, `chelis prove sampled/growth_sensitivity.ch` from
the repo root (package context) does not terminate. The keystone gate
(`scripts/prove_gate.py`) therefore proves the sampled lane by COPYING each file
to a scratch dir OUTSIDE the repo and proving it standalone -- the same
"copy-out" pattern the dischargeability probe runner uses for the same reason.

**Reproducer (chelis 0.14.0, release binary).** With
`sampled/growth_sensitivity.ch` containing an inline-body grad property
(`grad(fn (dd, rr, gg) -> (dd / (rr - gg)), wrt=rr)(d, r, g) < 0.0`) and `sampled`
in `reef.toml` `additional_sources`:

```
# standalone (copied to a scratch dir with no reef.toml): returns
$CHELIS prove /tmp/scratch/growth_sensitivity.ch --json --tier fuzz-only --samples 20 --seed 0
#   -> completes in ~5s

# in-package (proven from the repo root): hangs
$CHELIS prove sampled/growth_sensitivity.ch --json --tier fuzz-only --samples 20 --seed 0
#   -> no output; killed by `timeout 30` (exit 124)
```

Same file, same command, same sample count: standalone returns in ~5s, in-package
does not return in 30s.

**Ask.** Make in-package grad proving terminate (or report `unsupported`/`error`
promptly) so a package-resident AD lane can be gated in place, without the
copy-out workaround.

**Current status.** `scripts/prove_gate.py` now proves the checked-in sampled
file in its actual Reef package context. It no longer copies source to a
standalone temporary directory, so package/linker behavior is part of the
acceptance surface. Chelis#924's development fix removes the fixed preparation
cost, but this draft remains tracking evidence until the published release
passes the cold/warm oracle.
