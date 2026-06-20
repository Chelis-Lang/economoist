# Negative Tests

Each negative test is a Chelis test function that intentionally triggers
a failure. The suite asserts that each case FAILS with the expected
diagnostic. Run by `python3 scripts/run_negative_tests.py`.

Convention: `tests_neg/<area>/<name>.ch` + paired `.expect` sidecar.
Line 1 of `.expect` = diagnostic substring. Lines 2+ = documentation.
Function names MUST start with `test_negative_` so a misplaced positive
test surfaces as a config error.

The runner issues `chelis test <file> --json` and asserts fail-with-substring.
