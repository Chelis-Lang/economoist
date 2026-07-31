# Blocked Probes

Minimal reproducers of open upstream Chelis gaps, plus explicitly labeled
expected-failure adapter regression sentinels. Each file is EXPECTED TO FAIL
at the current pin and is run by `chelis test tests_blocked --expect blocked`
(CI and pin-bump checklist). A regression sentinel locks the adapter contract;
it is not evidence that its cited language issue remains open.

Convention: `tests_blocked/<area>/<name>.ch` + paired `.expect` sidecar. Line 1
of `.expect` is the diagnostic substring the failure must contain. Lines 2+
carry the upstream issue citation and de-narrowing instructions. The native
adapter classifies a pass as FIX-detected and a changed diagnostic as DRIFTED.

## Probe inventory

| Probe | Purpose | Pinned diagnostic |
|---|---|---|
| `adapter/file_level_diagnostic.ch` | Chelis#967 regression sentinel for the native blocked adapter; not a currently blocked language capability. | `precision mismatch: expected f32, got bool` |

A probe must be canonically formatted: the native worker enforces the same
compiler and style contracts as an ordinary test file.

## Cannot be probed (binary-level or absence-of-syntax)

Some blockers cannot be expressed as a `.ch` file that `chelis check` can
probe. These stay on the manual re-probe list in `docs/UPSTREAM_BUGS.md`:

- **SMT prove was absent from the released chelis tarball. RESOLVED (chelis
  v0.11.0).** A binary-level feature gate that no `.ch` file `chelis check`
  reads could exercise. SMT now ships in the released binary; verified at the
  0.14.0 pin by `scripts/prove_gate.py` running green on the release binary.
  Archived in `docs/UPSTREAM_BUGS.md`.
- **eval does not resolve imports for standalone files.** An `eval`-side
  resolution gap that `chelis check` does not exercise; `check` and `prove`
  resolve imports, so no single `check`-rejected file pins it. Re-probed by
  the oracle harness inlining single-expression bodies.
