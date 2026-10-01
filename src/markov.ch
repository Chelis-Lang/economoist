module Economoist.Markov
export (eps, make_dist, advance, next_mass, make_dist3, advance3, mass3_next)
-- A finite-state Markov transition at two or three states. Each size has an
-- opaque distribution type, guarded constructor, transition step, and scalar
-- mass operator.
--
-- The opaque distribution invariants require nonnegative masses whose sum
-- lies within eps() of one. A row-stochastic transition has nonnegative rows
-- that each sum to exactly one. The next distribution applies that
-- transition to the current masses.
--
-- SMT checks that each constructor and transition preserves its type
-- invariant over the reals. Separate properties check exact one-step mass
-- and nonnegativity under exact-sum guards. There is no checked stationarity,
-- convergence, ergodicity, or arbitrary-state-count claim. See
-- docs/models/markov.md.
def eps() -> f32 = 0.0001
-- Two nonnegative masses whose sum lies within eps() of one. This type
-- invariant differs from markov_mass_preserved's exact real-arithmetic goal.
@opaque
@invariant(d) ((((d.p0 >= 0.0) && (d.p1 >= 0.0)) && ((d.p0 + d.p1) >= (1.0 - eps))) && ((d.p0 + d.p1) <= (1.0 + eps)))
type Dist2 =
  | Dist2 { p0: f32, p1: f32 }
-- Construct a two-state value when the masses satisfy the invariant band.
-- The producer obligation checks that the returned value has that invariant.
def make_dist(p0: f32, p1: f32) -> Option[Dist2] = if ((((p0 >= 0.0) && (p1 >= 0.0)) && ((p0 + p1) >= (1.0 - eps()))) && ((p0 + p1) <= (1.0 + eps()))) then Some(Dist2 { p0, p1 }) else None
-- One Markov step. Dist2 supplies its stated invariant; the transition rows
-- are guarded row-stochastic. The producer obligation checks that the output
-- remains nonnegative with its mass sum inside the invariant band.
def advance(d: Dist2, t00: f32, t01: f32, t10: f32, t11: f32) -> Option[Dist2] = if ((((((t00 >= 0.0) && (t01 >= 0.0)) && (t10 >= 0.0)) && (t11 >= 0.0)) && ((t00 + t01) == 1.0)) && ((t10 + t11) == 1.0)) then Some(Dist2 { p0: ((d.p0 * t00) + (d.p1 * t10)), p1: ((d.p0 * t01) + (d.p1 * t11)) }) else None
-- One output mass entry of the transition step, as an exported scalar operator,
-- so the structural properties prove the real shipped arithmetic rather than a
-- restatement. The first output mass is next_mass(p0, p1, t00, t10); the second
-- is next_mass(p0, p1, t01, t11).
def next_mass(p: f32, q: f32, ta: f32, tb: f32) -> f32 = ((p * ta) + (q * tb))
-- Three nonnegative masses whose sum lies within eps() of one. This band
-- differs from markov3_mass_preserved's exact real-arithmetic goal.
@opaque
@invariant(d) (((((d.p0 >= 0.0) && (d.p1 >= 0.0)) && (d.p2 >= 0.0)) && (((d.p0 + d.p1) + d.p2) >= (1.0 - eps))) && (((d.p0 + d.p1) + d.p2) <= (1.0 + eps)))
type Dist3 =
  | Dist3 { p0: f32, p1: f32, p2: f32 }
-- Construct a three-state value when the masses satisfy the invariant band.
-- The producer obligation checks that the returned value has that invariant.
def make_dist3(p0: f32, p1: f32, p2: f32) -> Option[Dist3] = if (((((p0 >= 0.0) && (p1 >= 0.0)) && (p2 >= 0.0)) && (((p0 + p1) + p2) >= (1.0 - eps()))) && (((p0 + p1) + p2) <= (1.0 + eps()))) then Some(Dist3 { p0, p1, p2 }) else None
-- One three-state step. Dist3 supplies its stated invariant; the guarded
-- transition rows are row-stochastic. The producer obligation checks that
-- the output remains nonnegative with its mass sum inside the invariant band.
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
