# Boundaries

## One step and repeated updates

The Bellman checks cover one application of an operator. They do not check
that repeated applications converge to a fixed point. The Gordon checks
establish properties of `d / (r - g)` under stated guards; they do not
establish convergence of a cash-flow series.

## Fixed dimensions

The checked Markov and Bellman instances have two or three states. Their
results do not establish the same statements for every state-space size.
The Bellman instances have two actions per state. The Gordon expression
has no state dimension.

## Reals and floating point

cvc5 checks the listed properties using mathematical real arithmetic. A
result over reals does not establish the same result for `f32` execution
after rounding. The sampled automatic-differentiation check runs in `f32` at 500
seeded inputs; it does not establish a result for every input, or for any
input outside its sampling box.

## Guarded and unguarded functions

Only `make_dist`, `make_dist3`, `advance`, `advance3`, `gordon_pv_checked`
and `gordon_pv_strict_checked` test their inputs, and each returns `None` on
failure. Every other function, including all of `Economoist.Bellman`, returns
a number for any `f32` input, and the proved results say nothing about inputs
outside their assumptions.

## Read each result

Each result applies only under its stated assumptions. The
[model guide](models.md) summarizes the checked claims and
their limits.
