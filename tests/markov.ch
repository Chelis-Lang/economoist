module Economoist.Tests.Markov
import Std.Test (assert_close)
import Economoist.Markov (next_mass, mass3_next)
-- Numeric checks of the Markov step operator on a concrete instance. The
-- structural guarantees (simplex preservation) are proven by the prover; these
-- tests only confirm the numeric operator computes the expected values.
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
