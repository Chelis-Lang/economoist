# Blocked Probes

Minimal reproducers of open upstream chelis bugs or capability gaps that
block Economoist. Each probe is EXPECTED TO FAIL at the current pin. Run by
`python3 scripts/run_blocked_probes.py` (CI and pin-bump checklist).

Convention: `tests_blocked/<area>/<name>.ch` + paired `.expect` sidecar.
The runner copies each source to a temporary standalone directory and runs
`chelis check` on it. Line 1 of `.expect` = diagnostic substring the
failure must contain. Lines 2+ = upstream citation + de-narrowing
instructions.

## Probe inventory

| Probe | Blocker | Pinned diagnostic |
|---|---|---|
| `numerics/scalar_max.ch` | No bound scalar `max`/`min`/`abs` for `f32` at 0.8.0 (a bare `max` over `f32` is an unbound variable). Cited as `docs/issue_drafts/scalar_max_abs_f32.md`, to become `chelis#NNN` once filed; tracked in `docs/UPSTREAM_BUGS.md`. | `unbound variable: max` |

A probe must be canonically formatted: `chelis check` enforces the format
gate before name resolution, so an unformatted file fails on style rather
than on the blocker. Run `chelis fmt --inplace` on a new probe so its
failure pins the intended diagnostic.

## Cannot be probed (binary-level or absence-of-syntax)

Some blockers cannot be expressed as a `.ch` file that `chelis check` can
probe. These stay on the manual re-probe list in `docs/UPSTREAM_BUGS.md`:

- **SMT prove is absent from the released chelis tarball.** A binary-level
  feature gate: whether the `smt` feature is linked is a property of the
  binary, not of any source file, so no `.ch` file `chelis check` reads can
  exercise it. Verified instead by the `smt-prove-gate` building from source.
- **eval does not resolve imports for standalone files.** An `eval`-side
  resolution gap that `chelis check` does not exercise; `check` and `prove`
  resolve imports, so no single `check`-rejected file pins it. Re-probed by
  the oracle harness inlining single-expression bodies.
