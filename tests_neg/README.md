# Negative Tests

Each negative test is a Chelis test function that intentionally triggers
a failure. The suite asserts that each case FAILS with the expected
diagnostic. Run natively by `chelis test tests_neg --expect neg`.

Convention: `tests_neg/<area>/<name>.ch` + paired `.expect` sidecar.
Line 1 of `.expect` = diagnostic substring. Lines 2+ = documentation.
Files may use a `test_negative_*` function or deliberately contain only a bare
file-level check failure. Chelis 0.17.4 preserves either form as an expected
failure outcome (chelis#967). A clean file with neither a diagnostic nor a
`test_*` record is a configuration error, so the suite remains fail-closed.
