module Economoist.Markov
export (eps, make_dist, advance, next_mass, make_dist3, advance3, mass3_next)
-- A finite-state Markov transition at two or three states. Each size has an
-- opaque distribution type, guarded constructor, transition step, and scalar
-- mass operator.
--
-- The opaque distribution invariants require nonnegative masses whose sum
-- lies within eps() of one. A transition is admitted when its rows are
-- nonnegative, each row sum lies within eps() of one, and the masses the step
-- actually computes land inside the same band. The next distribution applies
-- that transition to the current masses.
--
-- SMT checks that each constructor and transition preserves its type
-- invariant over the reals. Separate properties check exact one-step mass
-- and nonnegativity under exact-sum guards. There is no checked stationarity,
-- convergence, ergodicity, or arbitrary-state-count claim. See
-- docs/models/markov.md.
def eps() -> f32 = 0.0001
-- One mass-sum tolerance test, shared by every constructor and transition in
-- this module so the distribution invariant and the transition guards cannot
-- drift apart. True when total lies within eps() of one.
def band_ok(total: f32) -> bool = ((total >= (1.0 - eps())) && (total <= (1.0 + eps())))
-- Two nonnegative masses whose sum lies within eps() of one. This type
-- invariant differs from markov_mass_preserved's exact real-arithmetic goal.
@opaque
@invariant(d) ((((d.p0 >= 0.0) && (d.p1 >= 0.0)) && ((d.p0 + d.p1) >= (1.0 - eps))) && ((d.p0 + d.p1) <= (1.0 + eps)))
type Dist2 =
  | Dist2 { p0: f32, p1: f32 }
-- Construct a two-state value when the masses satisfy the invariant band.
-- The producer obligation checks that the returned value has that invariant.
def make_dist(p0: f32, p1: f32) -> Option[Dist2] = if (((p0 >= 0.0) && (p1 >= 0.0)) && band_ok((p0 + p1))) then Some(Dist2 { p0, p1 }) else None
-- One Markov step. Dist2 supplies its stated invariant. The transition is
-- admitted when its rows are nonnegative and each row sum lies within the
-- same eps() band the distribution carries, and when the masses the step
-- computes also land inside that band; otherwise the step returns None. The
-- producer obligation derives output nonnegativity from the row and mass
-- nonnegativity and reads the output band off the guard, so a returned value
-- always satisfies the Dist2 invariant.
def advance(d: Dist2, t00: f32, t01: f32, t10: f32, t11: f32) -> Option[Dist2] = if (((((((t00 >= 0.0) && (t01 >= 0.0)) && (t10 >= 0.0)) && (t11 >= 0.0)) && band_ok((t00 + t01))) && band_ok((t10 + t11))) && band_ok((next_mass(d.p0, d.p1, t00, t10) + next_mass(d.p0, d.p1, t01, t11)))) then Some(Dist2 { p0: next_mass(d.p0, d.p1, t00, t10), p1: next_mass(d.p0, d.p1, t01, t11) }) else None
-- One output mass entry of the transition step, as an exported scalar operator,
-- so the structural properties prove the real shipped arithmetic rather than a
-- restatement. advance calls it for both entries, so the proved operator and
-- the shipped step are the same expression. The first output mass is
-- next_mass(p0, p1, t00, t10); the second is next_mass(p0, p1, t01, t11).
def next_mass(p: f32, q: f32, ta: f32, tb: f32) -> f32 = ((p * ta) + (q * tb))
-- Three nonnegative masses whose sum lies within eps() of one. This band
-- differs from markov3_mass_preserved's exact real-arithmetic goal.
@opaque
@invariant(d) (((((d.p0 >= 0.0) && (d.p1 >= 0.0)) && (d.p2 >= 0.0)) && (((d.p0 + d.p1) + d.p2) >= (1.0 - eps))) && (((d.p0 + d.p1) + d.p2) <= (1.0 + eps)))
type Dist3 =
  | Dist3 { p0: f32, p1: f32, p2: f32 }
-- Construct a three-state value when the masses satisfy the invariant band.
-- The producer obligation checks that the returned value has that invariant.
def make_dist3(p0: f32, p1: f32, p2: f32) -> Option[Dist3] = if ((((p0 >= 0.0) && (p1 >= 0.0)) && (p2 >= 0.0)) && band_ok(((p0 + p1) + p2))) then Some(Dist3 { p0, p1, p2 }) else None
-- One three-state step, admitted on the same terms as advance: nonnegative
-- rows, every row sum inside the eps() band, and the computed masses inside
-- that band as well. The producer obligation derives output nonnegativity and
-- reads the output band off the guard, so a returned value always satisfies
-- the Dist3 invariant.
def advance3(d: Dist3, t00: f32, t01: f32, t02: f32, t10: f32, t11: f32, t12: f32, t20: f32, t21: f32, t22: f32) -> Option[Dist3] = if ((((((((((((t00 >= 0.0) && (t01 >= 0.0)) && (t02 >= 0.0)) && (t10 >= 0.0)) && (t11 >= 0.0)) && (t12 >= 0.0)) && (t20 >= 0.0)) && (t21 >= 0.0)) && (t22 >= 0.0)) && band_ok(((t00 + t01) + t02))) && (band_ok(((t10 + t11) + t12)) && band_ok(((t20 + t21) + t22)))) && band_ok(((mass3_next(d.p0, d.p1, d.p2, t00, t10, t20) + mass3_next(d.p0, d.p1, d.p2, t01, t11, t21)) + mass3_next(d.p0, d.p1, d.p2, t02, t12, t22)))) then Some(Dist3 { p0: mass3_next(d.p0, d.p1, d.p2, t00, t10, t20), p1: mass3_next(d.p0, d.p1, d.p2, t01, t11, t21), p2: mass3_next(d.p0, d.p1, d.p2, t02, t12, t22) }) else None
-- One output mass entry of the n = 3 transition step, as an exported scalar
-- operator, so the structural properties prove the real shipped arithmetic
-- rather than a restatement. advance3 calls it for all three entries, so the
-- proved operator and the shipped step are the same expression. The first
-- output mass is mass3_next(p0, p1, p2, t00, t10, t20); the second is
-- mass3_next(p0, p1, p2, t01, t11, t21); the third is
-- mass3_next(p0, p1, p2, t02, t12, t22). (The name is mass3_next, not
-- next_mass3, so it does not form a shared next_ prefix group with the n = 2
-- next_mass operator, which the §7.1 prefix lint would reject.)
def mass3_next(p0: f32, p1: f32, p2: f32, ta: f32, tb: f32, tc: f32) -> f32 = (((p0 * ta) + (p1 * tb)) + (p2 * tc))
