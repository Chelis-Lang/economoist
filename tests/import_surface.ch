module Economoist.Tests.ImportSurface
import Std.Test (assert_close)
import Economoist.Markov (eps, make_dist, make_dist3, advance, advance3, next_mass, mass3_next)
import Economoist.Bellman (bellman_state0, bellman_state1, bellman_state0_n3, bellman_state1_n3, bellman_state2_n3, fmax, fmax3, fabs)
import Economoist.Growth (gordon_pv, gordon_pv_strict, gordon_pv_negated)
-- Smoke test for the frozen C Note import surface (docs/cnote-import-surface.json).
-- Every published symbol is imported and exercised, so the surface resolves under
-- the pinned binary. The opaque Dist2/Dist3 are held only through their producers.
def test_scalar_surface_resolves() -> unit ! { Test } = {
  e = eps()
  nm = next_mass(0.6f32, 0.4f32, 0.7f32, 0.2f32)
  bs = bellman_state0(1.0f32, 2.0f32, 0.5f32, 0.7f32, 0.3f32, 0.4f32, 0.2f32, 0.8f32, 0.9f32)
  gp = gordon_pv(2.0f32, 0.1f32, 0.05f32)
  gps = gordon_pv_strict(2.0f32, 0.1f32, 0.05f32)
  gpn = gordon_pv_negated(2.0f32, 0.1f32, 0.05f32)
  mx = fmax(nm, gp)
  ab = fabs(bs)
  total = add(add(add(add(e, mx), ab), nm), add(gp, gpn))
  composed = assert_close(total, add(add(add(0.0001f32, 40.0f32), 2.02f32), 0.5f32), 0.01f32, "scalar surface resolves and composes; gordon_pv + gordon_pv_negated cancel to 0")
  assert_close(gps, gp, 0.0001f32, "gordon_pv_strict is numerically identical to gordon_pv (same closed form, tighter stated domain)")
}
def test_n3_scalar_surface_resolves() -> unit ! { Test } = {
  z = 0.0f32
  m3 = mass3_next(0.2f32, 0.3f32, 0.5f32, 0.5f32, 0.25f32, 0.25f32)
  b1 = bellman_state1(z, z, z, z, z, z, z, z, z)
  b0n3 = bellman_state0_n3(z, z, z, z, z, z, z, z, z, z, z, z)
  b1n3 = bellman_state1_n3(z, z, z, z, z, z, z, z, z, z, z, z)
  b2n3 = bellman_state2_n3(z, z, z, z, z, z, z, z, z, z, z, z)
  mx3 = fmax3(b0n3, b1n3, b2n3)
  total = add(add(add(add(m3, b1), mx3), add(b1n3, b2n3)), b0n3)
  assert_close(total, 0.3f32, 0.001f32, "n=3 surface resolves; mass3_next == 0.3 and zero-state operators == 0")
}
def test_producer_surface_resolves() -> unit ! { Test } = {
  built2 = match make_dist(0.6f32, 0.4f32) with {
    | Some(d) => match advance(d, 0.7f32, 0.3f32, 0.2f32, 0.8f32) with {
    | Some(_) => 1.0f32
    | None => 0.0f32
  }
    | None => 0.0f32
  }
  built3 = match make_dist3(0.2f32, 0.3f32, 0.5f32) with {
    | Some(d) => match advance3(d, 1.0f32, 0.0f32, 0.0f32, 0.0f32, 1.0f32, 0.0f32, 0.0f32, 0.0f32, 1.0f32) with {
    | Some(_) => 1.0f32
    | None => 0.0f32
  }
    | None => 0.0f32
  }
  assert_close(add(built2, built3), 2.0f32, 0.0001f32, "make_dist/advance and make_dist3/advance3 resolve and produce distributions")
}
