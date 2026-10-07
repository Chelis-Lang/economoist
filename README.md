# Economoist

Economoist is a [Chelis](https://github.com/Chelis-Lang/chelis) package of
small economic models: Markov transitions, Bellman updates, and Gordon present
value. Each model states its assumptions, and its properties are checked over
the reals by SMT under those assumptions. A separate sampled check covers the
Gordon automatic-differentiation sensitivity at selected inputs.

Read the book at [chelis.ch/docs/economoist](https://chelis.ch/docs/economoist/)
(source in [`docs/book`](docs/book/)). Start with the
[model guide](https://chelis.ch/docs/economoist/models/) and the
[boundaries](https://chelis.ch/docs/economoist/boundaries/) of what each result
covers.

## Use

Install the release into your local Reef registry (no GitHub token needed),
add it as a dependency in your project's `reef.toml`, and build:

```sh
chelis reef install --from-github Chelis-Lang/economoist@v0.2.16
chelis reef build
```

Its one dependency, `chelis-std`, ships with the compiler. With `GITHUB_TOKEN`
set or `gh` signed in, `chelis reef build` fetches a missing package itself. Set
your project's compiler pin to the version this release requires (the
`compiler` field of this repository's `reef.toml`). The
[getting started page](https://chelis.ch/docs/economoist/getting-started/) has
the full sequence. See
[Reef and packages](https://chelis.ch/docs/chelis/reef/) and the
[Chelis installation guide](https://chelis.ch/docs/chelis/install/).

## License

MIT. See [LICENSE](LICENSE).
