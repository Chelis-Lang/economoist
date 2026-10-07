# Economoist Agent Contract

Canonical agent instructions for this repository. `CLAUDE.md` is a symlink
to this file so Claude-style and Codex-style entry points do not drift.

## Repo Identity

- Economoist is a downstream **shell repo** for the
  [Chelis](https://github.com/Chelis-Lang/chelis) language, scoped to
  verified economic and dynamic-programming models. It is the
  academic surface for checked economic models.
- Every `properties/` economic claim must pass as an unqualified SMT result
  over the reals. The concrete `f32` AD check belongs in `sampled/` and is
  fuzz-validated. No result is generalized beyond its guards or dimension.
- **Domain bifurcation.** Economic content lives here. Finance and
  derivatives stay in [Shoals](https://github.com/Chelis-Lang/shoals).
  Economoist must never depend on Shoals; the two shells share scaffolding,
  not modules.
- **Upstream of truth** is `Chelis-Lang/chelis`. The Chelis monorepo's
  `AGENTS.md` is inherited through the managed block, with the exact-heading
  exclusions declared below for compiler-only and monorepo-only procedures. The
  downstream shell contract applies in full. The machine-local
  environment sections of the monorepo `AGENTS.md` (workstation runbooks,
  first-exec notes, workstation-specific measurements) bind only where the
  named environment actually exists. Make changes to the inherited contract
  and shared skill source in the Chelis compiler repo, then run the pinned
  `chelis reef conform sync` here.

<!-- BEGIN CHELIS MANAGED BLOCK: agents-inheritance chelis@0.19.1 (sha256:6c56f142f4ead852) -->
# Chelis Agent Contract

Keep this file concise and relevant to every agent working in this repository.
Each added token is read tens of thousands of times. State a rule once, link the
document that owns the detail, and put the explanation in that document, not here.

`CLAUDE.md` is a symlink to this file so Claude-style and Codex-style entry points do
not drift.

## What Chelis Is

Chelis is a numerical computing language for code that agents write and people
supervise. Tensors carry named dimensions and precision in their type; the compiler
checks shapes, precision, effects, and ownership before anything runs, and `chelis
prove` checks the properties an author states, naming the method behind each result.
The bet is that numerical code an agent can reason about, and a person can review
through its types and properties, beats code whose mistakes first surface at run time.
Chelis is general purpose within numerical computing; the worked examples come from
quantitative finance. Differentiation and machine-learning programs are research
directions, not the definition of the language. It is not a systems language, a web
framework, a deep-learning framework, or a general scripting replacement for Python.
`spec/00-context.md` and `spec/design/chelis_canonical_reference.md` own the full
statement; their specifics may lag, their intent does not. When a tradeoff
appears, apply these in order:

1. **Unambiguity over ergonomics.** The author is an agent. The friction a human feels
   spelling out every type, effect, dtype, and dimension is not worth a reading the
   compiler has to guess at.
2. **Composition over special cases.** A new capability composes existing primitives
   before it earns a new one.
3. **Inference over annotation.** Where the checker determines something uniquely, the
   author does not repeat it; intermediates carry no ascription.
4. **Machine generation first.** A convenience that exists only for a human typist is
   not a reason to add syntax, a default, or a fallback.
5. **Additive sugar only.** Every surface form desugars to the core; nothing in the
   surface has semantics the core lacks.
6. **Explicit over implicit.** No implicit broadcasting (`expand` only), no implicit
   precision promotion, no implicit currying or partial application, no silent
   narrowing at ingress, no hidden effects. Where intent cannot be determined uniquely,
   the compiler rejects.
7. **Small language, big library.** The compiler knows only the closed RISC primitive
   set and its derived built-ins; everything else is a library. The canonical reference
   §8.5 has the core/standard-library/external-library taxonomy.
8. **Future-proof without over-building.** Decide the rule fully now, implement what
   the phase needs, and never narrow a rule to what a lane implements today.

Two corollaries govern how the compiler itself is changed. Chelis is pre-compatibility
unless a controlling contract says otherwise, so prefer the structural design that
makes a defect class impossible over a smaller-blast-radius patch, a legacy default, a
versionless compatibility fallback, or phase deferral; close the class, not the
instance. And determinism is part of the contract: for fixed program text, compiler
build, target, and declared inputs, every check, evaluation, and build result is a
function of those inputs, and feedback that varies between identical runs is a defect.

## Quality Standards

### Spec-First Development

- Before writing implementation, write test stubs derived from the owning spec.
- Every spec requirement should have a corresponding test before the code exists.
- If the spec says "X is a type error," write the failing test before implementing
  the checker.

### Negative Test Parity

- For every test that checks something works, add the corresponding failure test.
- If you cannot name the failure case, the spec understanding is still weak.

### Do Not Trust Green

- Passing tests prove alignment with the tests, not necessarily with the spec.
- After green CI, check what active requirements still lack tests.
- Audit silent fallbacks, default values, empty error vectors, and `unwrap_or` paths.

## Review And Merge

## Environment And Tooling

## Subagents

[`docs/investigations/agent_contract_rationale.md`](https://github.com/Chelis-Lang/chelis/blob/v0.19.1/docs/investigations/agent_contract_rationale.md)
holds the measurements behind these rules.

- Every subagent prompt names the delivery mechanism and the complete expected report.
  A report that is not sent through the platform's final-report channel has not been
  delivered. A subagent never ends its turn merely to wait for a background build or
  notification that cannot wake it: keep ownership through a synchronous wait, or return
  an honest partial result. A reviewer that has delivered its round report is not
  waiting; it stays available for the orchestrator to resume with the fix.
- CI is watched by at most one background waiter whose exit wakes the session, or by
  nobody. Never watch CI from a foreground sleep or poll loop.
- If an agent returns "waiting" or goes idle without the deliverable, resume it
  immediately with the exact missing items. Prefer a labelled partial report over
  silence or an overstated completion claim, and deduplicate repeated reports that
  race with a resume nudge.
- Every follow-up message to a running subagent, and every message to a peer session,
  ends by asking the recipient to acknowledge it and confirm what it will do. No
  acknowledgement by the recipient's next reply means the message was not received:
  resend it, consolidated.
- More than five subagents live at once under one orchestrator needs the user's
  explicit approval and a stated reason. Five is the widest fan-out measured working
  here, not a certified safe width, and it is a separate budget from the CPU one above.
- Every spawn names its model tier and says in one clause why that tier fits: the
  expensive tier for judgement whose errors are costly to detect, the cheap tier for
  mechanical work such as waiting on CI, polling, or transcribing a result. The
  orchestrator states its own context size in the message that announces a spawn.
- Every brief states a numeric report-length budget, and a numeric context budget except
  for red-team rounds. An agent that will exceed its context budget says so and returns
  what it has.
- A brief says which facts the orchestrator has already verified, against what head, and
  that the agent must not re-derive them, and it names what the agent still has to
  establish itself.
- A brief longer than a few paragraphs is a file passed by absolute path, stored where
  it outlives both the agent and the session, never in a per-session scratchpad.
  Inter-agent messages truncate silently near four kilobytes. "Inline" means
  self-contained, the opposite of "read `AGENTS.md`", not pasted into the spawn message.
- Reports come back the same way: the agent writes the report to a file and replies with
  the absolute path and a one-line summary. That reply is the delivery.
- A subagent that reuses a worktree restores its temporary probes and reports the final
  worktree status unless asked to retain them. Before a heavyweight cargo command it
  reports the exact command and expected weight to the orchestrator.

## Writing Chelis Source

Load the [`example-corpus` skill](agent-skills/example-corpus/SKILL.md) before writing
any `.ch`; it carries the Surf style rules, the parse-breaking spellings, and the Deep
AST contract. `spec/02-surf-syntax.md` §0.1 is the authority.

- `chelis build`, `check`, `validate`, and `eval --file` run `chelis fmt --check` and the
  blocking `chelis lint` rules before the front end; style failures block the build.
  `--allow-style-violations` is for emergency local builds only, never CI, and
  `CHELIS_STYLE_GATE_DISABLE=1` is reserved for the integration-test corpus. Run
  `chelis fmt --inplace <file>` and `chelis lint --check` before pushing.
- Type system: no implicit precision promotion, named tensor dimensions match by name,
  no implicit broadcasting (explicit `expand` only), integer literals default to `i32`
  and float literals to `f32`.
- `chelis build` invokes the native compiler for C, HIP, or Metal and produces an
  executable or static library, retaining sources and runtime artifacts. `--emit-c`
  stops after source emission. CPU is the acceptance priority; GPU targets remain
  prerelease. See `docs/book/src/backends.md`.

<!-- END CHELIS MANAGED BLOCK: agents-inheritance -->

<!-- shell-local:exclude:begin -->
<!-- ### Red Team Rounds -->
<!-- ### Pull Request Lifecycle -->
<!-- ## Spec Authority And Design Discipline -->
<!-- ## Change Hygiene -->
<!-- ## Issue Tracking -->
<!-- ### Worktree And Branch Discipline -->
<!-- ### Python And Scripts -->
<!-- ### Build And Gate Commands -->
<!-- ## Pointers -->
<!-- ## The Chelis-Lang Repositories -->
<!-- shell-local:exclude:end -->

## Economoist Red Team Rounds

Use [`redteam-exec`](agent-skills/redteam-exec/SKILL.md) for every PR before
merge, including documentation changes. Start with a fresh local reviewer on
the pushed exact head, keep that reviewer through local repair verification,
and push a repair only after the reviewer is satisfied. The skill owns round
caps, finding scope, and brief content. For each handoff, record the worktree
HEAD and full status, worktree list, and process ownership as specified by the
shell-local skill block. A dirty or busy worktree is unavailable for reuse.

## Economoist Worktrees

- Treat the primary checkout as read-only developer state. Create a dedicated
  worktree for each task and create its Python 3.11 environment with
  `uv venv --python 3.11 .venv`; do not reuse an unrelated worktree or share
  one with a reviewer during writes.
- Do not use the clone-wide stash. Park task work in a task-owned commit or
  scratch location. Before removing a merged PR worktree, check its status and
  process ownership and preserve anything uncertain. Then use
  `git worktree remove <path>` for that worktree; branch removal is separate.

## Honesty Boundaries

The book states where each result stops: its Boundaries page covers all
three boundaries below, and each model page's Scope section applies them to
that model. Comments in `src/` and `properties/` state the same limits next
to the code. The proven fact is never silently generalized past
what the SMT call established. Issue citations for held-out claims stay in
source comments and maintainer docs, never in the book. Three boundaries are
mandatory:

- **Single-step vs limit/convergence.** A green on a one-step contraction or
  monotonicity is not a green on the fixed point, the limit, or the
  convergence of the iteration. The limit claim needs a checked fixed-point argument and is held
  out (chelis#2829). State the single-step fact as exactly that.
- **Fixed dimension vs general-n.** A green proven at `n = 2` or `n = 3` is
  an instance, not the universal theorem over all `n`. The general-n claim is
  held out alongside convergence. Greens are fixed-dimension instances; say so
  at the property.
- **Reals vs floats.** The proven fact is a statement of real arithmetic, as
  discharged by cvc5 over the reals. It is not a statement about `f32`
  evaluation. Floating-point behavior of any executable demo is a separate,
  unproven concern.

## Book

`docs/book/` is the user-facing book for this shell. chelis.ch mirrors it
page for page (https://chelis.ch/docs/economoist/), and the chelis.ch text is
canonical: book pages are rendered from the site by the website's
`scripts/sync_books.py`, so edit prose on the site and re-render, or make the
same edit in both places in the same change.

The reader is an engineer, or an AI coding agent, writing Chelis code against
this shell. They know the domain but not this repo's internals or history, and
they want to call the API correctly the first time. Every page teaches: what the
API does, a runnable example with its real output, the contract (inputs, domain,
shapes, precision, errors) and the pitfalls.

Never in the book: issue or PR numbers, repo-internal paths (`spec/`, `src/`
internals, `scripts/`, `tests/`, maintainer docs), maintainer or CI commands,
contributor history, process talk (gates, red teams, agent instructions),
status words (planned, not yet, stub, phase, milestone), "see the source" in
place of documentation, em-dashes, and the word "load-bearing".
`scripts/check_book.py` enforces the mechanical part in CI.

A change that alters the public API updates the book in the same PR.

## Toolchain Policy

- `reef.toml` is authoritative for the compiler pin, `chelis-std`
  dependency, and package version. Workflow pin pairs repeat the compiler
  version; `reef.lock` records all three, and the C Note manifest repeats
  the compiler and package versions. Consistency checks guard each copy.
  The Economoist package version is independent of the compiler pin.
- A single released `chelis` binary drives `fmt`, `lint`, `reef build`,
  `eval`, and `prove`. `chelis reef setup` installs the `reef.toml` pin and
  locked dependencies; the local and CI proof gates run that release binary.
- Never vendor or build the chelis compiler into this shell. Consume the released
  tarball for everything, `prove` included.
- Coordinate compiler bumps across Chelis shells as a release wave. Each
  shell lands its own pin-bump PR; do not leave Economoist's pin behind.
- CI downloads the public Chelis release with its GitHub token.

## Pin Bump Checklist

A pin bump is a **de-narrowing event**, not a version edit. Run all of it in
one change set:

1. Update **every** pin location: `reef.toml` plus each workflow's
   `CHELIS_TAG`/`CHELIS_VERSION` env pair. Verify with the offline pin check
   (`scripts/audit_workarounds.py --pins-only`). Install the toolchain and
   locked dependencies with `chelis reef setup`.
2. Run the blocked-probe suite. **FIX-detected** means the upstream bug is
   gone: execute the sidecar's de-narrowing instructions, promote the probe
   to a real test, and archive the matching `UPSTREAM_BUGS` entry. **DRIFTED**
   means the failure mode moved; investigate before re-citing.
3. Run the staleness audit; triage every CLOSED-but-still-cited workaround
   site. Retire it, or re-cite the live residue issue. No silent carryover.
4. Re-probe every `UPSTREAM_BUGS` entry whose trigger names this release,
   **per-surface**. A changelog claim is not a verification. Blockers the
   probe suite cannot express are re-probed manually here.
5. Refresh `docs/CHELIS_SURFACE.md`: the header versions and every
   `@pin`/`@upstream` column.
6. Promote `UPSTREAM_BUGS` entries per the re-probe verdicts (to Archived, or
   back to Tracking with the residue recorded).
7. Run the **complete local gate** before pushing: fmt, lint, the package
   build (`reef build` catches package-context errors that per-file lint and
   test miss), tests, negative tests, blocked probes, and the **SMT prove
   gate**.

## Upstream Bugs

See `docs/UPSTREAM_BUGS.md` for the actively blocking, tracking, and
archived inventory and its per-section re-probe cadence.

**Narrowing-citation rule.** Any narrowing in code or spec (a `fail(...)`
guard on input the reference accepts, a fixed shape, a fixed dimension, a
forward-only path) cites, **at the narrowing site**, the live `chelis#NNN`
or a citeable registry sibling issue. A prose name cannot be checked by the
citation audit.

## Characterization Contract and Canon Surface

The cross-repo characterization seam is frozen at
[C Note characterization contract](https://github.com/Chelis-Lang/c-note/blob/main/docs/contracts/characterization_contract_v1.md)
(schema `chelis-shell.invariant-surface/1.0`). Economoist's producer
obligations under it:

- `docs/cnote-import-surface.json` is the invariant manifest with stable model
  and property IDs, per-pin `expected_tier_per_pin` values, and controls. At
  release, `release.yml` copies the then-current manifest byte-for-byte into a
  versioned asset, which C Note vendors. A checkout edit does not update an
  older published asset or its vendored copy. Coordinate changes to consumer
  semantics before release.
- `scripts/contract_gate.py` checks schema, pin, property and control
  resolution, guards, and required citations offline.
- `scripts/prove_gate.py` checks the manifest against the pinned release.
  Classification uses `proof_tier`, assumption discharges, and `qualifiers`,
  never a favorable `composite_verdict` string. A changed proof result fails.

**Proof and sampled split (Economoist-specific divergence).** `properties/`
contains only unqualified real-arithmetic SMT results. Concrete Gordon `f32`
AD checks live in `sampled/` (module prefix `Economoist.Sampled`), require
`proof_tier == "fuzz"` and expected result `fuzz_validated`, and cannot be
counted as a `properties/` proof. For an imported output function the gate
requires an exact property-to-function declaration edge in the complete
linker-owned `dependency_graph`; missing attribution fails closed. This
per-directory split is Economoist's recorded divergence from mixed-result
shells.

## Shared Local Skills

Project-local skills live in `agent-skills/`. `.claude/skills` and
`.codex/skills` are symlinks to that directory so both tool surfaces load the
same skill library. `.claude/commands/` and `.codex/commands/` mirror each
other. The nine shared skills (`redteam-exec`, `spec-sync`, `phase-gate`,
`backend-numerics`, `example-corpus`, `cli-surface`, `packaging-install`,
`issue-resolution`, `chelis-std`) are materialized from the pinned toolchain by
`chelis reef conform sync`; `agent-skills/UPSTREAM.toml` records the set.
The `red-team` alias stays wired to `redteam-exec`. Change a shared skill
upstream first, then sync it here. Never fork a shared skill in place.

## Scaffolding Drift Rule

All Chelis shell repos share the same scaffolding shape by design. Any
structural change to this repo (layout, CI workflow, agent surface, reef
manifest format) is mirrored into the other shells in the same change set, or
explicitly flagged as a per-repo divergence with a recorded reason. Changes
to the downstream shell contract land in the chelis monorepo first; this
shell then conforms.

Install the local git hooks with:

```sh
git config core.hooksPath ./hooks
```

The per-PR checks in `.github/workflows/ci.yml` run pin, authorship,
manifest, formatting, lint, build, and negative/blocked suites. The full
`scripts/run_local_gate.py` also runs the SMT proof gate, corrupt-model checks,
and numeric oracle before each push; nightly repeats the expensive proof work.
