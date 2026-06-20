module Economoist.Tests.ImportSurface
import Std.Test (assert_close)
import Economoist.Markov (eps, make_dist, advance, next_mass)
import Economoist.Bellman (bellman_state0, fmax, fabs)
import Economoist.Growth (gordon_pv)
-- Smoke test for the frozen C Note import surface (docs/cnote-import-surface.json).
-- Every published symbol is imported and exercised, so the surface resolves under
-- the pinned binary. The opaque Dist2 is held only through make_dist and advance.
def test_scalar_surface_resolves() -> unit ! { Test } = {
  e = eps()
  nm = next_mass(cast(0.6, f32), cast(0.4, f32), cast(0.7, f32), cast(0.2, f32))
  bs = bellman_state0(cast(1.0, f32), cast(2.0, f32), cast(0.5, f32), cast(0.7, f32), cast(0.3, f32), cast(0.4, f32), cast(0.2, f32), cast(0.8, f32), cast(0.9, f32))
  gp = gordon_pv(cast(2.0, f32), cast(0.1, f32), cast(0.05, f32))
  mx = fmax(nm, gp)
  ab = fabs(bs)
  total = add(add(add(e, mx), ab), nm)
  assert_close(total, add(add(add(cast(0.0001, f32), cast(40.0, f32)), cast(2.02, f32)), cast(0.5, f32)), cast(0.01, f32), "scalar surface resolves and composes")
}
def test_producer_surface_resolves() -> unit ! { Test } = {
  built = match make_dist(cast(0.6, f32), cast(0.4, f32)) with {
    | Some(d) => match advance(d, cast(0.7, f32), cast(0.3, f32), cast(0.2, f32), cast(0.8, f32)) with {
    | Some(_) => cast(1.0, f32)
    | None => cast(0.0, f32)
  }
    | None => cast(0.0, f32)
  }
  assert_close(built, cast(1.0, f32), cast(0.0001, f32), "make_dist then advance resolve and produce a distribution")
}
