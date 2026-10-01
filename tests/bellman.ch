module Economoist.Tests.Bellman
import Std.Test (assert_close)
import Economoist.Bellman (bellman_state0, bellman_state1, bellman_state0_n3, bellman_state1_n3, bellman_state2_n3)
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
  v = bellman_state0(10.0f32, 20.0f32, 1.0f32, 0.5f32, 0.5f32, 2.0f32, 0.0f32, 1.0f32, 0.9f32)
  assert_close(v, 20.0f32, 0.00001f32, "T v at state 0 == max(14.5, 20.0) == 20.0")
}
-- Action 0 wins. Same value function and row 0, but r1 = 0.0, p10 = 1.0,
-- p11 = 0.0 so action 1 falls to 0.0 + 0.9 * (1.0 * 10 + 0.0 * 20) = 9.0 and
-- action 0 (14.5) is the max.
def test_bellman_action0_wins() -> unit ! { Test } = {
  v = bellman_state0(10.0f32, 20.0f32, 1.0f32, 0.5f32, 0.5f32, 0.0f32, 1.0f32, 0.0f32, 0.9f32)
  assert_close(v, 14.5f32, 0.00001f32, "T v at state 0 == max(14.5, 9.0) == 14.5")
}
-- Three-state instance, action 1 wins. v0 = 10.0, v1 = 20.0, v2 = 30.0,
-- g = 0.9. Action 0: r0 = 1.0, row (0.5, 0.25, 0.25); action 1: r1 = 2.0, row
-- (0.0, 0.0, 1.0).
--   action 0: 1.0 + 0.9 * (0.5 * 10 + 0.25 * 20 + 0.25 * 30) = 1.0 + 0.9 * 17.5 = 16.75
--   action 1: 2.0 + 0.9 * (0.0 * 10 + 0.0 * 20 + 1.0 * 30) = 2.0 + 0.9 * 30 = 29.0
--   max(16.75, 29.0) = 29.0
def test_bellman_n3_action1_wins() -> unit ! { Test } = {
  v = bellman_state0_n3(10.0f32, 20.0f32, 30.0f32, 1.0f32, 0.5f32, 0.25f32, 0.25f32, 2.0f32, 0.0f32, 0.0f32, 1.0f32, 0.9f32)
  assert_close(v, 29.0f32, 0.00001f32, "T v at state 0 (n=3) == max(16.75, 29.0) == 29.0")
}
-- Output state 1 (n=2). bellman_state1 is term by term bellman_state0 with the
-- state-1 rewards rr* and rows q*; the same numbers as test_bellman_action1_wins
-- give the same value. rr0 = 1.0, q row (0.5, 0.5); rr1 = 2.0, q row (0.0, 1.0).
--   action 0: 1.0 + 0.9 * (0.5 * 10 + 0.5 * 20) = 14.5
--   action 1: 2.0 + 0.9 * (0.0 * 10 + 1.0 * 20) = 20.0
--   max(14.5, 20.0) = 20.0
def test_bellman_state1_action1_wins() -> unit ! { Test } = {
  v = bellman_state1(10.0f32, 20.0f32, 1.0f32, 0.5f32, 0.5f32, 2.0f32, 0.0f32, 1.0f32, 0.9f32)
  assert_close(v, 20.0f32, 0.00001f32, "T v at state 1 == max(14.5, 20.0) == 20.0")
}
-- Output state 1 (n=3). bellman_state1_n3 with the same numbers as
-- test_bellman_n3_action1_wins. rr0 = 1.0, q row (0.5, 0.25, 0.25); rr1 = 2.0, q
-- row (0.0, 0.0, 1.0). action 0 = 16.75, action 1 = 29.0, max = 29.0.
def test_bellman_state1_n3_action1_wins() -> unit ! { Test } = {
  v = bellman_state1_n3(10.0f32, 20.0f32, 30.0f32, 1.0f32, 0.5f32, 0.25f32, 0.25f32, 2.0f32, 0.0f32, 0.0f32, 1.0f32, 0.9f32)
  assert_close(v, 29.0f32, 0.00001f32, "T v at state 1 (n=3) == max(16.75, 29.0) == 29.0")
}
-- Output state 2 (n=3). bellman_state2_n3 with the same numbers. rs0 = 1.0, s row
-- (0.5, 0.25, 0.25); rs1 = 2.0, s row (0.0, 0.0, 1.0). action 0 = 16.75, action 1
-- = 29.0, max = 29.0.
def test_bellman_state2_n3_action1_wins() -> unit ! { Test } = {
  v = bellman_state2_n3(10.0f32, 20.0f32, 30.0f32, 1.0f32, 0.5f32, 0.25f32, 0.25f32, 2.0f32, 0.0f32, 0.0f32, 1.0f32, 0.9f32)
  assert_close(v, 29.0f32, 0.00001f32, "T v at state 2 (n=3) == max(16.75, 29.0) == 29.0")
}
