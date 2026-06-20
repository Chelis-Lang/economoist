module Economoist.Markov
export (eps, make_dist, advance, next_mass)
-- Economoist.Markov: a finite-state Markov transition operator over a fixed
-- small state space (n = 2; the n = 3 form is identical entry by entry).
--
-- A distribution on the 2-simplex is a pair of nonnegative masses summing to
-- one. A row-stochastic transition has nonnegative rows that each sum to one.
-- The next distribution is the transition applied to the current one.
--
-- PROVEN here (single application, SMT, transcendental-free, over the reals):
--   advance : applying a row-stochastic transition to a distribution on the
--             simplex yields a distribution on the simplex. The invariant
--             producer obligation proves nonnegativity preserved and total mass
--             preserved together.
-- HELD OUT (see docs/models/markov.md): stationary distribution existence and
--   uniqueness, convergence to stationarity, ergodicity (limit results, need
--   induction); and the general-n theorem (this is the n = 2, n = 3 instance,
--   not the all-n result).
def eps() -> f32 = 0.0001
-- A distribution on the 2-simplex. The invariant carries an f32 epsilon band on
-- the sum: it states the runtime f32 invariant, which is distinct from the exact
-- real-arithmetic mass identity proven by markov_mass_preserved.
@opaque
@invariant(d) ((((d.p0 >= 0.0) && (d.p1 >= 0.0)) && ((d.p0 + d.p1) >= (1.0 - eps))) && ((d.p0 + d.p1) <= (1.0 + eps)))
type Dist2 =
  | Dist2 { p0: f32, p1: f32 }
-- Construct a distribution from masses already on the simplex. The producer
-- obligation discharges at SMT: under the guard the pair is nonnegative and sums
-- to one, so the constructed value satisfies the invariant.
def make_dist(p0: f32, p1: f32) -> Option[Dist2] = if ((((p0 >= 0.0) && (p1 >= 0.0)) && ((p0 + p1) >= (1.0 - eps()))) && ((p0 + p1) <= (1.0 + eps()))) then Some(Dist2 { p0: p0, p1: p1 }) else None
-- One Markov step. The input distribution is an opaque Dist2, so its simplex
-- invariant is the assumed precondition; the transition rows (t00, t01) and
-- (t10, t11) are guarded row-stochastic. The producer obligation proves the
-- output is again on the simplex (nonnegativity and total mass both preserved).
def advance(d: Dist2, t00: f32, t01: f32, t10: f32, t11: f32) -> Option[Dist2] = if ((((((t00 >= 0.0) && (t01 >= 0.0)) && (t10 >= 0.0)) && (t11 >= 0.0)) && ((t00 + t01) == 1.0)) && ((t10 + t11) == 1.0)) then Some(Dist2 { p0: ((d.p0 * t00) + (d.p1 * t10)), p1: ((d.p0 * t01) + (d.p1 * t11)) }) else None
-- One output mass entry of the transition step, as an exported scalar operator,
-- so the structural properties prove the real shipped arithmetic rather than a
-- restatement. The first output mass is next_mass(p0, p1, t00, t10); the second
-- is next_mass(p0, p1, t01, t11).
def next_mass(p: f32, q: f32, ta: f32, tb: f32) -> f32 = ((p * ta) + (q * tb))
