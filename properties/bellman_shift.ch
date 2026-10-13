module Economoist.Properties.Bellman_shift
import Economoist.Bellman (bellman_state0, bellman_state1, bellman_state0_n3, bellman_state1_n3, bellman_state2_n3)
-- For stochastic action rows and 0 <= g < 1, adding c to every input
-- value adds exactly g*c to each exported one-step Bellman output.
-- These are exact-real SMT claims about the imported function bodies, not
-- guarantees about rounded f32 evaluation.
@property bellman_shift_state0 forall(v0: f32, v1: f32, r0: f32, p00: f32, p01: f32, r1: f32, p10: f32, p11: f32, g: f32, c: f32) where p00 >= 0.0, p01 >= 0.0, (p00 + p01) == 1.0, p10 >= 0.0, p11 >= 0.0, (p10 + p11) == 1.0, g >= 0.0, g < 1.0:
  (bellman_state0((v0 + c), (v1 + c), r0, p00, p01, r1, p10, p11, g) == (bellman_state0(v0, v1, r0, p00, p01, r1, p10, p11, g) + (g * c)))
@property bellman_shift_state0_guards_satisfiable forall(v0: f32, v1: f32, r0: f32, p00: f32, p01: f32, r1: f32, p10: f32, p11: f32, g: f32, c: f32) where p00 >= 0.0, p01 >= 0.0, (p00 + p01) == 1.0, p10 >= 0.0, p11 >= 0.0, (p10 + p11) == 1.0, g >= 0.0, g < 1.0:
  false
@property bellman_shift_state1 forall(v0: f32, v1: f32, rr0: f32, q00: f32, q01: f32, rr1: f32, q10: f32, q11: f32, g: f32, c: f32) where q00 >= 0.0, q01 >= 0.0, (q00 + q01) == 1.0, q10 >= 0.0, q11 >= 0.0, (q10 + q11) == 1.0, g >= 0.0, g < 1.0:
  (bellman_state1((v0 + c), (v1 + c), rr0, q00, q01, rr1, q10, q11, g) == (bellman_state1(v0, v1, rr0, q00, q01, rr1, q10, q11, g) + (g * c)))
@property bellman_shift_state1_guards_satisfiable forall(v0: f32, v1: f32, rr0: f32, q00: f32, q01: f32, rr1: f32, q10: f32, q11: f32, g: f32, c: f32) where q00 >= 0.0, q01 >= 0.0, (q00 + q01) == 1.0, q10 >= 0.0, q11 >= 0.0, (q10 + q11) == 1.0, g >= 0.0, g < 1.0:
  false
@property bellman_shift_state0_n3 forall(v0: f32, v1: f32, v2: f32, r0: f32, p00: f32, p01: f32, p02: f32, r1: f32, p10: f32, p11: f32, p12: f32, g: f32, c: f32) where p00 >= 0.0, p01 >= 0.0, p02 >= 0.0, ((p00 + p01) + p02) == 1.0, p10 >= 0.0, p11 >= 0.0, p12 >= 0.0, ((p10 + p11) + p12) == 1.0, g >= 0.0, g < 1.0:
  (bellman_state0_n3((v0 + c), (v1 + c), (v2 + c), r0, p00, p01, p02, r1, p10, p11, p12, g) == (bellman_state0_n3(v0, v1, v2, r0, p00, p01, p02, r1, p10, p11, p12, g) + (g * c)))
@property bellman_shift_state0_n3_guards_satisfiable forall(v0: f32, v1: f32, v2: f32, r0: f32, p00: f32, p01: f32, p02: f32, r1: f32, p10: f32, p11: f32, p12: f32, g: f32, c: f32) where p00 >= 0.0, p01 >= 0.0, p02 >= 0.0, ((p00 + p01) + p02) == 1.0, p10 >= 0.0, p11 >= 0.0, p12 >= 0.0, ((p10 + p11) + p12) == 1.0, g >= 0.0, g < 1.0:
  false
@property bellman_shift_state1_n3 forall(v0: f32, v1: f32, v2: f32, rr0: f32, q00: f32, q01: f32, q02: f32, rr1: f32, q10: f32, q11: f32, q12: f32, g: f32, c: f32) where q00 >= 0.0, q01 >= 0.0, q02 >= 0.0, ((q00 + q01) + q02) == 1.0, q10 >= 0.0, q11 >= 0.0, q12 >= 0.0, ((q10 + q11) + q12) == 1.0, g >= 0.0, g < 1.0:
  (bellman_state1_n3((v0 + c), (v1 + c), (v2 + c), rr0, q00, q01, q02, rr1, q10, q11, q12, g) == (bellman_state1_n3(v0, v1, v2, rr0, q00, q01, q02, rr1, q10, q11, q12, g) + (g * c)))
@property bellman_shift_state1_n3_guards_satisfiable forall(v0: f32, v1: f32, v2: f32, rr0: f32, q00: f32, q01: f32, q02: f32, rr1: f32, q10: f32, q11: f32, q12: f32, g: f32, c: f32) where q00 >= 0.0, q01 >= 0.0, q02 >= 0.0, ((q00 + q01) + q02) == 1.0, q10 >= 0.0, q11 >= 0.0, q12 >= 0.0, ((q10 + q11) + q12) == 1.0, g >= 0.0, g < 1.0:
  false
@property bellman_shift_state2_n3 forall(v0: f32, v1: f32, v2: f32, rs0: f32, s00: f32, s01: f32, s02: f32, rs1: f32, s10: f32, s11: f32, s12: f32, g: f32, c: f32) where s00 >= 0.0, s01 >= 0.0, s02 >= 0.0, ((s00 + s01) + s02) == 1.0, s10 >= 0.0, s11 >= 0.0, s12 >= 0.0, ((s10 + s11) + s12) == 1.0, g >= 0.0, g < 1.0:
  (bellman_state2_n3((v0 + c), (v1 + c), (v2 + c), rs0, s00, s01, s02, rs1, s10, s11, s12, g) == (bellman_state2_n3(v0, v1, v2, rs0, s00, s01, s02, rs1, s10, s11, s12, g) + (g * c)))
@property bellman_shift_state2_n3_guards_satisfiable forall(v0: f32, v1: f32, v2: f32, rs0: f32, s00: f32, s01: f32, s02: f32, rs1: f32, s10: f32, s11: f32, s12: f32, g: f32, c: f32) where s00 >= 0.0, s01 >= 0.0, s02 >= 0.0, ((s00 + s01) + s02) == 1.0, s10 >= 0.0, s11 >= 0.0, s12 >= 0.0, ((s10 + s11) + s12) == 1.0, g >= 0.0, g < 1.0:
  false
