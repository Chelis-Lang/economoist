module Economoist.Markov
export (eps, make_dist, advance, next_mass, make_dist3, advance3, mass3_next)
-- Economoist.Markov: a finite-state Markov transition operator over a fixed
-- small state space. The structural greens ship at two dimensions, n = 2 and
-- n = 3, each with its own opaque distribution type, guarded constructor,
-- transition step, and scalar mass operator.
--
-- A distribution on the simplex is a vector of nonnegative masses summing to
-- one (a pair on the 2-simplex for n = 2, a triple on the 3-simplex for n = 3).
-- A row-stochastic transition has nonnegative rows that each sum to one. The
-- next distribution is the transition applied to the current one.
--
-- PROVEN here (single application, SMT, transcendental-free, over the reals):
--   advance / advance3 : applying a row-stochastic transition to a distribution
--             on the simplex yields a distribution on the simplex. The invariant
--             producer obligation proves nonnegativity preserved and total mass
--             preserved together, at both n = 2 and n = 3.
-- HELD OUT (see docs/models/markov.md): stationary distribution existence and
--   uniqueness, convergence to stationarity, ergodicity (limit results, need
--   induction); and the general-n (all-n) theorem. The shipped greens cover the
--   two fixed dimensions n = 2 and n = 3, not every state space size.
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
def make_dist(p0: f32, p1: f32) -> Option[Dist2] = if ((((p0 >= 0.0) && (p1 >= 0.0)) && ((p0 + p1) >= (1.0 - eps()))) && ((p0 + p1) <= (1.0 + eps()))) then Some(Dist2 { p0, p1 }) else None
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
-- A distribution on the 3-simplex. As with Dist2, the invariant carries an f32
-- epsilon band on the sum: it states the runtime f32 invariant, which is
-- distinct from the exact real-arithmetic mass identity proven by
-- markov3_mass_preserved.
@opaque
@invariant(d) (((((d.p0 >= 0.0) && (d.p1 >= 0.0)) && (d.p2 >= 0.0)) && (((d.p0 + d.p1) + d.p2) >= (1.0 - eps))) && (((d.p0 + d.p1) + d.p2) <= (1.0 + eps)))
type Dist3 =
  | Dist3 { p0: f32, p1: f32, p2: f32 }
-- Construct a 3-simplex distribution from masses already on the simplex. The
-- producer obligation discharges at SMT: under the guard the triple is
-- nonnegative and sums to one, so the constructed value satisfies the invariant.
def make_dist3(p0: f32, p1: f32, p2: f32) -> Option[Dist3] = if (((((p0 >= 0.0) && (p1 >= 0.0)) && (p2 >= 0.0)) && (((p0 + p1) + p2) >= (1.0 - eps()))) && (((p0 + p1) + p2) <= (1.0 + eps()))) then Some(Dist3 { p0, p1, p2 }) else None
-- One Markov step at n = 3. The input distribution is an opaque Dist3, so its
-- simplex invariant is the assumed precondition; the transition rows
-- (t00, t01, t02), (t10, t11, t12), and (t20, t21, t22) are guarded
-- row-stochastic. The producer obligation proves the output is again on the
-- 3-simplex (nonnegativity and total mass both preserved).
def advance3(d: Dist3, t00: f32, t01: f32, t02: f32, t10: f32, t11: f32, t12: f32, t20: f32, t21: f32, t22: f32) -> Option[Dist3] = if (((((((((((t00 >= 0.0) && (t01 >= 0.0)) && (t02 >= 0.0)) && (t10 >= 0.0)) && (t11 >= 0.0)) && (t12 >= 0.0)) && (t20 >= 0.0)) && (t21 >= 0.0)) && (t22 >= 0.0)) && ((((t00 + t01) + t02) == 1.0) && (((t10 + t11) + t12) == 1.0))) && (((t20 + t21) + t22) == 1.0)) then Some(Dist3 { p0: (((d.p0 * t00) + (d.p1 * t10)) + (d.p2 * t20)), p1: (((d.p0 * t01) + (d.p1 * t11)) + (d.p2 * t21)), p2: (((d.p0 * t02) + (d.p1 * t12)) + (d.p2 * t22)) }) else None
-- One output mass entry of the n = 3 transition step, as an exported scalar
-- operator, so the structural properties prove the real shipped arithmetic
-- rather than a restatement. The first output mass is
-- mass3_next(p0, p1, p2, t00, t10, t20); the second is
-- mass3_next(p0, p1, p2, t01, t11, t21); the third is
-- mass3_next(p0, p1, p2, t02, t12, t22). (The name is mass3_next, not
-- next_mass3, so it does not form a shared next_ prefix group with the n = 2
-- next_mass operator, which the §7.1 prefix lint would reject.)
def mass3_next(p0: f32, p1: f32, p2: f32, ta: f32, tb: f32, tc: f32) -> f32 = (((p0 * ta) + (p1 * tb)) + (p2 * tc))
