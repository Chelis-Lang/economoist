module Economoist.Tests.Growth
import Std.Test (assert_close)
import Economoist.Growth (gordon_pv, gordon_pv_checked, gordon_pv_strict_checked)
-- Concrete-instance test of the Gordon present value against a hand-computed
-- expected value. With D = 2, r = 0.1, g = 0.05 the denominator r - g = 0.05 and
-- P = D / (r - g) = 2 / 0.05 = 40. This exercises the f32 evaluation of the
-- shipped gordon_pv expression; it is a runtime check, separate from the
-- real-arithmetic SMT greens in properties/growth.ch.
def test_gordon_pv_concrete() -> unit ! { Test } = {
  px = gordon_pv(2.0f32, 0.1f32, 0.05f32)
  assert_close(px, 40.0f32, 0.001f32, "P = D/(r-g) = 2/0.05 = 40")
}
-- A second instance with a different growth rate. With D = 1, r = 0.08, g = 0.03
-- the denominator is 0.05 and P = 1 / 0.05 = 20.
def test_gordon_pv_growth() -> unit ! { Test } = {
  px = gordon_pv(1.0f32, 0.08f32, 0.03f32)
  assert_close(px, 20.0f32, 0.001f32, "P = 1/0.05 = 20")
}
-- Domain-checked entry points. Each positive case has its negative twin: the
-- raw exports are total, so the only observable difference is the branch these
-- return, and a regression that drops a guard shows up as Some where None is
-- asserted.
-- Inside r > g the checked value is the same closed form the raw export
-- computes: D = 1, r = 0.08, g = 0.03 gives 1 / 0.05 = 20.
def test_gordon_pv_checked_in_domain() -> unit ! { Test } = {
  px = match gordon_pv_checked(1.0f32, 0.08f32, 0.03f32) with {
    | Some(v) => v
    | None => 0.0f32
  }
  assert_close(px, 20.0f32, 0.001f32, "checked value inside r > g equals the raw closed form")
}
-- r < g. The raw export returns -20.000002, a plausible-looking negative present
-- value; the checked export refuses.
def test_gordon_pv_checked_rejects_r_below_g() -> unit ! { Test } = {
  refused = match gordon_pv_checked(1.0f32, 0.03f32, 0.08f32) with {
    | Some(_) => 0.0f32
    | None => 1.0f32
  }
  assert_close(refused, 1.0f32, 0.0001f32, "r < g is refused, where gordon_pv returns -20.000002")
}
-- r = g. The raw export returns inf.
def test_gordon_pv_checked_rejects_r_equals_g() -> unit ! { Test } = {
  refused = match gordon_pv_checked(1.0f32, 0.05f32, 0.05f32) with {
    | Some(_) => 0.0f32
    | None => 1.0f32
  }
  assert_close(refused, 1.0f32, 0.0001f32, "r = g is refused, where gordon_pv returns inf")
}
-- A NaN rate. This test is what pins the guard's POSITIVE spelling: `r > g` is
-- false for a NaN r, so the guard fails closed. Rewriting it as
-- `if (r <= g) then None else Some(...)` states the same domain and returns
-- Some here, because every ordering comparison against NaN is false. If this
-- test fails, the guard was negated.
def test_gordon_pv_checked_rejects_nan_rate() -> unit ! { Test } = {
  nan = (0.0f32 / 0.0f32)
  refused = match gordon_pv_checked(1.0f32, nan, 0.03f32) with {
    | Some(_) => 0.0f32
    | None => 1.0f32
  }
  assert_close(refused, 1.0f32, 0.0001f32, "a NaN rate is refused; the guard is written positively so it fails closed")
}
-- The strict variant inside its margin-of-safety domain r > g + 0.01: the spread
-- 0.05 clears the one-point margin, so D = 1 gives 20.
def test_gordon_pv_strict_checked_in_domain() -> unit ! { Test } = {
  px = match gordon_pv_strict_checked(1.0f32, 0.08f32, 0.03f32) with {
    | Some(v) => v
    | None => 0.0f32
  }
  assert_close(px, 20.0f32, 0.001f32, "strict checked value inside r > g + 0.01 equals the raw closed form")
}
-- The strict variant's guard is tighter than a positive denominator, and this is
-- the case that separates them: r = 0.055, g = 0.05 has r > g, so gordon_pv
-- returns a finite positive 200, and gordon_pv_checked would accept it -- but the
-- 0.005 spread does not clear the one-point margin, so the strict checked export
-- refuses. A guard that only tested r > g would pass this test wrongly.
def test_gordon_pv_strict_checked_rejects_inside_margin() -> unit ! { Test } = {
  refused = match gordon_pv_strict_checked(1.0f32, 0.055f32, 0.05f32) with {
    | Some(_) => 0.0f32
    | None => 1.0f32
  }
  accepted = match gordon_pv_checked(1.0f32, 0.055f32, 0.05f32) with {
    | Some(v) => v
    | None => 0.0f32
  }
  composed = assert_close(refused, 1.0f32, 0.0001f32, "a positive spread inside the one-point margin is refused by the strict guard")
  assert_close(accepted, 200.0f32, 0.1f32, "the same input is accepted by the r > g guard, so the two domains are genuinely different")
}
