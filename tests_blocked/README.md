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

No blocked probes yet. The first upstream blocker that can be expressed as a
standalone `.ch` file `chelis check` rejects populates this directory, with
its pinned diagnostic and `chelis#NNN` citation in the `.expect` sidecar.

## Cannot be probed (binary-level or absence-of-syntax)

Some blockers cannot be expressed as a `.ch` file that `chelis check` can
probe (for example a binary-level feature gate such as the smt proof tier
being absent from the release tarball, verified instead by the
smt-prove-gate building from source, or absence-of-syntax gaps where no
source can exercise the missing construct). Those are tracked in prose
rather than as probes here.
