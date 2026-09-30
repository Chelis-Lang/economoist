# Chelis 0.18.12 migration

Economoist 0.2.14 moves directly from Chelis 0.18.10 to the published
0.18.12 release. The package and three workflow pins, bundled `chelis-std`
lock, managed agent contract and skills, and C Note manifest agree at this pin.
Economoist did not publish a package at 0.18.11.

The official tag points to commit
`c81d8188de6ebad032c1bb1c0a427eb0408feee3` (tag workflow
`36769966221`). On this Darwin arm64 host,
`scripts/install_chelis_toolchain.py --skip-launcher` downloaded
`chelis-v0.18.12-darwin-arm64.tar.gz`, checked its release checksum sidecar,
and installed the binary at `~/.local/share/chelis/0.18.12/bin/chelis`.
The archive SHA-256 is
`8cdcbf598c3f04e37a9a211e7abaa67fbaf6d4c135a34f00c1944b1e43b8e90d`;
the installed binary SHA-256 is
`b0df096e2b43eb28d4a40138fdcc2f8807d39bffeab5b2145e639f5b9d4d3351`
and reports `chelis 0.18.12`. The installer now selects the native Darwin
arm64 asset on this host and can leave an existing global launcher untouched.

With `reef.lock` removed from the task worktree after saving a copy, the
official binary's `chelis reef build` regenerated a byte-identical lock.
Its only dependency is `chelis-std` 0.4.0 from `bundled` source at compiler
0.18.12, with archive hash
`59cb08f67e4ca0b139b87336414fd050a1d3c082ceeeae9ce15b2318d45ad913`
and shell hash
`f780fab3dfdf545a1e35821e30ad7e020a81cead75951b6a67754e6d7c9cb9d9`.
There are no local-registry entries.

The blocked diagnostic sentinel and negative test retain their expected
failure classifications on the official binary. No active or tracking
`UPSTREAM_BUGS.md` entry has a 0.18.12 re-probe trigger. The parked Beacon
surface still returns eight structured `unsupported` Gordon-property records
under `--tier beacon-only`, with the named rank-zero tensor[f64] input
requirement; that command exits 2 for unsupported results. No model, property,
sampled source, numeric golden, or expected tier changed: nine invariants
remain SMT `proven` and one concrete AD invariant remains `fuzz_validated`.

On 2026-09-30, with `CHELIS_BIN` set to the installed release binary and an
isolated `CHELIS_REEF_HOME`, `.venv/bin/python scripts/run_local_gate.py
--quiet` passed all ten stages: formatting, lint, package build, native
tests, negative tests, blocked probes, C Note contract, SMT proof controls,
forge negatives, and numeric oracle. `chelis reef conform audit --explain`
reported no MUST failures, `chelis reef conform bump-check --base origin/main`
passed, `scripts/audit_workarounds.py --pins-only` guarded all three
workflows, and `scripts/contract_gate.py` checked seven models and ten
invariants. The installer regression suite passed twelve tests.
