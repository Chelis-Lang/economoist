module Economoist.Tests.Bellman
import Std.Test (assert_close)
import Economoist.Bellman (bellman_state0)
-- Concrete-instance test of one Bellman step at state 0, asserting the numeric
-- operator value against a hand-computed expected value. This is an f32
-- evaluation check, distinct from the real-arithmetic SMT greens in
-- properties/bellman.ch.
-- Action 1 wins. r0 = 1.0, p00 = 0.5, p01 = 0.5; r1 = 2.0, p10 = 0.0,
-- p11 = 1.0; v0 = 10.0, v1 = 20.0, g = 0.9.
--   action 0: 1.0 + 0.9 * (0.5 * 10 + 0.5 * 20) = 1.0 + 0.9 * 15 = 14.5
--   action 1: 2.0 + 0.9 * (0.0 * 10 + 1.0 * 20) = 2.0 + 0.9 * 20 = 20.0
--   max(14.5, 20.0) = 20.0
def test_bellman_action1_wins() -> unit ! { Test } = {
  v = bellman_state0(cast(10.0, f32), cast(20.0, f32), cast(1.0, f32), cast(0.5, f32), cast(0.5, f32), cast(2.0, f32), cast(0.0, f32), cast(1.0, f32), cast(0.9, f32))
  assert_close(v, cast(20.0, f32), cast(0.00001, f32), "T v at state 0 == max(14.5, 20.0) == 20.0")
}
-- Action 0 wins. Same value function and row 0, but r1 = 0.0, p10 = 1.0,
-- p11 = 0.0 so action 1 falls to 0.0 + 0.9 * (1.0 * 10 + 0.0 * 20) = 9.0 and
-- action 0 (14.5) is the max.
def test_bellman_action0_wins() -> unit ! { Test } = {
  v = bellman_state0(cast(10.0, f32), cast(20.0, f32), cast(1.0, f32), cast(0.5, f32), cast(0.5, f32), cast(0.0, f32), cast(1.0, f32), cast(0.0, f32), cast(0.9, f32))
  assert_close(v, cast(14.5, f32), cast(0.00001, f32), "T v at state 0 == max(14.5, 9.0) == 14.5")
}
