# Economoist Agent Contract

Canonical agent instructions for this repository. `CLAUDE.md` is a symlink
to this file so Claude-style and Codex-style entry points do not drift.

## Repo Identity

<!-- BEGIN CHELIS MANAGED BLOCK: agents-inheritance chelis@0.18.12 (sha256:ba2c4adc45022f00) -->
# Chelis Agent Contract

Keep this file concise and relevant to every agent working in this repository.
Each added token is read tens of thousands of times. State a rule once, link the
document that owns the detail, and put the explanation in that document, not here.

`CLAUDE.md` is a symlink to this file so Claude-style and Codex-style entry points do
not drift.

## What Chelis Is

Chelis is a functional language for AI research, built for a workflow where a coding
agent is the primary author and a human is the supervisor, and where the programs are
themselves AI systems: models, training loops, search spaces, learned functions. The
bet is that a type system, representation, and compilation model designed around AI
primitives from the start beat ones bolted onto Python or a systems language later. It
is not a general-purpose language, a systems language, a web framework, or a Python
replacement. `spec/00-context.md` and `spec/design/chelis_canonical_reference.md` own
the full statement; their specifics may lag, their intent does not. When a tradeoff
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

### Red Team Rounds

Run every round through the [`redteam-exec` skill](agent-skills/redteam-exec/SKILL.md).
It carries the brief shape, the worktree-reuse rules, and the verify mode.

- Red team against the spec, the code, the tests, the examples, and the CLI behavior.
  Execute tests and commands; source inspection is not proof.
- Every pull request, documentation-only work included, gets at least one round before
  merge. A round is the whole live back-and-forth between one reviewer and the author,
  not a single review pass:
  1. A fresh local subagent reviews the exact head from an inline brief and reports
     its findings.
  2. The reviewer stays alive. The author repairs the findings in the worktree.
  3. The author hands the repair back, and the same reviewer verifies it and looks for
     similar issues the repair may have missed or introduced.
  4. Any further finding goes back to the author, and steps 2 and 3 repeat.
  5. The round ends only when that reviewer states it is satisfied.
  A reviewer that has reported is not finished; it is waiting for the fix. Ending the
  loop after the first report, or verifying a repair with a different reviewer, is not
  a round.
- A pull request gets at most three fresh rounds; a fourth needs the user's explicit
  approval. A prose-only pull request gets one, and a second needs the same approval.
  The pull request's round record is the counter. Verification by the standing reviewer
  does not count; the end-of-pull-request round does.
- A finding is in scope only when the pull request introduces it, worsens it, or claims
  to correct it. Discovery during review does not bring a pre-existing defect into scope.
- A confirmed in-scope P0 or P1 merits a fresh round after the current round finishes,
  within the cap. Unmigrated assertions, old comments, and minor documentation drift do
  not. A rebase does not by itself merit a round: send a hand-resolved intersection that
  stays within files the standing reviewer already read to that reviewer for focused
  verification, and use a fresh round only when the rebase introduces a new mechanism or
  touches files that reviewer did not read. A targeted review of substantial rebase
  overlap needs no permission and never counts toward the cap.
- For documentation and design reviews, severity follows contract impact. A wrong
  normative rule, or a plan that cannot close a named in-scope deliverable, is P0 or P1.
  A design document that misdescribes current `main`, or exposes a sequencing seam while
  the contract stays achievable, is P2 or P3 and is recorded as residual work, never
  promoted to a merge blocker. Wording, line-level accuracy of the pull request body,
  staleness against a sibling pull request's moving head, and anything whose fix would
  add text without a necessity sentence are out of scope.
- State a pull request's claim at the granularity its oracle proves. An unbounded
  universal claim invites sampling in every round and can never be closed.
- A finding class is the defect category, not its file, line, or wording instance.
  Every round record names the class of each finding. When two consecutive rounds
  report the same class, or replace a repaired finding with a different class, stop
  patching witnesses: change the representation, the oracle, the claim, or the brief
  before running another round.
- Repairs may correct, remove, or narrow the pull request's content. They must not add
  design scope, mechanisms, inventories, or promises merely to absorb a finding. When a
  correction would need that, reduce the claim and track the rest outside the pull
  request.
- Freshness is a property of the reviewer's context, not the filesystem. Hand a
  reviewer an existing worktree and its warm target only when it is at the exact review
  head, has a known clean baseline, and has no concurrent writer, and paste the output of
  `.venv/bin/python scripts/worktree_status.py` into the brief as the evidence. Unknown
  or not-clean means wait, and free is the probe's best answer rather than a proof: a
  run that takes no lease, `--fast` among them, is caught only by a scan of the
  processes it spawned. A reviewer whose probes mutate tracked source gets its own
  worktree, and you never edit a worktree a reviewer is reading.
- Before spawning a fresh round, retire only your own stale or failed subagent handles;
  a standing reviewer awaiting a fix is neither. If a spawn routes to remote
  infrastructure, errors, or comes back broken, retire it and retry until you have a
  working fresh local subagent, or state that red-team validation is blocked.

## Environment And Tooling

### Worktree And Branch Discipline

- The primary checkout (the main worktree in `git worktree list --porcelain`) is live
  developer state. Read-only queries are fine there; never switch branches, edit, build,
  or create scratch artifacts in it.
- Create a dedicated worktree before the first write of every task, including small
  documentation edits and throwaway probes, and give it its own `.venv` with
  `uv venv --python 3.11`; never copy or symlink another checkout's `.venv`.
- A worktree isolates the working tree, the index, and its HEAD reflog. The stash
  stack, `.git/info/exclude`, the hooks directory, and branch reflogs are shared by
  every worktree on the clone. Do not run `git stash` in a shared clone: to discard your
  own changes use `git checkout -- <paths>`; to park them, copy the files to task-owned
  scratch space or commit them on your branch.
- Do not repurpose an unrelated worktree because it appears idle. Reuse only for the
  same PR or immediate follow-up after checking ownership, exact head, status, and active
  processes. Never share a worktree with a reviewer while either of you writes to it.
- After a PR merges, remove its worktree and task-owned target with individual
  `git worktree remove <path>` and `cargo clean --target-dir <path>` commands, never a
  blanket loop, after confirming the PR is merged, nothing uncommitted is worth keeping,
  and no process owns the target. Squash merges mean "commits ahead of `origin/main`"
  proves nothing; compare patch ids when in doubt. Branch deletion is a separate decision.

## Subagents

[`docs/investigations/agent_contract_rationale.md`](docs/investigations/agent_contract_rationale.md)
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
- `chelis build` emits C, a header, runtime artifacts, and compile flags; `--target hip`
  emits host code with embedded kernel strings. Neither invokes the native compiler.

## Pointers

- **Shared skills** live in `agent-skills/`; `.claude/skills` and `.codex/skills` are
  symlinks to that one authored tree, `.claude/commands/` and `.codex/commands/` stay byte-identical, and the
  `red-team` alias is wired to `redteam-exec` with its fresh-round and verify modes. The
  set: `redteam-exec`, `spec-sync`, `phase-gate`, `backend-numerics`, `example-corpus`,
  `cli-surface`, `packaging-install`, `issue-resolution`.
- **Toolchain and packaging.** `chelisup` is the installer and pin-resolving `chelis`
  shim; `chelis reef setup` is the orchestrator. Use the
  [`packaging-install` skill](agent-skills/packaging-install/SKILL.md) for any change
  there. One trap it enforces at compile time: `reef setup` subprocesses the real
  `chelisup` binary, never `chelisup::install::install` in-process, because that helper
  copies `current_exe()` over the shim. Design:
  [`spec/design/chelis_packaging_and_install.md`](spec/design/chelis_packaging_and_install.md).
- **Downstream shells** inherit this complete contract through a stamped managed block
  and must satisfy [`spec/design/shell_repo_contract.md`](spec/design/shell_repo_contract.md),
  shipped in the toolchain as `chelis reef conform`. Full inheritance is the default,
  but each shell decides which portions apply. Shell-owned additions stay outside the
  block and should remain when they are relevant and current. To omit an inherited
  section, put its exact ATX heading in a shell-owned span such as
  `<!-- shell-local:exclude:begin -->`,
  `<!-- ### Numeric Surface Discipline -->`, `<!-- shell-local:exclude:end -->`; sync
  removes that heading and its section, while deleting the selector restores it. The
  root `# Chelis Agent Contract` selector omits the entire inherited body.
  Contract changes land here first, editing the doc and the conformance
  `MANIFEST`/`REGISTRY` in lockstep. §7.1 of that doc is the audit a `conform bump` wave
  still owes after the mechanical starter runs.
<!-- END CHELIS MANAGED BLOCK: agents-inheritance -->

<!-- shell-local:exclude:begin -->
<!-- ### Pull Request Lifecycle -->
<!-- ## Spec Authority And Design Discipline -->
<!-- ## Change Hygiene -->
<!-- ## Issue Tracking -->
<!-- ### Python And Scripts -->
<!-- ### Build And Gate Commands -->
<!-- ## The Chelis-Lang Repositories -->
<!-- shell-local:exclude:end -->

- Economoist is a downstream **shell repo** for the
  [Chelis](https://github.com/Chelis-Lang/chelis) language, scoped to
  verified economic and dynamic-programming models. It is the
  academic-launch surface for "C Proof".
- The intent is singular: every economic property this shell states is a
  genuine, unqualified SMT green (cvc5, over the reals, zero fuzz, no
  contract). An amber result, or one that only closes under a contract
  qualifier, is a bug to fix, not a result to ship. The repo exists to make
  that claim defensible to an academic reader, not to enumerate a
  deliverables list.
- **Domain bifurcation.** Economic content lives here. Finance and
  derivatives stay in [Shoals](https://github.com/Chelis-Lang/shoals).
  Economoist must never depend on Shoals; the two shells share scaffolding,
  not modules.
- **Upstream of truth** is `Chelis-Lang/chelis`. The Chelis monorepo's
  `AGENTS.md` is inherited through the managed block, with the exact-heading
  exclusions above for compiler-only and monorepo-only procedures. The
  downstream shell contract applies in full. The machine-local
  environment sections of the monorepo `AGENTS.md` (workstation runbooks,
  first-exec notes, workstation-specific measurements) bind only where the
  named environment actually exists. For red-team worktree evidence, use
  this shell's worktree status and process checks; the inherited
  `scripts/worktree_status.py` example belongs to the compiler repo.

### Honesty boundaries

Every module's docs state, per property, where the green stops. The proven
fact is never silently generalized past what the SMT call established. Three
boundaries are mandatory:

- **Single-step vs limit/convergence.** A green on a one-step contraction or
  monotonicity is not a green on the fixed point, the limit, or the
  convergence of the iteration. The limit claim needs induction and is held
  out. State the single-step fact as exactly that.
- **Fixed dimension vs general-n.** A green proven at `n = 2` or `n = 3` is
  an instance, not the universal theorem over all `n`. The general-n claim is
  held out alongside convergence. Greens are fixed-dimension instances; say so
  at the property.
- **Reals vs floats.** The proven fact is a statement of real arithmetic, as
  discharged by cvc5 over the reals. It is not a statement about `f32`
  evaluation. Floating-point behavior of any executable demo is a separate,
  unproven concern.

## Toolchain Policy

- `reef.toml` is the **single source of truth** for the `chelis` and
  `chelis-std` pins and the package `version`. Do not duplicate any of those
  numbers anywhere else; tooling and CI read them from `reef.toml` directly.
  The Economoist package `version` track is its own and is not aligned to the
  compiler pin.
- **One-binary reality.** A single released `chelis` tarball drives every stage
  -- `fmt`, `lint`, `reef build`, `eval`, and `prove`. SMT ships in the released
  binary as of chelis v0.11.0 (chelis#422 resolved; verified at the 0.14.0 pin on
  2026-07-10, `scripts/prove_gate.py` fully green against
  `~/.local/share/chelis/<pin>/bin/chelis`). The tarball is consumed from the
  private `Chelis-Lang/chelis` releases and installed side-by-side under
  `~/.local/share/chelis/<pin>/` via `scripts/install_chelis_toolchain.py`.
- Never vendor or build the chelis compiler into this shell. Consume the released
  tarball for everything, `prove` included.
- Compiler bumps land in **every** Chelis shell in the same change set; do
  not bump Economoist unilaterally.
- CI authenticates to the private `Chelis-Lang/chelis` releases via the repo
  secret `CHELIS_RELEASE_TOKEN` (a PAT with `contents: read`).

## Pin Bump Checklist

A pin bump is a **de-narrowing event**, not a version edit. Run all of it in
one change set:

1. Update **every** pin location: `reef.toml` plus each workflow's
   `CHELIS_TAG`/`CHELIS_VERSION` env pair. Verify with the offline pin check
   (`scripts/audit_workarounds.py --pins-only`). Install the toolchain via
   the checked-in installer (`scripts/install_chelis_toolchain.py`).
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

See `docs/UPSTREAM_BUGS.md` for the active-blocking, tracking, parked, and
archived inventory and its per-section re-probe cadence.

**Narrowing-citation rule.** Any narrowing in code or spec (a `fail(...)`
guard on input the reference accepts, a fixed shape, a fixed dimension, a
forward-only path) cites, **at the narrowing site**, either `chelis#NNN` or a
parked draft under `docs/issue_drafts/`. Never a prose name: a prose-name
citation is invisible to every mechanical audit.

## Characterization Contract and Canon Surface

The cross-repo characterization seam is frozen at
[`c-note/docs/contracts/characterization_contract_v1.md`](../c-note/docs/contracts/characterization_contract_v1.md)
(schema `chelis-shell.invariant-surface/1.0`). Economoist's producer
obligations under it:

- `docs/cnote-import-surface.json` -- the invariant-surface manifest (models +
  invariants + per-pin expected tiers + controls). Published byte-identical as
  the release asset `economoist-<ver>.invariants.json` by `release.yml`; C Note
  vendors and freshness-gates that asset.
- `scripts/contract_gate.py` -- fast offline consistency gate (schema/pin
  freshness, property + control resolution, precondition/where-clause
  cross-check, tier citations).
- `scripts/prove_gate.py` -- the keystone: expected-tier enforcement off the
  manifest against the pinned RELEASE binary. An achieved tier is classified
  from `proof_tier` + assumption discharge + `qualifiers`, **never** from the
  `composite_verdict` string; tier drift in either direction fails.

**Two-lane split (flagged divergence).** Economoist keeps the `properties/`
tree as its pure unqualified-SMT-green boundary -- that green-only asymmetry vs
Shoals is the shell's identity and is contractual. Weaker-tier library
invariants (fuzz-validated AD sensitivities) live in a separate top-level
`sampled/` dir (module prefix `Economoist.Sampled`, in `reef.toml`
`additional_sources`), gated separately: `proof_tier == "fuzz"`, expected tier
`fuzz_validated`, name-linted, and never colliding with a `properties/` green.
Shoals instead hosts mixed tiers in `properties/` keyed on expected-tier; this
per-dir split is an Economoist divergence recorded here and in the contract doc
per the Scaffolding Drift Rule. Anti-vacuity for imported output fns is verified
from Chelis 0.17.2 onward by the linker-owned `dependency_graph`: the gate
requires an exact edge from the property declaration (package, module, source,
kind, and name) to the exact exported model function. Goal-string inspection is
only a compatibility oracle for older pins; the legacy flat `dependency_edges`
limitation is retained as a historical record in
`docs/issue_drafts/dependency_edges_imports.md`.

## Shared Local Skills

Project-local skills live in `agent-skills/`. `.claude/skills` and
`.codex/skills` are symlinks to that directory so both tool surfaces load the
same skill library. `.claude/commands/` and `.codex/commands/` mirror each
other. The eight shared skills (`redteam-exec`, `spec-sync`, `phase-gate`,
`backend-numerics`, `example-corpus`, `cli-surface`, `packaging-install`,
`issue-resolution`) are materialized from the pinned toolchain by
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

**Recorded convergence.** The SMT prove gate once required a from-source
`--features smt` build (an Economoist-specific `smt-prove-gate` job that cached a
`chelis-smt` binary per chelis tag). That narrowing is retired now that SMT ships
in the released binary (chelis#422, resolved v0.11.0): the prove gate installs the
pinned release toolchain via the shared `.github/actions/install-chelis` composite
action, the same release-binary path the sibling shells use. The offline pin
guard now recognizes composite-action installs (the `actions/install-chelis`
marker in `scripts/audit_workarounds.py`); mirror that marker into the sibling
shells' pin guards per this rule.

**Lean per-PR / real-SMT nightly.** The prove gate (`scripts/prove_gate.py`)
and its metamorphic anti-vacuity forge negatives (`scripts/run_forge_tests.py`)
do NOT run per-PR: an audit found this job costing every PR ~5-9 min of
real-SMT wall, the same anti-pattern the Scaffolding Drift Rule flagged in
Shoals (shoals#32). Both now run in `.github/workflows/nightly.yml` (the
`prove` job: daily + `workflow_dispatch`, pinned RELEASE toolchain) and in
`scripts/run_local_gate.py` before push. Per-PR CI (`.github/workflows/ci.yml`)
stays lean: `hard-rule-guard` + `no-ai-authorship` (offline), `contract-gate`
(offline manifest validation), and `Chelis gate` (fmt + lint + `chelis reef
build` compile signal + the fast negative-test/blocked-probe suites).
