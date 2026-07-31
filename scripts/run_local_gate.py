#!/usr/bin/env python3
"""Run the Economoist local acceptance gate.

Invokes, in order:

  1. ``chelis fmt --check`` over every ``.ch`` file in ``src/``,
     ``properties/``, ``demos/``, ``sampled/``, ``tests/``.
  2. ``chelis lint --check`` over the same set of ``.ch`` files.
  3. ``chelis reef build`` for package-level compiler validation.
  4. ``chelis test tests/`` for the native unit suite.
  5. Native negative adapter (``chelis test tests_neg --expect neg``): every
     ``.ch`` under ``tests_neg/`` must fail with its pinned diagnostic.
  6. Native blocked adapter (``chelis test tests_blocked --expect blocked``):
     every executable probe must still fail with its pinned diagnostic (a
     now-passing probe surfaces as FIX-detected). The stage is skipped when
     there are no executable blocked probes at the current pin.
  7. ``scripts/contract_gate.py`` (offline manifest consistency).
  8. ``scripts/prove_gate.py`` (SMT keystone gate, release binary).
  9. ``scripts/run_forge_tests.py`` (metamorphic anti-vacuity forge negatives).
  10. ``scripts/oracle_harness.py`` (numeric oracle).

Stages 7-10 are conditional on their script existing, so the gate is
usable before those harnesses land. A stage whose source directory holds
no ``.ch`` files yet is skipped with a printed notice rather than failing.

The ``chelis`` binary is taken from the ``CHELIS_BIN`` environment
variable, then the reef.toml-pinned release install
(``~/.local/share/chelis/<pin>/bin/chelis``), then ``chelis`` on PATH.
SMT ships in the release binary, so one binary drives every stage.

Exits 0 only if every stage that ran succeeds.

Per-PR CI (``.github/workflows/ci.yml``) mirrors only stages 1-3, 5, 6
(the ``Chelis gate`` job: fmt + lint + reef build + negative tests +
blocked probes) and stage 7 (the offline ``contract-gate`` job) -- this is
the LEAN per-PR gate. Stages 8-9 (``scripts/prove_gate.py``, the SMT
keystone, and its metamorphic anti-vacuity forge negatives) do NOT run
per-PR: an audit found this pair costing every PR ~5-9 min of real-SMT
wall, so both moved to ``.github/workflows/nightly.yml`` (the ``prove``
job, daily + ``workflow_dispatch``, pinned RELEASE toolchain), alongside
stage 10 (the oracle harness). This local gate still runs every stage
before push, regardless of which CI workflow covers it.

Usage:

    python3 scripts/run_local_gate.py [--quiet]

This script lives in Python per the repo policy that prohibits shell
scripts.
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
import re
from pathlib import Path
from shutil import which

REPO_ROOT = Path(__file__).resolve().parents[1]


def _resolve_bin() -> str:
    """Resolve a chelis binary matching the reef pin, so a stale `chelis` on
    PATH (a different version) is not used. SMT ships in the release binary
    (chelis#422 resolved at v0.11.0), so there is no separate from-source smt
    binary to prefer."""
    for env in ("CHELIS_BIN", "CHELIS_SMT_BIN"):
        v = os.environ.get(env)
        if v and (Path(v).expanduser().is_file() or which(v)):
            return str(Path(v).expanduser())
    m = re.search(r'compiler\s*=\s*"=([^"]+)"', (REPO_ROOT / "reef.toml").read_text())
    if m:
        base = Path.home() / ".local/share/chelis" / m.group(1)
        for cand in (base / "bin" / "chelis", base / "chelis"):
            if cand.is_file():
                return str(cand)
    if which("chelis"):
        return "chelis"
    sys.exit("error: no chelis binary found; set CHELIS_BIN")


def _assert_version(binary: str) -> None:
    """Post-resolution guard: the resolved binary must be the reef-pinned version."""
    m = re.search(r'compiler\s*=\s*"=([^"]+)"', (REPO_ROOT / "reef.toml").read_text())
    if not m:
        return
    got = subprocess.run([binary, "--version"], capture_output=True, text=True).stdout.strip()
    if got != f"chelis {m.group(1)}":
        sys.exit(f"run_local_gate: resolved binary reports {got!r}, expected 'chelis {m.group(1)}' (reef pin); set CHELIS_BIN")


CHELIS = _resolve_bin()
_assert_version(CHELIS)

# Directories swept by fmt/lint, in stage order.
SOURCE_DIRS = ["src", "properties", "demos", "sampled", "tests"]


def run(cmd: list[str], *, quiet: bool) -> int:
    """Run a subprocess, return its exit code. Streams output on failure."""
    if not quiet:
        print(f"  $ {' '.join(cmd)}", flush=True)
    result = subprocess.run(cmd, cwd=REPO_ROOT, capture_output=True, text=True)
    if result.returncode != 0:
        sys.stdout.write(result.stdout)
        sys.stderr.write(result.stderr)
    return result.returncode


def ch_files_in(dirname: str) -> list[Path]:
    d = REPO_ROOT / dirname
    return sorted(d.glob("*.ch")) if d.exists() else []


def ch_files_under(dirname: str) -> list[Path]:
    d = REPO_ROOT / dirname
    return sorted(d.rglob("*.ch")) if d.exists() else []


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--quiet", action="store_true", help="suppress per-file lines")
    args = parser.parse_args()
    quiet = args.quiet

    print("[1/10] chelis fmt --check")
    fmt_any = False
    for dirname in SOURCE_DIRS:
        for path in ch_files_in(dirname):
            fmt_any = True
            rel = path.relative_to(REPO_ROOT)
            rc = run([CHELIS, "fmt", "--check", str(rel)], quiet=quiet)
            if rc != 0:
                print(f"FAIL: chelis fmt --check {rel}")
                return rc
    if not fmt_any:
        print("  notice: no .ch files under src/ properties/ demos/ sampled/ tests/; skipping fmt")

    print("[2/10] chelis lint --check")
    lint_targets = [f"{d}/" for d in SOURCE_DIRS if ch_files_in(d)]
    if lint_targets:
        rc = run([CHELIS, "lint", "--check", *lint_targets], quiet=False)
        if rc != 0:
            print("FAIL: chelis lint --check")
            return rc
    else:
        print("  notice: no .ch files under src/ properties/ demos/ sampled/ tests/; skipping lint")

    print("[3/10] chelis reef build")
    rc = run([CHELIS, "reef", "build"], quiet=False)
    if rc != 0:
        print("FAIL: chelis reef build")
        return rc

    print("[4/10] chelis test tests/")
    if ch_files_in("tests"):
        rc = run([CHELIS, "test", "tests/"], quiet=False)
        if rc != 0:
            print("FAIL: chelis test tests/")
            return rc
    else:
        print("  notice: no .ch files under tests/; skipping test stage")

    print("[5/10] native negative tests")
    if ch_files_under("tests_neg"):
        rc = run([CHELIS, "test", "tests_neg", "--expect", "neg"], quiet=False)
        if rc != 0:
            print("FAIL: chelis test tests_neg --expect neg")
            return rc
    else:
        print("  notice: no .ch files under tests_neg/; skipping negative-test stage")

    print("[6/10] native blocked probes")
    if ch_files_under("tests_blocked"):
        rc = run([CHELIS, "test", "tests_blocked", "--expect", "blocked"], quiet=False)
        if rc != 0:
            print("FAIL: chelis test tests_blocked --expect blocked")
            return rc
    else:
        print("  notice: no executable blocked probes at this pin; skipping blocked stage")

    print("[7/10] contract gate (manifest consistency, offline)")
    if (REPO_ROOT / "scripts" / "contract_gate.py").exists():
        rc = run([sys.executable, "scripts/contract_gate.py"], quiet=False)
        if rc != 0:
            print("FAIL: scripts/contract_gate.py")
            return rc
    else:
        print("  notice: scripts/contract_gate.py not present yet; skipping")

    print("[8/10] prove gate (keystone, release binary)")
    if (REPO_ROOT / "scripts" / "prove_gate.py").exists():
        rc = run([sys.executable, "scripts/prove_gate.py"], quiet=False)
        if rc != 0:
            print("FAIL: scripts/prove_gate.py")
            return rc
    else:
        print("  notice: scripts/prove_gate.py not present yet; skipping")

    print("[9/10] forge negatives (metamorphic anti-vacuity)")
    if (REPO_ROOT / "scripts" / "run_forge_tests.py").exists():
        rc = run([sys.executable, "scripts/run_forge_tests.py"], quiet=False)
        if rc != 0:
            print("FAIL: scripts/run_forge_tests.py")
            return rc
    else:
        print("  notice: scripts/run_forge_tests.py not present yet; skipping")

    print("[10/10] oracle harness")
    if (REPO_ROOT / "scripts" / "oracle_harness.py").exists():
        rc = run([sys.executable, "scripts/oracle_harness.py"], quiet=False)
        if rc != 0:
            print("FAIL: scripts/oracle_harness.py")
            return rc
    else:
        print("  notice: scripts/oracle_harness.py not present yet; skipping")

    print("OK: economoist local gate green")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
