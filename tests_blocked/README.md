# Blocked probes

There is no open, expressible Chelis blocker at the current pin, so this
directory has no `.ch` probe. `scripts/run_local_gate.py` skips the empty blocked
suite. The active issue inventory is [`docs/UPSTREAM_BUGS.md`](../docs/UPSTREAM_BUGS.md).

When an open blocker has a file-level reproducer, add an isolated
`tests_blocked/<area>/<name>.ch` and `.expect`. The sidecar's first line is the
diagnostic measured on the pinned release; later lines give the live issue
number and the action to take if the probe starts passing. Run
`chelis test tests_blocked --expect blocked`. A passing probe must be promoted
to an ordinary regression test when that adds coverage, and its blocker entry
retired.

The resolved file-level adapter behavior is checked by
[`tests_neg/parse/type_mismatch.ch`](../tests_neg/parse/type_mismatch.ch).
