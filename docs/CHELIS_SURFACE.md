<!-- BEGIN CHELIS MANAGED BLOCK: chelis-surface-header chelis@0.18.12 (sha256:28011bed9ccb5778) -->
This file is a domain-scoped view of the canonical Chelis capability surface,
generated for the pinned toolchain. Each capability row is marked `@pin` (usable
at the current pin) or `@upstream` (lands at the next bump). **Read it before
designing around a suspected language gap** — most downstream over-narrowing
traces to not knowing the real surface. Regenerate with `chelis reef conform
sync` at every pin bump; the upstream source of truth is `docs/CHELIS_SURFACE.md`
in `Chelis-Lang/chelis`.
<!-- END CHELIS MANAGED BLOCK: chelis-surface-header -->

# Chelis Capability Surface for Economoist

What the Chelis language and the bundled chelis-std actually provide to the
economic-models domain this shell touches. Read this before designing around a
suspected language gap.

> **Pinned candidate:** chelis 0.18.12 (chelis-std 0.4.0, bundled;
> candidate source `8cb4946a365569ceda478f86a7c37baa3fda4082`) ·
> **Latest published upstream:** 0.18.11 ·
> **Last refreshed:** 2026-09-30
>
> **Release identity:** official 0.18.12 asset pending. Capability status at
> this pin is provisional until the published compiler passes the complete gate.

Rows are marked `@pin` (present in the 0.18.12 candidate) or `@upstream`
(expected after it). The final published-asset probe controls these labels.

## Proof surface (the spine of this shell)

| Capability | Status | Notes |
|---|---|---|
| SMT prove tier (cvc5, QF_NRA over the reals) | `@pin` | `chelis prove --json --tier smt-only`. SMT ships in the released chelis binary as of v0.11.0 (chelis#422 resolved, archived in `UPSTREAM_BUGS.md`); no from-source build. The official 0.18.12 asset must be the final gate binary. |
| Green markers | `@pin` | `status:"passed"`, `proof_tier:"smt"`, `samples:0`, `arith_model:"real"`, `composite_verdict:"proven_modulo_real_arithmetic"` (chelis 0.9.0; the prover is honest that it proved the goal over the reals, not the f32 rounding behaviour, which is exactly this shell's boundary). The older plain `"proven"` token is also accepted by the gate. |
| Reals, not floats | `@pin` | A green is a real-arithmetic fact (`arith_model:"real"`), not a statement about `f32` evaluation. Stated per model. |
| Per-property non-vacuity | `@pin` | A guarded property carries a `preconditions` assumption whose non-vacuity cvc5 establishes (a guard-satisfying model). The gate also ships explicit `*_guards_satisfiable` witnesses that refute. |
| Invariant-producer obligations | `@pin` | An `@opaque` type with `@invariant`, plus a `def` returning the type or `Option[T]`, generates an obligation that discharges the invariant at SMT. The carrier for E1 simplex preservation. |
| `@property forall ... where ...` | `@pin` | Operator-form goals (`>=`, `<=`, `&&`, `*`) lower to cvc5. As of chelis 0.9.0 the builtin-call forms (`gte`, `mul`) also lower to SMT (verified `proven_modulo_real_arithmetic`, tier `smt`, samples 0); they were fuzz-only at 0.8.0. The shipped goals stay in operator form for clarity regardless. Params must be scalar (`f32`); tensor params drop to fuzz. |
| prove-side import resolution | `@pin` | `prove` resolves module imports, so a property targets the real exported function. |
| Two-call comparison/subtraction of an ITE-bodied operator at a goal site | `@pin` | A goal that compares or subtracts two calls of the same `if/then/else`-bodied operator def (e.g. `bellman_state0(v...) - bellman_state0(w...)`) now lowers faithfully: true goals prove, false goals refute with a counterexample. The two-call collapse soundness bug (chelis#426) was fixed at chelis 0.10.0 and re-verified at 0.14.0 (probe p04, archived in `UPSTREAM_BUGS.md`); `properties/bellman.ch` calls the exported operators directly at the goal site, and the former `unsound_pattern_lint` was removed. |
| Nested `fmax`-style sup at a goal site (n=3 sup-norm contraction) | `@pin` | The n=3 per-output-state Bellman sup-norm contraction now lowers to SMT: the `fmax3` three-coordinate sup on the right combined with the two-call n=3 operator arithmetic on the left proves (6 greens + 6 refuting witnesses). The nested-fmax lowering gap (chelis#425) was fixed in 0.14.0 (probe p15 + per-surface, archived in `UPSTREAM_BUGS.md`). General-`n` and value-iteration convergence remain held out (need induction). |

## Numeric and language primitives the domain uses

| Family | Status | Notes |
|---|---|---|
| Arithmetic `+ - * /`, comparisons `>= <= > < == !=` | `@pin` | Lower to cvc5. A `/` with a guarded-nonzero denominator now lowers: the Gordon greens call the exported `gordon_pv(d, r, g) = d / (r - g)` directly at the goal site under the `r > g` guard and prove at SMT (probes p01/p02/p03), replacing the earlier multiplied-through polynomial restatements (which were vacuous). |
| `if/then/else` | `@pin` | Lowers as ITE in QF_NRA. |
| Scalar `abs` for `f32` | `@pin` | `abs` binds and proves smt-green (verified at 0.14.0). Exported `fabs` remains stable shell API and preserves the audited ITE proof shape, not a workaround. See archived chelis#424. |
| Scalar `max`/`min` for `f32` | `@pin` | Real-Reef executable probes compile and pass for both scalar `max` and `min`. Exported `fmax`/`fmax3` remain stable shell API and preserve the existing ITE-shaped SMT corpus, not a narrowing. See archived chelis#424. |
| `Option[T]`, `Some`/`None`, `match` | `@pin` | Used by the guarded producers. |
| `@opaque` types with `@invariant` | `@pin` | Field access stays inside the module; values held by consumers only through producers. |
| `cast`, `f32` literals | `@pin` | Test and eval bodies use builtin-call forms freely; only prove goals require operator form. |
| `grad` in `eval` (AD) | `@pin` | E4 comparative statics: the derivative of the displayed `gordon_pv` expression. Single-expression discipline. See the AD row below for mode and lane rules. |
| eval-side package import resolution | `@pin` | `eval --file` resolves imports against the current Reef package even for an ad hoc snippet outside `src/`. Re-probed on the official 0.18.10 binary by importing and evaluating `Economoist.Growth.gordon_pv`; the numeric oracle now calls exported models directly. See archived chelis#423. |
| `Std.Test` (`assert_close`) | `@pin` | The executable numeric suite under `tests/`. |
| Transcendentals (`exp`, `log`, normal CDF) | n/a | Not used. Every economic goal is transcendental-free by construction; if one appears, the model is written wrong. |

## Automatic differentiation and rank (the AD demo surface)

| Capability | Status | Notes |
|---|---|---|
| AD mode (`grad`) | `@pin` | `grad` is **reverse-mode** automatic differentiation, not forward-mode (`spec/06-transformations.md` §2 title and §2.3 "Algorithm: Reverse-Mode AD"). The signature requires a scalar floating result `B` (§2.1: `f : A -> B`, `B` a scalar floating result; `grad(f) : A -> dA`). In `chelis eval` and the Tide host runtime, `grad` is applied by lowering the runtime transform back into the RISC DAG evaluator using the **same reverse-mode rules** as the tensor lane, not a separate host AD engine (§2.10). |
| grad-lane rule for `f32` scalars | `@pin` | The E4 demo differentiates a scalar `f32` lambda (`grad(fn (d,r,g) -> d/(r-g), wrt=r)`); the result is a rank-0 tensor (`tensor(shape=[], data=[...])`). Integer-typed parameters are a hard error (`non_differentiable`, §2.7); the Gordon params are all `f32`, so this never bites. The proven sign is the real-arithmetic fact; the `f32` AD value confirms the sign at a point and is not itself a proof (`docs/models/growth.md` E4). |
| Zero-grad / differentiability lanes | `@pin` | `spec/06-transformations.md` §2.7: `CmpLt` routes **zero gradient** to both inputs (with a compiler warning); `Max(a,b)` is differentiable almost everywhere, the gradient routing to the larger input (subgradient convention, **zero at ties**); `Cast` to integer is zero-gradient. The shipped Gordon body `d/(r-g)` is a smooth rational with no comparison, `max`, or integer cast on the differentiated path, so it has a well-defined nonzero gradient at the demo point. Bellman's `fmax`/`fabs` helpers are not in the AD path. |
| grad goal lowering (tier) | `@pin` | Chelis#923's fail-closed scalar-grad SMT path is present. Economoist still keeps the concrete `f32` AD check `fuzz_validated`, separate from the real-arithmetic two-point green `gordon_decreasing_in_r`. |
| grad through cross-module import | `@pin` | Economoist#13 re-probed a direct imported gradient at 0.17.1: it returned a fuzz verdict whose compiler-emitted goal contained the imported function. The sampled satisfying and corrupt properties now differentiate `Economoist.Growth.gordon_pv` directly. Package-sized fixed cost is separate (chelis#924). |
| compiler-owned dependency attribution | `@pin` | Chelis#922's linker-owned complete/unavailable `dependency_graph` contains both direct property-to-`gordon_pv` edges. `scripts/prove_gate.py` fails closed on a missing edge. |
| persistent package prove context | `@pin` | Chelis#924's integrity-checked prepared Reef graph cache and linker-reachable post-verdict check are present. The sampled gate exercises the real package context. |
| Rank polymorphism (`..r`) | n/a | Not relied on. Chelis verbs are **not** implicitly rank-polymorphic and there is **no implicit broadcasting**: all rank/dimension manipulation is explicit via `expand`/`reshape`/`permute` (`spec/04-type-system.md` §4.2). Optional `..r` rank-variable defs exist as an identity-tier feature (`spec/design/rank_polymorphism.md`, "IDENTITY TIER SHIPPED"), but this shell uses **fixed small dimensions** (n=2 and n=3) with **scalar `f32`** params and never writes a `..r` def, so rank polymorphism has no bearing on the proof or AD surface here. |

## Where to read more

In this shell:

- The prove invocation and the SMT-green gate: `scripts/prove_gate.py`.
- The numeric oracle: `scripts/oracle_harness.py`.
- The frozen C Note surface: `docs/cnote-import-surface.json`.
- Per-model proven-versus-held-out boundaries: `docs/models/`.

In the chelis numbered specs and design docs (paths relative to the chelis
upstream repo). Each topic below is one this shell leans on; the cited
file and section are the authoritative upstream source.

| Topic this shell touches | Upstream spec or design doc | Section |
|---|---|---|
| SMT prove tier, cvc5 lowering, reals (QF_NRA) caveat | `spec/design/chelis_property_spec.md` | `### Tier B SMT proofs are over the reals (caveat)` |
| cvc5-lowerable intrinsics and sort handling (the lowering source of truth) | `spec/design/prove_obligation_unification.md` | `## U3 -- one cvc5-lowerable intrinsic source of truth + sort-mismatch pre-check` |
| `@opaque` types and `@invariant` well-formedness | `spec/04-type-system.md` | `### 2.5 Opaque Types`, `#### 2.5.1 Invariant Declaration Well-Formedness` |
| `@opaque` invariant obligations: producer set and obligation synthesis | `spec/design/opaque_invariants_rfc.md` | `## 8. D-PRODUCER: the producer set (covered-or-rejected)`, `## 9. D-OBLIG: obligation synthesis and output` |
| `@property forall ... where ...` surface and the prove tiers | `spec/design/chelis_property_spec.md` | `## Surf Syntax`, `## CLI Contract` |
| `grad` and automatic differentiation in eval | `spec/06-transformations.md` | `## 2. grad -- Reverse-Mode Automatic Differentiation`, `### 2.7 Non-Differentiable Operations`, `### 2.10 Backend support: tensor lane vs host lane`, `## 7. Formal Semantics of grad` |
| No implicit broadcasting; rank-polymorphism status | `spec/04-type-system.md`, `spec/design/rank_polymorphism.md` | `### 4.2 No Broadcasting`; "IDENTITY TIER SHIPPED" / Implementation Status |
| The chelis-std module surface used (scalar builtins, reductions) | `docs/book/src/stdlib.md` | `## Standard library modules` |
| The downstream shell-repo contract this shell follows | `spec/design/shell_repo_contract.md` | `## 3. Capability surface doc -- docs/CHELIS_SURFACE.md (MUST)` |

The 0.18.12 candidate and its pending release gate are summarized in
[the migration record](chelis-0.18.12-migration.md); the published 0.18.10
record is [kept alongside it](chelis-0.18.10-migration.md). Exact scalar and rank-zero
tensor eval values are decoded from their dtype-tagged bits. The imported
Gordon properties remain unsupported by `--tier beacon-only`; this release
does not promote any economic property to the NN bound lane.
