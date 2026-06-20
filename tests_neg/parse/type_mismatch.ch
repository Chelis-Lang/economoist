module Economoist.Tests.Neg.TypeMismatch
import Std.Test (assert_close)
-- Negative test: the body binds a bool (a comparison result) and hands it to
-- assert_close, which takes f32 arguments. The type checker rejects the test at
-- compile time, so the suite fails with a pinned diagnostic rather than passing.
def test_negative_type_mismatch() -> unit ! { Test } = {
  bad = (1.0 >= 0.0)
  assert_close(bad, cast(0.0, f32), cast(0.01, f32), "bool is not f32")
}
