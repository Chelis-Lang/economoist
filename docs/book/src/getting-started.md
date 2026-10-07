# Getting started

Economoist 0.2.16 is built for Chelis 0.19.1. Install Chelis with the
[installation guide](https://chelis.ch/docs/chelis/install/), then create a project:

```sh
chelis reef init demo --module-prefix Demo --output demo
cd demo
```

## Declare the dependency

Edit the generated `reef.toml`. The `compiler` pin must be `"=0.19.1"`, the
exact version Economoist 0.2.16 requires; Reef rejects a project whose pin
differs. Add Economoist under `[dependencies]`:

```toml
[package]
name = "demo"
version = "0.1.0"
compiler = "=0.19.1"
module_prefix = "Demo"
additional_sources = []
resolver = "2"

[dependencies]
economoist = { version = "0.2.16" }
```

`chelis reef build` downloads the Economoist release and records its version
and archive hashes in `reef.lock`. Economoist's own dependency, `chelis-std` 0.4.0,
ships with the compiler. The download uses the GitHub API; if it reports that
no token is available, run `gh auth login` or set `GITHUB_TOKEN`. The
[Reef guide](https://chelis.ch/docs/chelis/reef/) covers lockfiles and `reef setup`.

## A first program

Replace `src/main.ch`:

```chelis
module Demo.Main
import Economoist.Growth (gordon_pv, gordon_pv_checked)
price = gordon_pv(2.0f32, 0.1f32, 0.05f32)
checked = gordon_pv_checked(1.0f32, 0.03f32, 0.08f32)
```

Then format, check, and evaluate it:

```sh
chelis fmt --inplace src/main.ch
chelis check src/main.ch
chelis eval --file src/main.ch
chelis reef build
```

`chelis check` reports `"score": 1` with an empty `errors` list. The
evaluator prints:

```text
price = 40.0
checked = None
```

A dividend of 2 discounted at 10% with 5% growth is worth `2 / 0.05 = 40`.
The second call has the required return below the growth rate, so the checked
function refuses it. Every Economoist function takes and returns `f32`;
write literals with the `f32` suffix, as above, so they match.

The library has three modules:

| Module | Import | Page |
| --- | --- | --- |
| `Economoist.Markov` | `make_dist`, `advance`, `next_mass`, `make_dist3`, `advance3`, `mass3_next`, `eps` | [Markov transitions](models/markov.md) |
| `Economoist.Bellman` | `bellman_state0`, `bellman_state1`, `bellman_state0_n3`, `bellman_state1_n3`, `bellman_state2_n3`, `fmax`, `fmax3`, `fabs` | [Bellman operator](models/bellman.md) |
| `Economoist.Growth` | `gordon_pv`, `gordon_pv_checked`, `gordon_pv_strict`, `gordon_pv_strict_checked`, `gordon_pv_negated` | [Gordon present value](models/growth.md) |

## Check a property against the library

`chelis prove` checks a `@property` in your own project against the imported
functions, so you can confirm a stated result or test a claim of your own.
This file states Gordon positivity twice, once outside the model's domain
(`g > r`) and once inside it (`r > g`):

```chelis
module Demo.Main
import Economoist.Growth (gordon_pv)
@property gordon_positive_wrong forall(d: f32, r: f32, g: f32) where d > 0.0, g > r:
  (gordon_pv(d, r, g) > 0.0)
@property gordon_positive_control forall(d: f32, r: f32, g: f32) where d > 0.0, r > g:
  (gordon_pv(d, r, g) > 0.0)
```

`chelis prove src/main.ch` prints:

```text
property failure: gordon_positive_wrong
  --> src/main.ch
property: gordon_positive_control -- 0/0 passed
1 passed, 1 failed, 0 unsupported, 0 errors
```

and exits with status 1 because one property failed. `0/0` means no samples
were drawn: the cvc5 SMT solver proved the control over real arithmetic. With
`--json`, the failed property's record carries the solver's counterexample,
`{"d": "1.0", "g": "0.0", "r": "(- 1.0)"}`, which is `d = 1, r = -1, g = 0`
and gives a present value of `-1`. The
[counterexamples page](business-wrong.md) lists the other
false claims of this kind and the guard each one is missing.
