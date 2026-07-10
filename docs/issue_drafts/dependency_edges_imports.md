# Draft: prove --json dependency_edges omits cross-module import references

Not yet filed upstream (draft; cite this path until a chelis#NNN is assigned).

**Summary.** The `prove --json` summary record carries a `dependency_edges` array
(`{property, references}`) intended to list the functions a property's goal
references. It lists only calls to defs in the SAME file; a call to a function
imported from another module resolves and proves, but its reference does NOT
appear in `dependency_edges` -- the array is `[]`.

**Why it matters for the characterization contract.** The contract
(`chelis-shell.invariant-surface/1.0`) proposes a mechanical anti-vacuity check:
an invariant declaring `references_output_fn: "direct"` must show its output fn in
the prover's `dependency_edges`. Economoist's proven properties import their
output fns from `src/` (e.g. `Economoist.Growth.gordon_pv`,
`Economoist.Bellman.bellman_state0`), so `dependency_edges` is uniformly `[]` for
them even though the goals genuinely call the exports -- the dependency_edges
anti-vacuity check does not survive the module-import boundary.

**Reproducer (chelis 0.14.0).** A local-def call reports the reference:

```
def gpv(d: f32, r: f32, g: f32) -> f32 = (d / (r - g))
@property loc forall(d: f32, r: f32, g: f32) where (d > 0.0), (r > g): (gpv(d, r, g) > 0.0)
-- dependency_edges: [{property: loc, references: ["gpv"]}]
```

The same property importing `gpv` from another module proves but reports
`references: []`.

**Workaround (in use).** The producer gate (`scripts/prove_gate.py`) verifies
anti-vacuity from the prover-emitted `goal` string, which DOES carry the mangled
imported reference (e.g. `pkg__economoist__Economoist__Growth__gordon_pv(d, r,
g)`), PLUS the corrupt-flip control (the violating twin must break with a
counterexample). Goal-string reference + corrupt-flip is a stronger anti-vacuity
guarantee than dependency_edges alone.

**Ask.** Populate `dependency_edges[].references` with cross-module import calls,
so consumers can compute anti-vacuity from the structured field rather than
parsing the goal string.

**Filing condition.** dependency_edges still omits import references at the next
chelis release.
