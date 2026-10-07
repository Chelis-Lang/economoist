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

Add the released `economoist` package as a dependency in your project's
`reef.toml` and run `chelis reef build`. Reef downloads the package and its
released dependencies. Set your project's compiler pin to the version this
release requires (the `compiler` field of this repository's `reef.toml`). See
[Reef and packages](https://chelis.ch/docs/chelis/reef/) and the
[Chelis installation guide](https://chelis.ch/docs/chelis/install/).

## License

MIT. See [LICENSE](LICENSE).
