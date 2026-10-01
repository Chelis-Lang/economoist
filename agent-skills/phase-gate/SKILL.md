---
name: phase-gate
description: Use when deciding whether a Chelis phase is actually complete. Applies the repo’s completion standard, checks manual gates, examples, docs, and phase-specific acceptance criteria before any completion claim.
---

# Phase Gate

Use this skill when a phase is claimed complete or nearly complete.

## Acceptance Oracle

Before judging a phase, identify its single authoritative oracle:

- one command
- one named suite
- or one documented manual validation runner

Treat all other evidence as supporting material, not the completion decision itself.

## Completion Rule

Do not call the phase complete if any of these remain:

- broken default gate
- missing or ambiguous phase oracle
- hidden manual-only acceptance criteria not documented as such
- false-perfect machine-facing reports
- examples/docs whose meaning contradicts the actual implementation
<!-- shell-local:begin -->
<!-- shell-local:exclude:begin -->
<!-- ## Default Gate -->
<!-- ## Additional Required Checks -->
<!-- shell-local:exclude:end -->

## Economoist Default Gate

Run `.venv/bin/python scripts/run_local_gate.py` in a dedicated worktree with
the `reef.toml`-pinned released Chelis binary. It covers formatting, linting,
package build, tests, negative and blocked probes, the contract and SMT proof
gates, forge negatives, and the numeric oracle. Run
`chelis reef conform audit --explain` for the inherited shell contract. For a
phase or property completion claim, also run its named acceptance oracle;
green PR CI alone does not establish that claim.

## Economoist Required Checks

- Identify the claimed property and its expected result in
  `docs/SUMMARY.md` and `docs/cnote-import-surface.json`; check the gate's
  result against that exact scope.
- Execute any documented manual acceptance command and verify that ignored
  tests have an explicit reason and runner.
- Check executable models and demos, and confirm that the docs distinguish
  single-step results from convergence, fixed dimensions from general
  dimensions, and proof over reals from floating-point behavior.
<!-- shell-local:end -->
