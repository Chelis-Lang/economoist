module Economoist.Tests.Growth
import Std.Test (assert_close, assert_true, assert_false)
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
-- return, and a regression that drops a guard shows up as an admitted input
-- where a refusal is asserted.
-- True when the checked export admits the rates, false when it refuses. The
-- claim under test is which branch came back, so it is folded to a bool and
-- asserted with assert_true/assert_false rather than compared with a
-- tolerance, the same shape tests/markov.ch's pair_admitted uses.
def checked_admitted(d: f32, r: f32, g: f32) -> bool =
  match gordon_pv_checked(d, r, g) with {
    | Some(_) => true
    | None => false
  }
def strict_checked_admitted(d: f32, r: f32, g: f32) -> bool =
  match gordon_pv_strict_checked(d, r, g) with {
    | Some(_) => true
    | None => false
  }
-- Inside r > g the checked value is the same closed form the raw export
-- computes: D = 1, r = 0.08, g = 0.03 gives 1 / 0.05 = 20.
def test_gordon_pv_checked_in_domain() -> unit ! { Test } = {
  px = match gordon_pv_checked(1.0f32, 0.08f32, 0.03f32) with {
    | Some(v) => v
    | None => 0.0f32
  }
  composed = assert_true(checked_admitted(1.0f32, 0.08f32, 0.03f32), "r > g is admitted")
  assert_close(px, 20.0f32, 0.001f32, "checked value inside r > g equals the raw closed form")
}
-- r < g. The raw export returns -20.000002, a plausible-looking negative present
-- value; the checked export refuses.
def test_gordon_pv_checked_rejects_r_below_g() -> unit ! { Test } = assert_false(checked_admitted(1.0f32, 0.03f32, 0.08f32), "r < g is refused, where gordon_pv returns -20.000002")
-- r = g. The raw export returns inf.
def test_gordon_pv_checked_rejects_r_equals_g() -> unit ! { Test } = assert_false(checked_admitted(1.0f32, 0.05f32, 0.05f32), "r = g is refused, where gordon_pv returns inf")
-- A NaN rate. This test is what pins the guard's POSITIVE spelling: `r > g` is
-- false for a NaN r, so the guard fails closed. Rewriting it as
-- `if (r <= g) then None else Some(...)` states the same domain and admits this
-- input, because every ordering comparison against NaN is false. If this test
-- fails, the guard was negated.
def test_gordon_pv_checked_rejects_nan_rate() -> unit ! { Test } = {
  nan = (0.0f32 / 0.0f32)
  assert_false(checked_admitted(1.0f32, nan, 0.03f32), "a NaN rate is refused; the guard is written positively so it fails closed")
}
-- A NaN growth rate, refused by the same mechanism and on the other side of the
-- comparison. The guard covers both rate arguments, not just r.
def test_gordon_pv_checked_rejects_nan_growth() -> unit ! { Test } = {
  nan = (0.0f32 / 0.0f32)
  assert_false(checked_admitted(1.0f32, 0.08f32, nan), "a NaN growth rate is refused")
}
-- The rate guard does NOT inspect the dividend, and this test records that
-- rather than asserting a property the guard does not have. d < 0 satisfies
-- every rate condition, so the checked export admits it and returns a negative
-- present value -- the same -20.000002 the raw export gives. gordon_positive is
-- proven under d > 0.0 as well as r > g, so Some(v) does not imply v > 0.
-- economoist#38 asked for the rate domain; widening these guards to the
-- dividend would be a separate change.
def test_gordon_pv_checked_admits_negative_dividend() -> unit ! { Test } = {
  px = match gordon_pv_checked(-1.0f32, 0.08f32, 0.03f32) with {
    | Some(v) => v
    | None => 0.0f32
  }
  composed = assert_true(checked_admitted(-1.0f32, 0.08f32, 0.03f32), "the rate guard admits a negative dividend; it does not check d")
  assert_close(px, -20.0f32, 0.001f32, "and returns the negative closed form, so Some does not imply a positive value")
}
-- The strict variant inside its margin-of-safety domain r > g + 0.01: the spread
-- 0.05 clears the one-point margin, so D = 1 gives 20.
def test_gordon_pv_strict_checked_in_domain() -> unit ! { Test } = {
  px = match gordon_pv_strict_checked(1.0f32, 0.08f32, 0.03f32) with {
    | Some(v) => v
    | None => 0.0f32
  }
  composed = assert_true(strict_checked_admitted(1.0f32, 0.08f32, 0.03f32), "a spread clearing the margin is admitted")
  assert_close(px, 20.0f32, 0.001f32, "strict checked value inside r > g + 0.01 equals the raw closed form")
}
-- The strict variant's guard is tighter than a positive denominator, and this is
-- the case that separates them: r = 0.055, g = 0.05 has r > g, so gordon_pv
-- returns a finite positive 200.0000457763672, and gordon_pv_checked admits it
-- -- but the 0.005 spread does not clear the one-point margin, so the strict
-- checked export refuses. A guard that only tested r > g would pass this test
-- wrongly.
def test_gordon_pv_strict_checked_rejects_inside_margin() -> unit ! { Test } = {
  accepted = match gordon_pv_checked(1.0f32, 0.055f32, 0.05f32) with {
    | Some(v) => v
    | None => 0.0f32
  }
  refused = assert_false(strict_checked_admitted(1.0f32, 0.055f32, 0.05f32), "a positive spread inside the one-point margin is refused by the strict guard")
  composed = assert_true(checked_admitted(1.0f32, 0.055f32, 0.05f32), "the same input is admitted by the r > g guard, so the two domains are genuinely different")
  assert_close(accepted, 200.0000457763672f32, 0.00001f32, "and the r > g guard returns the exact closed form there; the tolerance is below the 4.6e-5 gap to 200.0, so this pins the value rather than its magnitude")
}
