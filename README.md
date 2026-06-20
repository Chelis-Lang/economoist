# Economoist

Verified economic and dynamic-programming models for the
[Chelis](https://github.com/Chelis-Lang/chelis) language. Ships as a reef
package under the `Economoist` module prefix.

Economoist is the academic-launch surface for "C Proof": every economic
property it states is written to be a genuine, unqualified SMT green (cvc5,
over the reals, zero fuzz, no contract). A result that only closes under a
contract qualifier, or that comes back amber, is treated as a bug to fix
rather than a result to ship.

Economic content lives here. Finance and derivatives stay in
[Shoals](https://github.com/Chelis-Lang/shoals), and Economoist never depends
on Shoals.

## Modules

| Module | Contents |
|---|---|
| `Economoist.Markov` | Finite-state Markov chains: stochastic-matrix structure, row-stochasticity invariants, one-step distribution updates. |
| `Economoist.Bellman` | Bellman operators for dynamic programming: the value-update map, monotonicity and discounting structure of a single application. |
| `Economoist.Growth` | Discrete-time growth models: capital-accumulation and production-function structure, single-step transition properties. |

## Honesty boundaries

Every proven property says where the green stops. The three boundaries are
mandatory in each module's docs:

- **Single-step vs limit/convergence.** A green on a one-step contraction or
  monotonicity is not a green on the fixed point or the convergence of the
  iteration. The limit claim needs induction and is held out.
- **Fixed dimension vs general-n.** A green at `n = 2` or `n = 3` is an
  instance, not the universal theorem over all `n`. The general-n claim is
  held out alongside convergence.
- **Reals vs floats.** The proven fact is real arithmetic as discharged by
  cvc5 over the reals, not a statement about `f32` evaluation. The
  floating-point behavior of any demo is a separate, unproven concern.

## Building and proving

Build the package with the released `chelis` tarball:

```sh
chelis reef build
```

SMT prove uses a separate from-source binary that links cvc5. Build it with:

```sh
python3 scripts/build_chelis_smt.py
```

which runs `cargo build --release -p chelis-cli --features smt` (the build
host needs `cmake`, `g++`, and `libclang-dev`) and installs it side-by-side
as `~/.local/share/chelis/0.8.0/chelis-smt`. The prove gate drives that
binary over the property bodies in `properties/`.

`reef.toml` is the single source of truth for the compiler and `chelis-std`
pins and the package version.

## License

MIT. See [LICENSE](LICENSE).
