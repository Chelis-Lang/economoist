module Economoist.Tests.ImportSurface
import Std.Test (assert_close)
import Economoist.Markov (eps, make_dist, make_dist3, advance, advance3, next_mass, mass3_next)
import Economoist.Bellman (bellman_state0, bellman_state1, bellman_state0_n3, bellman_state1_n3, bellman_state2_n3, fmax, fmax3, fabs)
import Economoist.Growth (gordon_pv, gordon_pv_negated)
-- Smoke test for the frozen C Note import surface (docs/cnote-import-surface.json).
-- Every published symbol is imported and exercised, so the surface resolves under
-- the pinned binary. The opaque Dist2/Dist3 are held only through their producers.
def test_scalar_surface_resolves() -> unit ! { Test } = {
  e = eps()
  nm = next_mass(cast(0.6, f32), cast(0.4, f32), cast(0.7, f32), cast(0.2, f32))
  bs = bellman_state0(cast(1.0, f32), cast(2.0, f32), cast(0.5, f32), cast(0.7, f32), cast(0.3, f32), cast(0.4, f32), cast(0.2, f32), cast(0.8, f32), cast(0.9, f32))
  gp = gordon_pv(cast(2.0, f32), cast(0.1, f32), cast(0.05, f32))
  gpn = gordon_pv_negated(cast(2.0, f32), cast(0.1, f32), cast(0.05, f32))
  mx = fmax(nm, gp)
  ab = fabs(bs)
  total = add(add(add(add(e, mx), ab), nm), add(gp, gpn))
  assert_close(total, add(add(add(cast(0.0001, f32), cast(40.0, f32)), cast(2.02, f32)), cast(0.5, f32)), cast(0.01, f32), "scalar surface resolves and composes; gordon_pv + gordon_pv_negated cancel to 0")
}
def test_n3_scalar_surface_resolves() -> unit ! { Test } = {
  z = cast(0.0, f32)
  m3 = mass3_next(cast(0.2, f32), cast(0.3, f32), cast(0.5, f32), cast(0.5, f32), cast(0.25, f32), cast(0.25, f32))
  b1 = bellman_state1(z, z, z, z, z, z, z, z, z)
  b0n3 = bellman_state0_n3(z, z, z, z, z, z, z, z, z, z, z, z)
  b1n3 = bellman_state1_n3(z, z, z, z, z, z, z, z, z, z, z, z)
  b2n3 = bellman_state2_n3(z, z, z, z, z, z, z, z, z, z, z, z)
  mx3 = fmax3(b0n3, b1n3, b2n3)
  total = add(add(add(add(m3, b1), mx3), add(b1n3, b2n3)), b0n3)
  assert_close(total, cast(0.3, f32), cast(0.001, f32), "n=3 surface resolves; mass3_next == 0.3 and zero-state operators == 0")
}
def test_producer_surface_resolves() -> unit ! { Test } = {
  built2 = match make_dist(cast(0.6, f32), cast(0.4, f32)) with {
    | Some(d) => match advance(d, cast(0.7, f32), cast(0.3, f32), cast(0.2, f32), cast(0.8, f32)) with {
    | Some(_) => cast(1.0, f32)
    | None => cast(0.0, f32)
  }
    | None => cast(0.0, f32)
  }
  built3 = match make_dist3(cast(0.2, f32), cast(0.3, f32), cast(0.5, f32)) with {
    | Some(d) => match advance3(d, cast(1.0, f32), cast(0.0, f32), cast(0.0, f32), cast(0.0, f32), cast(1.0, f32), cast(0.0, f32), cast(0.0, f32), cast(0.0, f32), cast(1.0, f32)) with {
    | Some(_) => cast(1.0, f32)
    | None => cast(0.0, f32)
  }
    | None => cast(0.0, f32)
  }
  assert_close(add(built2, built3), cast(2.0, f32), cast(0.0001, f32), "make_dist/advance and make_dist3/advance3 resolve and produce distributions")
}
