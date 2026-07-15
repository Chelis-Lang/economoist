# Draft: ship the SMT feature in the released chelis tarball

Filed upstream as chelis#422 on 2026-06-20.

**RESOLVED (chelis v0.11.0).** SMT ships in the released chelis tarball as of
v0.11.0; re-verified at the pinned 0.14.0 release binary on 2026-07-10
(`scripts/prove_gate.py` fully green -- every property `proof_tier: smt`,
`samples: 0`). Archived in `docs/UPSTREAM_BUGS.md`; economoist's prove gate
runs on the release binary, and `scripts/build_chelis_smt.py` was removed.
(The prove gate itself later moved off the per-PR `ci.yml` path onto the
`nightly.yml` schedule -- a lean-CI split, tracked separately from this
resolved release-binary issue.)

**Summary.** `chelis prove` reaches the SMT tier only when the binary is built
with `--features smt` (linked against cvc5). The released `chelis-vX.Y.Z` tarball
is built without the feature, so `prove` silently degrades an SMT-amenable goal to
a fuzz-sampled pass.

**Impact on downstream shells.** A shell whose entire value is unqualified SMT
greens (Economoist) cannot consume the released tarball for its proof gate; it
must build the compiler from source, which needs cmake, g++, and libclang. The
silent degrade is the same failure that turned a downstream square amber.

**Reproducer.** With the released tarball, run `chelis prove` on a real-over-reals
inequality such as `@property nn forall(x: f32): (x * x) >= 0.0` and observe
`proof_tier:"fuzz"` rather than `"smt"`.

**Ask.** Publish an SMT-enabled artifact (or document that the standard tarball is
fuzz-only and point to a from-source build), so downstream prove gates can pin a
binary without a local cvc5 toolchain.

**Filing condition.** The released tarball still lacks the `smt` feature at the
next release.
