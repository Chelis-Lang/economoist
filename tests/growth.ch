module Economoist.Tests.Growth
import Std.Test (assert_close)
import Economoist.Growth (gordon_pv)
-- Concrete-instance test of the Gordon present value against a hand-computed
-- expected value. With D = 2, r = 0.1, g = 0.05 the denominator r - g = 0.05 and
-- P = D / (r - g) = 2 / 0.05 = 40. This exercises the f32 evaluation of the
-- shipped gordon_pv expression; it is a runtime check, separate from the
-- real-arithmetic SMT greens in properties/growth.ch.
def test_gordon_pv_concrete() -> unit ! { Test } = {
  px = gordon_pv(cast(2.0, f32), cast(0.1, f32), cast(0.05, f32))
  assert_close(px, cast(40.0, f32), cast(0.001, f32), "P = D/(r-g) = 2/0.05 = 40")
}
-- A second instance with a different growth rate. With D = 1, r = 0.08, g = 0.03
-- the denominator is 0.05 and P = 1 / 0.05 = 20.
def test_gordon_pv_growth() -> unit ! { Test } = {
  px = gordon_pv(cast(1.0, f32), cast(0.08, f32), cast(0.03, f32))
  assert_close(px, cast(20.0, f32), cast(0.001, f32), "P = 1/0.05 = 20")
}
