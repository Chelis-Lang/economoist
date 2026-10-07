# Developing Economoist

Maintainer notes for working from a source checkout. The user-facing book is
in [`book/`](book/); this file is not part of it.

## Layout and what each check means

- `src/` contains the model functions and guarded distribution types.
  `properties/` states facts about those functions. Passing SMT checks
  establish the stated properties over real arithmetic, under their written
  guards, at the shipped dimensions. The `f32` type annotations do not turn an
  SMT result into a floating-point guarantee.
- `sampled/` checks the Gordon automatic-differentiation result by sampling. A
  passing sampled check is not a proof for every input.
- `demos/` contains selected false claims and passing controls. The false
  claims are expected to produce counterexamples.
- `tests/` exercises concrete values.

## Run from a source checkout

Install Git, `uv`, and the GitHub CLI (`gh`), then authenticate with
`gh auth login` or set `GITHUB_TOKEN`. Bootstrap `chelisup`
([install guide](https://chelis.ch/docs/chelis/install/)) from the public
Chelis release:

```sh
gh release download --repo Chelis-Lang/chelis --pattern chelisup.sh --output - | sh
export PATH="$HOME/.chelis/bin:$PATH"
gh repo clone Chelis-Lang/economoist
cd economoist
uv venv --python 3.11
chelisup install "$(.venv/bin/python -c 'import tomllib; print(tomllib.load(open("reef.toml", "rb"))["package"]["compiler"].removeprefix("="))')"
chelis reef setup
chelis --version
chelis reef build
chelis test tests/
.venv/bin/python scripts/prove_gate.py
```

`chelisup install` reads the compiler pin from `reef.toml` and installs its
version-selecting shim. `reef setup` then installs the locked dependencies.
From this checkout, `chelis --version` reports the pinned version. Add
`~/.chelis/bin` to your shell's startup file to keep `chelis` available in
later sessions. The proof gate checks the SMT properties and sampled result
separately, and exits successfully when the expected proofs, counterexamples,
and controls behave as specified. For the complete local check, run
`.venv/bin/python scripts/run_local_gate.py`.

## Reading raw proof output

`chelis prove` checks one file or package. In JSON output, a passing checked
goal reports `status: "passed"`, `proof_tier: "smt"`, `arith_model: "real"`,
and `samples: 0`.

Each `properties/` file also contains `*_guards_satisfiable` witnesses. They
assert `false` under the corresponding guards; a counterexample shows those
guards admit an input. Running `chelis prove` directly on a `properties/` file
therefore exits nonzero even when the package is healthy.
`demos/businesswrong.ch` likewise has selected false claims paired with
passing controls, and `sampled/growth_sensitivity.ch` has a `_wrong` companion
that is expected to fail with a counterexample. Use `scripts/prove_gate.py`
for the package verdict.

## The book

`docs/book/` is rendered from the chelis.ch docs; see the Book section of
[`AGENTS.md`](../AGENTS.md). Check it with:

```sh
mdbook build docs/book
python3 scripts/check_book.py docs/book/src README.md
.venv/bin/python scripts/check_book_examples.py
```

`check_book_examples.py` builds this checkout into a throwaway Reef registry
(it points `HOME` at a temporary directory, so `~/.chelis/reef` is untouched),
runs each `chelis` block in the book as a consumer project's `src/main.ch`,
and compares the output with the `text` block that follows it. A failure
means the chelis.ch page is wrong or the API changed; fix the site page and
re-render.
