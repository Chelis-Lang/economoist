# Economoist

Verified economic and dynamic-programming models for the
[Chelis](https://github.com/Chelis-Lang/chelis) language, shipped as a reef
package under the `Economoist` module prefix.

Economoist is the academic-launch surface for "C Proof". Its defining principle:
every economic property it states is a genuine, unqualified SMT green, proven at
the SMT tier by cvc5 over the reals with no fuzz sampling and no contract. A
property that comes back sampled or contract-qualified is a bug to fix, not a
result to ship.

Economic content lives here. Finance and derivatives stay in
[Shoals](https://github.com/Chelis-Lang/shoals), and Economoist never depends on
Shoals.

## Documentation

This README stays small on purpose. Anything that moves as models are added or
proofs change lives in the docs:

- [docs/SUMMARY.md](docs/SUMMARY.md) indexes the models, the business-wrong
  demos, the surfaces, and the gates.
- [docs/models/](docs/models/) gives each model's proven properties and its
  held-out boundaries (limit and convergence, fixed dimension, reals versus
  floats), stated per property.
- [docs/CHELIS_SURFACE.md](docs/CHELIS_SURFACE.md) records what Chelis and
  chelis-std provide to this domain.
- [docs/cnote-import-surface.json](docs/cnote-import-surface.json) is the frozen
  machine-readable import surface for C Note.

## Building and proving

Build the package with the released `chelis` tarball:

```sh
chelis reef build
```

SMT prove uses a separate from-source binary that links cvc5. Build it with
`python3 scripts/build_chelis_smt.py`, which runs
`cargo build --release -p chelis-cli --features smt` (the host needs `cmake`,
`g++`, and `libclang-dev`). `scripts/prove_gate.py` drives that binary over the
properties in `properties/` and the demos in `demos/`; `scripts/run_local_gate.py`
runs the full gate.

`reef.toml` is the single source of truth for the compiler and `chelis-std` pins
and the package version.

## License

MIT. See [LICENSE](LICENSE).
