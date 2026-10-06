# Economoist

Economoist is a [Chelis](https://github.com/Chelis-Lang/chelis) package of small economic models: Markov transitions, Bellman updates, and Gordon present value. Start with the [model guide](docs/SUMMARY.md) for the checked claims and their limits.

The package pins Chelis in [`reef.toml`](reef.toml). Its checks have different meanings:

- `src/` contains the model functions and guarded distribution types. `properties/` states facts about those functions. Passing SMT checks establish the stated properties over real arithmetic, under their written guards, at the shipped dimensions. The `f32` type annotations do not turn an SMT result into a floating-point guarantee.
- `sampled/` checks the Gordon automatic-differentiation result by sampling. A passing sampled check is not a proof for every input.
- `demos/` contains selected false claims and passing controls. The false claims are expected to produce counterexamples.
- `tests/` exercises concrete values.

## Run from a source checkout

Install Git, `uv`, and the GitHub CLI (`gh`), then authenticate with
`gh auth login` or set `GITHUB_TOKEN`. Bootstrap
[`chelisup`](https://github.com/Chelis-Lang/chelis/blob/main/docs/book/src/install.md)
from the public Chelis release:

```sh
gh release download --repo Chelis-Lang/chelis --pattern chelisup.sh --output - | sh
export PATH="$HOME/.chelis/bin:$PATH"
gh repo clone Chelis-Lang/economoist
cd economoist
uv venv --python 3.11
chelis reef setup
chelis --version
chelis reef build
chelis test tests/
.venv/bin/python scripts/prove_gate.py
```

`reef setup` installs the compiler pinned in `reef.toml` and its locked
dependencies. From this checkout, `chelis --version` reports that version.
Add `~/.chelis/bin` to your shell's startup file to keep `chelis` available in
later sessions. The proof gate checks the SMT properties and sampled result
separately, and exits successfully when the expected proofs, counterexamples,
and controls behave as specified. For the complete local check, run
`.venv/bin/python scripts/run_local_gate.py`.

Running `chelis prove` directly on `properties/growth.ch` exits nonzero because that file also contains deliberately false guard-satisfiability witnesses. Use `scripts/prove_gate.py` for the package verdict; see [reading proof results](docs/SUMMARY.md#reading-proof-results).

## License

MIT. See [LICENSE](LICENSE).
