# Draft: prove --json dependency_edges omits cross-module import references

Historical draft, superseded by chelis#922's linker-owned dependency graph in
Chelis 0.17.2. Retained to document the legacy flat-field limitation.

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

**Historical workaround (no longer active).** Before Chelis 0.17.2, the
producer gate verified anti-vacuity from the prover-emitted `goal` string plus
the corrupt-flip control. At current pins it instead requires chelis#922's
complete linker-owned `dependency_graph` and an exact declaration-to-declaration
edge; the goal fallback is restricted to pre-0.17.2 compatibility.

**Resolution.** chelis#922 added the structured linker-owned dependency graph,
which supersedes `dependency_edges[].references` for this purpose.

**Archive condition.** Keep this draft only as historical rationale while
pre-0.17.2 compatibility remains documented.
