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

SMT prove ships in the same released `chelis` binary as of chelis v0.11.0, so no
separate from-source build is needed. `scripts/prove_gate.py` drives `chelis
prove` over the properties in `properties/` and the demos in `demos/`;
`scripts/run_local_gate.py` runs the full gate. All stages resolve one binary:
`CHELIS_BIN` if set, else the reef.toml-pinned release install
(`~/.local/share/chelis/<pin>/bin/chelis`), else `chelis` on PATH.

`reef.toml` is the single source of truth for the compiler and `chelis-std` pins
and the package version.

The **lean per-PR** CI gate (`.github/workflows/ci.yml`) runs the fast checks
only: `chelis fmt --check`, `chelis lint --check`, `chelis reef build`, the
negative-test and blocked-probe suites, plus the offline `hard-rule-guard`,
`no-ai-authorship`, and `contract-gate` jobs. `scripts/prove_gate.py` (the SMT
keystone) and its metamorphic anti-vacuity forge negatives
(`scripts/run_forge_tests.py`) do NOT run per-PR -- real-SMT wall over the full
canon runs ~5-9 min -- so both run in the **nightly** CI gate
(`.github/workflows/nightly.yml`, daily + `workflow_dispatch`) instead.
`scripts/run_local_gate.py` runs every stage locally before push.

## License

MIT. See [LICENSE](LICENSE).
