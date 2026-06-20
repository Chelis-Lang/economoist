# Out-of-band numeric cross-check against QuantEcon

The in-repo oracle ([`scripts/oracle_harness.py`](../scripts/oracle_harness.py))
validates the shell's `eval` numerics against recorded analytic-mirror goldens,
stdlib only. QuantEcon is a research cross-check, not a shipped dependency, since
it does not fit the stdlib-only gate. It is therefore run out of band and the
result recorded here.

Performed 2026-06-20 with `quantecon` and `numpy` in an ephemeral environment.
For concrete instances, the analytic mirrors the in-repo oracle trusts were
checked against an independent computation:

- Markov step (3 states): the next distribution `d @ P` computed by numpy matched
  the `next_mass3` mirror entry by entry (`[0.535, 0.295, 0.17]`) and summed to
  one; `quantecon.MarkovChain` agreed on the same chain. QuantEcon's stationary
  distribution for that chain is the held-out convergence content (not a shipped
  property), shown only for reference.
- Gordon present value: `D / (r - g)` at `(2, 0.1, 0.05)` equals `40.0`.
- Bellman operator (one application): the max over actions equals `2.02`.

All matched. The cross-check confirms the analytic mirrors are correct against an
independent library. The prove gate, not this cross-check, is what establishes
the structural properties; a matching number is not a proof.
