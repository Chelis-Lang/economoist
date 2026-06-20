module Economoist.Properties.Markov
import Economoist.Markov (next_mass)
-- Structural properties of one Markov step, proven at the SMT tier over the
-- reals against the exported next_mass operator. These are single-application
-- facts: they do not assert convergence to a stationary distribution, and they
-- are the n = 2 instance, not the general-n theorem. See docs/models/markov.md.
-- Total mass preserved, exactly. For a row-stochastic transition applied to a
-- distribution summing to one, the output masses sum to one. This is an exact
-- real-arithmetic identity (no epsilon), distinct from the f32 runtime band the
-- Dist2 invariant carries.
@property markov_mass_preserved forall(p0: f32, p1: f32, t00: f32, t01: f32, t10: f32, t11: f32) where ((p0 + p1) == 1.0), ((t00 + t01) == 1.0), ((t10 + t11) == 1.0):
  ((next_mass(p0, p1, t00, t10) + next_mass(p0, p1, t01, t11)) == 1.0)
-- Non-negativity preserved. Nonnegative input masses and nonnegative transition
-- entries give nonnegative output masses.
@property markov_nonneg_preserved forall(p0: f32, p1: f32, t00: f32, t01: f32, t10: f32, t11: f32) where (p0 >= 0.0), (p1 >= 0.0), (t00 >= 0.0), (t01 >= 0.0), (t10 >= 0.0), (t11 >= 0.0):
  ((next_mass(p0, p1, t00, t10) >= 0.0) && (next_mass(p0, p1, t01, t11) >= 0.0))
-- Non-vacuity witnesses. Each asserts false under the same guards as the
-- property above and must be refuted at the SMT tier: cvc5 finds a
-- guard-satisfying model, proving the guards are jointly satisfiable and the
-- green above is not vacuous.
@property markov_mass_preserved_guards_satisfiable forall(p0: f32, p1: f32, t00: f32, t01: f32, t10: f32, t11: f32) where ((p0 + p1) == 1.0), ((t00 + t01) == 1.0), ((t10 + t11) == 1.0):
  false
@property markov_nonneg_preserved_guards_satisfiable forall(p0: f32, p1: f32, t00: f32, t01: f32, t10: f32, t11: f32) where (p0 >= 0.0), (p1 >= 0.0), (t00 >= 0.0), (t01 >= 0.0), (t10 >= 0.0), (t11 >= 0.0):
  false
