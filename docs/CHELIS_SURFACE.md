<!-- BEGIN CHELIS MANAGED BLOCK: chelis-surface-header chelis@0.18.12 (sha256:28011bed9ccb5778) -->
This file is a domain-scoped view of the canonical Chelis capability surface,
generated for the pinned toolchain. Each capability row is marked `@pin` (usable
at the current pin) or `@upstream` (lands at the next bump). **Read it before
designing around a suspected language gap** — most downstream over-narrowing
traces to not knowing the real surface. Regenerate with `chelis reef conform
sync` at every pin bump; the upstream source of truth is `docs/CHELIS_SURFACE.md`
in `Chelis-Lang/chelis`.
<!-- END CHELIS MANAGED BLOCK: chelis-surface-header -->

# Chelis capability surface for Economoist

> **Pinned compiler:** 0.18.12 · **Bundled chelis-std:** 0.4.0 ·
> **Latest published compiler:** 0.18.12 · **Checked:** 2026-10-01

`@pin` means the released toolchain supports the capability used here.
`@upstream` is reserved for a capability expected at the next pin; none is
currently claimed. [`docs/UPSTREAM_BUGS.md`](UPSTREAM_BUGS.md) tracks open and
parked gaps.

## Proof and model binding

| Capability | Status | Economoist use and limit |
|---|---|---|
| SMT proof with cvc5 | `@pin` | `chelis prove --json --tier smt-only` checks the scalar `properties/` goals over the reals. The gate requires `status:"passed"`, `proof_tier:"smt"`, `arith_model:"real"`, zero samples, and no contract qualifier. This says nothing about `f32` rounding. |
| Guard and model checks | `@pin` | The gate checks positive `properties/` goals for unqualified SMT results and checks their declared guard-satisfiability witnesses for refutation. The manifest's `properties/` invariants also require an exact property-to-export edge in a complete linker-owned `dependency_graph` and a verdict change under corrupt model substitution. Other `properties/` goals do not receive that substitution check. |
| `@property forall ... where ...` | `@pin` | The written guards bound each statement. Operator-form scalar arithmetic and comparisons lower to SMT. The package does not claim tensor-valued proof goals. |
| `@opaque` with `@invariant` | `@pin` | `Dist2` and `Dist3` producers carry checked distribution obligations. Their tolerance-bearing type invariant is distinct from the exact-sum Markov properties. |
| Package imports in `prove` and `eval --file` | `@pin` | Properties and numeric probes reach the exported functions in the current Reef package. |
| Two-call comparisons and three-coordinate maximum | `@pin` | The Bellman goals compare two calls of the same exported operator. Each two- or three-state output has upper and lower one-step contraction goals. The paired false controls refute. |

## Numeric and language surface

| Capability | Status | Economoist use and limit |
|---|---|---|
| Scalar `f32` arithmetic and comparisons | `@pin` | Model code uses `+`, `-`, `*`, `/`, and comparisons. SMT treats the property expressions as real arithmetic; tests and `eval` exercise concrete `f32` values separately. |
| `if/then/else`, scalar `max`, `min`, `abs` | `@pin` | Bellman uses exported `fmax`, `fmax3`, and `fabs` helpers whose ITE bodies are part of its stable API and checked goal shape. |
| `Option[T]`, `Some`, `None`, `match` | `@pin` | Guarded distribution producers return `None` for invalid transitions. |
| `Std.Test` and `assert_close` | `@pin` | `tests/` exercises concrete model values. The negative test checks a bool passed to the floating-point assertion family is rejected. |
| Rank and dimension handling | `@pin` | This package uses fixed two- and three-state models with scalar parameters. Chelis does not implicitly broadcast; shape changes require explicit operations. No general-state-count proof is claimed. |

## Automatic differentiation

| Capability | Status | Economoist use and limit |
|---|---|---|
| Reverse-mode `grad` | `@pin` | `sampled/growth_sensitivity.ch` differentiates the imported `gordon_pv` export with respect to `r`. The concrete `f32` AD result is fuzz-validated, separate from the real-arithmetic two-point SMT comparison. |
| Scalar gradient in SMT | `@pin` | Supported scalar gradients can lower to SMT. Economoist keeps its sampled result because that record characterizes concrete AD behavior. |
| Compiler-owned dependency graph | `@pin` | `scripts/prove_gate.py` requires the exact declaration edge from each direct property to its exported function; it never treats a goal string as ownership evidence. |
| Larger-state bound propagation | no claim | Beacon's current scalar input-box surface does not certify the larger economic state-space models; see chelis#2830 and beacon#52 in [`UPSTREAM_BUGS.md`](UPSTREAM_BUGS.md). |

## Read more

- [Model guide](SUMMARY.md) — the checked claims and their one-step,
  fixed-dimension, and real-arithmetic limits.
- [`scripts/prove_gate.py`](../scripts/prove_gate.py) — exact proof verdict and
  model-dependency checks.
- [`scripts/oracle_harness.py`](../scripts/oracle_harness.py) — concrete value checks.
- [`docs/cnote-import-surface.json`](cnote-import-surface.json) — stable C Note
  model and invariant IDs, expected verdicts, and controls.
- Chelis `spec/04-type-system.md` §§2.5 and 4.2 — opaque invariants and explicit
  shape handling; `spec/06-transformations.md` §2 — reverse-mode AD;
  `spec/design/chelis_property_spec.md` — proof reporting and induction scope;
  `spec/design/shell_repo_contract.md` §§3–5 — downstream surface, issue, and
  probe requirements.
