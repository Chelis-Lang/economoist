# Negative tests

Each `.ch` file must fail with the diagnostic substring on the first line of
its paired `.expect`. Run `chelis test tests_neg --expect neg`.

`parse/type_mismatch.ch` passes a bool to the floating-point `assert_close`
family. It has no `test_*` declaration, so it also checks that the adapter
reports a file-level checker diagnostic. A clean file with no test record is a
configuration error.
