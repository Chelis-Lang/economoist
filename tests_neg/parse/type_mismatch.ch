module Economoist.Tests.Neg.TypeMismatch
import Std.Test (assert_close)
-- Bare negative file: the body binds a bool (a comparison result) and hands it
-- to assert_close, which takes f32 arguments. There is deliberately no test_*
-- declaration: the native expected-failure adapter must preserve the file-level
-- check diagnostic (chelis#967, resolved in 0.17.4).
def negative_type_mismatch() -> unit ! { Test } = {
  bad = (1.0 >= 0.0)
  assert_close(bad, cast(0.0, f32), cast(0.01, f32), "bool is not f32")
}
