module Economoist.Tests.Neg.TypeMismatch
import Std.Test (assert_close)
-- Bare negative file: the body binds a bool (a comparison result) and hands it
-- to assert_close, which takes f32 arguments. There is deliberately no test_*
-- declaration: the native expected-failure adapter must preserve the file-level
-- check diagnostic (chelis#967).
def negative_type_mismatch() -> unit ! { Test } = {
  bad = (1.0 >= 0.0)
  assert_close(bad, 0.0f32, 0.01f32, "bool is not f32")
}
