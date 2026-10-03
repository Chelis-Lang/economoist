module Economoist.Tests.Markov
import Std.Test (assert_close, assert_true, assert_false)
import Economoist.Markov (next_mass, mass3_next, make_dist, advance, make_dist3, advance3)
-- Numeric checks of the Markov step operator on a concrete instance. The
-- structural guarantees (simplex preservation) are proven by the prover; these
-- tests only confirm the numeric operator computes the expected values.
--
-- The admission tests below cover the guard, not the arithmetic: which
-- transitions advance and advance3 accept, and which they refuse. Each
-- accepted case has a refused counterpart.
def test_next_mass_entry() -> unit ! { Test } = {
  m0 = next_mass(0.6f32, 0.4f32, 0.7f32, 0.2f32)
  assert_close(m0, 0.5f32, 0.0001f32, "next_mass entry 0 == 0.5")
}
def test_output_masses_sum_to_one() -> unit ! { Test } = {
  m0 = next_mass(0.6f32, 0.4f32, 0.7f32, 0.2f32)
  m1 = next_mass(0.6f32, 0.4f32, 0.3f32, 0.8f32)
  total = add(m0, m1)
  assert_close(total, 1.0f32, 0.0001f32, "output masses sum to one")
}
def test_mass3_next_entry() -> unit ! { Test } = {
  m0 = mass3_next(0.2f32, 0.3f32, 0.5f32, 0.5f32, 0.1f32, 0.2f32)
  assert_close(m0, 0.23f32, 0.0001f32, "mass3_next entry 0 == 0.23")
}
def test_output_masses3_sum_to_one() -> unit ! { Test } = {
  m0 = mass3_next(0.2f32, 0.3f32, 0.5f32, 0.5f32, 0.1f32, 0.2f32)
  m1 = mass3_next(0.2f32, 0.3f32, 0.5f32, 0.3f32, 0.6f32, 0.3f32)
  m2 = mass3_next(0.2f32, 0.3f32, 0.5f32, 0.2f32, 0.3f32, 0.5f32)
  total = add(add(m0, m1), m2)
  assert_close(total, 1.0f32, 0.0001f32, "n=3 output masses sum to one")
}
-- True when the two-state step accepts the matrix whose every row is (a, b),
-- applied to the point mass on state 0. False when any guard refuses it, and
-- false if that point mass is itself refused, which would make the probe
-- vacuous rather than informative.
def pair_admitted(a: f32, b: f32) -> bool =
  match make_dist(1.0, 0.0) with {
    | Some(d) => match advance(d, a, b, a, b) with {
    | Some(_) => true
    | None => false
  }
    | None => false
  }
-- The three-state counterpart of pair_admitted, over the matrix whose every
-- row is (a, b, c).
def triple_admitted(a: f32, b: f32, c: f32) -> bool =
  match make_dist3(1.0, 0.0, 0.0) with {
    | Some(d) => match advance3(d, a, b, c, a, b, c, a, b, c) with {
    | Some(_) => true
    | None => false
  }
    | None => false
  }
-- The two-state step over the matrix whose every row is (a, b), applied to a
-- starting distribution whose own mass sum is start rather than one.
def drifted_pair_admitted(start: f32, a: f32, b: f32) -> bool =
  match make_dist(start, 0.0) with {
    | Some(d) => match advance(d, a, b, a, b) with {
    | Some(_) => true
    | None => false
  }
    | None => false
  }
-- The three-state step over the matrix whose every row is (a, b, c), applied
-- to a starting distribution whose own mass sum is start rather than one.
def drifted_admitted(start: f32, a: f32, b: f32, c: f32) -> bool =
  match make_dist3(start, 0.0, 0.0) with {
    | Some(d) => match advance3(d, a, b, c, a, b, c, a, b, c) with {
    | Some(_) => true
    | None => false
  }
    | None => false
  }
-- economoist#34 regression. 0.1773 + 0.6378 + 0.1849 is exactly one in decimal and
-- every entry is nonnegative, so the matrix is row-stochastic; left-associated
-- in f32 the row sums to 0.99999994. The exact == 1.0 guard this replaces
-- refused it.
def test_advance3_admits_decimal_row() -> unit ! { Test } = assert_true(triple_admitted(0.1773f32, 0.6378f32, 0.1849f32), "advance3 admits a row summing to one in decimal")
-- The n = 2 instance of the same row, which the exact guard already admitted.
def test_advance_admits_decimal_row() -> unit ! { Test } = assert_true(pair_admitted(0.1773f32, 0.8227f32), "advance admits a row summing to one in decimal")
-- Exact halves are representable, so this passed under the exact guard too. It
-- separates "the band widened the accepted set" from "the band broke it".
def test_advance3_admits_exact_row() -> unit ! { Test } = assert_true(triple_admitted(0.5f32, 0.25f32, 0.25f32), "advance3 admits an exactly representable row")
-- Just inside the band: the row sums to 1.00005, within eps() of one.
def test_advance3_admits_row_inside_band() -> unit ! { Test } = assert_true(triple_admitted(1.00005f32, 0.0f32, 0.0f32), "advance3 admits a row sum inside the eps band")
-- Just outside it: the row sums to 1.0002, more than eps() from one. The band
-- is a tolerance, not an amnesty.
def test_advance3_rejects_row_outside_band() -> unit ! { Test } = assert_false(triple_admitted(1.0002f32, 0.0f32, 0.0f32), "advance3 rejects a row sum outside the eps band")
-- Grossly non-stochastic rows stay refused at both sizes.
def test_advance3_rejects_row_summing_high() -> unit ! { Test } = assert_false(triple_admitted(0.5f32, 0.5f32, 0.5f32), "advance3 rejects rows summing to 1.5")
def test_advance_rejects_row_summing_high() -> unit ! { Test } = assert_false(pair_admitted(0.5f32, 0.6f32), "advance rejects rows summing to 1.1")
-- A negative entry is refused even though the row sums to exactly one, so the
-- band did not displace the nonnegativity half of the guard.
def test_advance3_rejects_negative_entry() -> unit ! { Test } = assert_false(triple_admitted(-0.1f32, 0.6f32, 0.5f32), "advance3 rejects a negative row entry")
def test_advance_rejects_negative_entry() -> unit ! { Test } = assert_false(pair_admitted(-0.1f32, 1.1f32), "advance rejects a negative row entry")
-- The output band is load-bearing, and tolerance does not compound silently. A
-- distribution summing to 0.99992 and rows each summing to 0.99992 are both
-- inside the band on their own; the masses the step computes sum to about
-- 0.99984, outside it, so the step refuses rather than returning a Dist3 that
-- violates its own invariant.
def test_advance3_rejects_compounded_drift() -> unit ! { Test } = assert_false(drifted_admitted(0.99992f32, 0.99992f32, 0.0f32, 0.0f32), "advance3 rejects a step whose computed masses leave the band")
-- The same starting distribution with an exactly representable row stays
-- admitted, so the rejection above is the compounded drift and not the
-- starting distribution on its own.
def test_advance3_admits_drifted_start_on_exact_row() -> unit ! { Test } = assert_true(drifted_admitted(0.99992f32, 1.0f32, 0.0f32, 0.0f32), "advance3 admits a drifted start under an exact row")
-- The n = 2 band edge, which the exact guard refused. advance is named in this
-- change's scope and its admission side needs its own cover: with only the
-- n = 3 tests, reverting advance's two row-sum legs to == 1.0 left both the
-- suite and the prover green.
def test_advance_admits_row_inside_band() -> unit ! { Test } = assert_true(pair_admitted(1.00005f32, 0.0f32), "advance admits a row sum inside the eps band")
-- Its refused counterpart, one step further out.
def test_advance_rejects_row_outside_band() -> unit ! { Test } = assert_false(pair_admitted(1.0002f32, 0.0f32), "advance rejects a row sum outside the eps band")
-- The n = 2 instances of the compounded-drift pair: the start and the row each
-- sit inside the band, their product does not, and the step refuses.
def test_advance_rejects_compounded_drift() -> unit ! { Test } = assert_false(drifted_pair_admitted(0.99992f32, 0.99992f32, 0.0f32), "advance rejects a step whose computed masses leave the band")
def test_advance_admits_drifted_start_on_exact_row() -> unit ! { Test } = assert_true(drifted_pair_admitted(0.99992f32, 1.0f32, 0.0f32), "advance admits a drifted start under an exact row")
