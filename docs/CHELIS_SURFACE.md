# Chelis Capability Surface for Economoist

What the Chelis language and the bundled chelis-std actually provide to the
economic-models domain this shell touches. Read this before designing around a
suspected language gap.

> **Pinned:** chelis 0.8.0 (chelis-std 0.4.0, bundled) ·
> **Latest upstream:** 0.8.0 · **Last refreshed:** 2026-06-20

Rows are marked `@pin` (usable today at 0.8.0) or `@upstream` (expected at the
next bump). Refresh this table at every pin bump.

## Proof surface (the spine of this shell)

| Capability | Status | Notes |
|---|---|---|
| SMT prove tier (cvc5, QF_NRA over the reals) | `@pin*` | `chelis prove --json --tier smt-only`. *Requires a from-source binary built `cargo build --release -p chelis-cli --features smt` (links cvc5; needs cmake, g++, libclang). The released tarball is fuzz-only and silently degrades; see `UPSTREAM_BUGS.md`. |
| Green markers | `@pin` | `status:"passed"`, `proof_tier:"smt"`, `samples:0`, `arith_model:"real"`, `composite_verdict:"proven"`. |
| Reals, not floats | `@pin` | A green is a real-arithmetic fact (`arith_model:"real"`), not a statement about `f32` evaluation. Stated per model. |
| Per-property non-vacuity | `@pin` | A guarded property carries a `preconditions` assumption whose non-vacuity cvc5 establishes (a guard-satisfying model). The gate also ships explicit `*_guards_satisfiable` witnesses that refute. |
| Invariant-producer obligations | `@pin` | An `@opaque` type with `@invariant`, plus a `def` returning the type or `Option[T]`, generates an obligation that discharges the invariant at SMT. The carrier for E1 simplex preservation. |
| `@property forall ... where ...` | `@pin` | Goals must be operator-form (`>=`, `<=`, `&&`, `*`); builtin-call forms (`gte`, `mul`) do not lower and drop to fuzz. Params must be scalar (`f32`); tensor params drop to fuzz. |
| prove-side import resolution | `@pin` | `prove` resolves module imports, so a property targets the real exported function. |

## Numeric and language primitives the domain uses

| Family | Status | Notes |
|---|---|---|
| Arithmetic `+ - * /`, comparisons `>= <= > < == !=` | `@pin` | Lower to cvc5. Keep `/` out of proof goals; use multiplied-through polynomial form (Gordon). |
| `if/then/else` | `@pin` | Lowers as ITE in QF_NRA. |
| Scalar `max`/`min`/`abs` for `f32` | `@upstream` | No bound scalar builtin exists at 0.8.0; define local `fmax`/`fabs` with `if/then/else` (they lower as ITE and prove smt-green). See `UPSTREAM_BUGS.md`. |
| `Option[T]`, `Some`/`None`, `match` | `@pin` | Used by the guarded producers. |
| `@opaque` types with `@invariant` | `@pin` | Field access stays inside the module; values held by consumers only through producers. |
| `cast`, `f32` literals | `@pin` | Test and eval bodies use builtin-call forms freely; only prove goals require operator form. |
| `grad` in `eval` (AD) | `@pin` | E4 comparative statics: the derivative of the displayed `gordon_pv` expression. Single-expression discipline. |
| eval-side import resolution (standalone files) | `@upstream` | `eval` does not resolve imports for standalone files; a template inlines the single-expression body until this lands. The proof surface is not blocked by this. See `UPSTREAM_BUGS.md`. |
| `Std.Test` (`assert_close`) | `@pin` | The executable numeric suite under `tests/`. |
| Transcendentals (`exp`, `log`, normal CDF) | n/a | Not used. Every economic goal is transcendental-free by construction; if one appears, the model is written wrong. |

## Where to read more

- The prove invocation and the SMT-green gate: `scripts/prove_gate.py`.
- The numeric oracle: `scripts/oracle_harness.py`.
- The frozen C Note surface: `docs/cnote-import-surface.json`.
- Per-model proven-versus-held-out boundaries: `docs/models/`.
