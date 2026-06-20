module Economoist.Tests.Markov
import Std.Test (assert_close)
import Economoist.Markov (next_mass, mass3_next)
-- Numeric checks of the Markov step operator on a concrete instance. The
-- structural guarantees (simplex preservation) are proven by the prover; these
-- tests only confirm the numeric operator computes the expected values.
def test_next_mass_entry() -> unit ! { Test } = {
  m0 = next_mass(cast(0.6, f32), cast(0.4, f32), cast(0.7, f32), cast(0.2, f32))
  assert_close(m0, cast(0.5, f32), cast(0.0001, f32), "next_mass entry 0 == 0.5")
}
def test_output_masses_sum_to_one() -> unit ! { Test } = {
  m0 = next_mass(cast(0.6, f32), cast(0.4, f32), cast(0.7, f32), cast(0.2, f32))
  m1 = next_mass(cast(0.6, f32), cast(0.4, f32), cast(0.3, f32), cast(0.8, f32))
  total = add(m0, m1)
  assert_close(total, cast(1.0, f32), cast(0.0001, f32), "output masses sum to one")
}
def test_mass3_next_entry() -> unit ! { Test } = {
  m0 = mass3_next(cast(0.2, f32), cast(0.3, f32), cast(0.5, f32), cast(0.5, f32), cast(0.1, f32), cast(0.2, f32))
  assert_close(m0, cast(0.23, f32), cast(0.0001, f32), "mass3_next entry 0 == 0.23")
}
def test_output_masses3_sum_to_one() -> unit ! { Test } = {
  m0 = mass3_next(cast(0.2, f32), cast(0.3, f32), cast(0.5, f32), cast(0.5, f32), cast(0.1, f32), cast(0.2, f32))
  m1 = mass3_next(cast(0.2, f32), cast(0.3, f32), cast(0.5, f32), cast(0.3, f32), cast(0.6, f32), cast(0.3, f32))
  m2 = mass3_next(cast(0.2, f32), cast(0.3, f32), cast(0.5, f32), cast(0.2, f32), cast(0.3, f32), cast(0.5, f32))
  total = add(add(m0, m1), m2)
  assert_close(total, cast(1.0, f32), cast(0.0001, f32), "n=3 output masses sum to one")
}
