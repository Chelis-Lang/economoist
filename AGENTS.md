# Economoist Agent Contract

Canonical agent instructions for this repository. `CLAUDE.md` is a symlink
to this file so Claude-style and Codex-style entry points do not drift.

## Repo Identity

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
  `AGENTS.md` applies here **verbatim** unless explicitly overridden below,
  and the downstream shell contract applies in full. The machine-local
  environment sections of the monorepo `AGENTS.md` (workstation runbooks,
  first-exec notes, workstation-specific measurements) bind only where the
  named environment actually exists.

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

## Shared Local Skills

Project-local skills live in `agent-skills/`. `.claude/skills` and
`.codex/skills` are symlinks to that directory so both tool surfaces load the
same skill library. `.claude/commands/` and `.codex/commands/` mirror each
other. The shared skill set (`redteam-exec`, `spec-sync`, `phase-gate`,
`backend-numerics`, `example-corpus`, `cli-surface`) and the `red-team` alias
wired to `redteam-exec` are copied from the monorepo and stay behaviorally
aligned with it. A change to a shared skill lands in the monorepo first, then
propagates here. Never fork a shared skill in place.

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
action and runs per-PR, the same release-binary path the sibling shells use. The
offline pin guard now recognizes composite-action installs (the
`actions/install-chelis` marker in `scripts/audit_workarounds.py`); mirror that
marker into the sibling shells' pin guards per this rule.
