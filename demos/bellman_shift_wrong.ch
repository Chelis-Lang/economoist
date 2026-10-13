module Economoist.Demos.Bellman_shift_wrong
import Economoist.Bellman (bellman_state0)
-- Dropping row normalization breaks the constant-shift identity. The
-- controlled claim restores stochastic rows. Both goals call the export.
@property bellman_shift_without_rows_wrong forall(v0: f32, v1: f32, r0: f32, p00: f32, p01: f32, r1: f32, p10: f32, p11: f32, g: f32, c: f32) where p00 >= 0.0, p01 >= 0.0, p10 >= 0.0, p11 >= 0.0, g > 0.0, g < 1.0, c > 0.0:
  (bellman_state0((v0 + c), (v1 + c), r0, p00, p01, r1, p10, p11, g) == (bellman_state0(v0, v1, r0, p00, p01, r1, p10, p11, g) + (g * c)))
@property bellman_shift_with_rows_control forall(v0: f32, v1: f32, r0: f32, p00: f32, p01: f32, r1: f32, p10: f32, p11: f32, g: f32, c: f32) where p00 >= 0.0, p01 >= 0.0, p10 >= 0.0, p11 >= 0.0, (p00 + p01) == 1.0, (p10 + p11) == 1.0, g > 0.0, g < 1.0, c > 0.0:
  (bellman_state0((v0 + c), (v1 + c), r0, p00, p01, r1, p10, p11, g) == (bellman_state0(v0, v1, r0, p00, p01, r1, p10, p11, g) + (g * c)))
