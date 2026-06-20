module Economoist.Properties.Markov
import Economoist.Markov (next_mass, mass3_next)
-- Structural properties of one Markov step, proven at the SMT tier over the
-- reals against the exported next_mass (n = 2) and mass3_next (n = 3) operators.
-- These are single-application facts: they do not assert convergence to a
-- stationary distribution, and they are the n = 2 and n = 3 instances (both
-- shipped), not the general-n theorem. See docs/models/markov.md.
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
-- The same two structural facts at n = 3, against the exported mass3_next
-- operator. Total mass preserved, exactly: for a row-stochastic 3x3 transition
-- applied to a triple summing to one, the three output masses sum to one. This
-- is an exact real-arithmetic identity (no epsilon), distinct from the f32
-- runtime band the Dist3 invariant carries.
@property markov3_mass_preserved forall(p0: f32, p1: f32, p2: f32, t00: f32, t01: f32, t02: f32, t10: f32, t11: f32, t12: f32, t20: f32, t21: f32, t22: f32) where (((p0 + p1) + p2) == 1.0), (((t00 + t01) + t02) == 1.0), (((t10 + t11) + t12) == 1.0), (((t20 + t21) + t22) == 1.0):
  (((mass3_next(p0, p1, p2, t00, t10, t20) + mass3_next(p0, p1, p2, t01, t11, t21)) + mass3_next(p0, p1, p2, t02, t12, t22)) == 1.0)
-- Non-negativity preserved at n = 3. Nonnegative input masses and nonnegative
-- transition entries give nonnegative output masses.
@property markov3_nonneg_preserved forall(p0: f32, p1: f32, p2: f32, t00: f32, t01: f32, t02: f32, t10: f32, t11: f32, t12: f32, t20: f32, t21: f32, t22: f32) where (p0 >= 0.0), (p1 >= 0.0), (p2 >= 0.0), (t00 >= 0.0), (t01 >= 0.0), (t02 >= 0.0), (t10 >= 0.0), (t11 >= 0.0), (t12 >= 0.0), (t20 >= 0.0), (t21 >= 0.0), (t22 >= 0.0):
  (((mass3_next(p0, p1, p2, t00, t10, t20) >= 0.0) && (mass3_next(p0, p1, p2, t01, t11, t21) >= 0.0)) && (mass3_next(p0, p1, p2, t02, t12, t22) >= 0.0))
-- Non-vacuity witnesses for the n = 3 properties. Each asserts false under the
-- same guards and must be refuted at the SMT tier: cvc5 finds a guard-satisfying
-- model, proving the guards are jointly satisfiable and the green is not vacuous.
@property markov3_mass_preserved_guards_satisfiable forall(p0: f32, p1: f32, p2: f32, t00: f32, t01: f32, t02: f32, t10: f32, t11: f32, t12: f32, t20: f32, t21: f32, t22: f32) where (((p0 + p1) + p2) == 1.0), (((t00 + t01) + t02) == 1.0), (((t10 + t11) + t12) == 1.0), (((t20 + t21) + t22) == 1.0):
  false
@property markov3_nonneg_preserved_guards_satisfiable forall(p0: f32, p1: f32, p2: f32, t00: f32, t01: f32, t02: f32, t10: f32, t11: f32, t12: f32, t20: f32, t21: f32, t22: f32) where (p0 >= 0.0), (p1 >= 0.0), (p2 >= 0.0), (t00 >= 0.0), (t01 >= 0.0), (t02 >= 0.0), (t10 >= 0.0), (t11 >= 0.0), (t12 >= 0.0), (t20 >= 0.0), (t21 >= 0.0), (t22 >= 0.0):
  false
