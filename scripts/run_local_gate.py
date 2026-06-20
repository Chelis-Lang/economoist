#!/usr/bin/env python3
"""Run the Economoist local acceptance gate.

Invokes, in order:

  1. ``chelis fmt --check`` over every ``.ch`` file in ``src/``,
     ``properties/``, ``demos/``, ``tests/``.
  2. ``chelis lint --check`` over the same set of ``.ch`` files.
  3. ``chelis reef build`` for package-level compiler validation.
  4. ``chelis test tests/`` for the native unit suite.
  5. Negative tests (``python3 scripts/run_negative_tests.py``): every
     ``.ch`` under ``tests_neg/`` must fail with its pinned diagnostic.
  6. Blocked probes (``python3 scripts/run_blocked_probes.py``): every
     ``.ch`` under ``tests_blocked/`` must still fail with its pinned
     diagnostic (a now-passing probe surfaces as FIX-detected).
  7. ``scripts/prove_gate.py`` IF that file exists (SMT proof harness).
  8. ``scripts/oracle_harness.py`` IF that file exists (numeric oracle).

Stages 7 and 8 are conditional on their script existing, so the gate is
usable before those harnesses land. A stage whose source directory holds
no ``.ch`` files yet is skipped with a printed notice rather than failing.

The ``chelis`` binary is taken from the ``CHELIS_BIN`` environment
variable, defaulting to ``chelis`` on PATH; this lets the gate run against
the side-by-side smt binary at
``~/.local/share/chelis/0.8.0/chelis-smt``.

Exits 0 only if every stage that ran succeeds.

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
    PATH (a different version that cannot parse 0.8.0 syntax) is not used."""
    for env in ("CHELIS_BIN", "CHELIS_SMT_BIN"):
        v = os.environ.get(env)
        if v and (Path(v).expanduser().is_file() or which(v)):
            return str(Path(v).expanduser())
    m = re.search(r'compiler\s*=\s*"=([^"]+)"', (REPO_ROOT / "reef.toml").read_text())
    if m:
        for name in ("chelis-smt", "chelis"):
            cand = Path.home() / ".local/share/chelis" / m.group(1) / name
            if cand.is_file():
                return str(cand)
    for name in ("chelis-smt", "chelis"):
        if which(name):
            return name
    sys.exit("error: no chelis binary found; set CHELIS_BIN")


CHELIS = _resolve_bin()

# Directories swept by fmt/lint, in stage order.
SOURCE_DIRS = ["src", "properties", "demos", "tests"]


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


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--quiet", action="store_true", help="suppress per-file lines")
    args = parser.parse_args()
    quiet = args.quiet

    print("[1/8] chelis fmt --check")
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
        print("  notice: no .ch files under src/ properties/ demos/ tests/; skipping fmt")

    print("[2/8] chelis lint --check")
    lint_targets = [f"{d}/" for d in SOURCE_DIRS if ch_files_in(d)]
    if lint_targets:
        rc = run([CHELIS, "lint", "--check", *lint_targets], quiet=False)
        if rc != 0:
            print("FAIL: chelis lint --check")
            return rc
    else:
        print("  notice: no .ch files under src/ properties/ demos/ tests/; skipping lint")

    print("[3/8] chelis reef build")
    rc = run([CHELIS, "reef", "build"], quiet=False)
    if rc != 0:
        print("FAIL: chelis reef build")
        return rc

    print("[4/8] chelis test tests/")
    if ch_files_in("tests"):
        rc = run([CHELIS, "test", "tests/"], quiet=False)
        if rc != 0:
            print("FAIL: chelis test tests/")
            return rc
    else:
        print("  notice: no .ch files under tests/; skipping test stage")

    print("[5/8] negative tests")
    rc = run([sys.executable, "scripts/run_negative_tests.py"], quiet=False)
    if rc != 0:
        print("FAIL: scripts/run_negative_tests.py")
        return rc

    print("[6/8] blocked probes")
    rc = run([sys.executable, "scripts/run_blocked_probes.py"], quiet=False)
    if rc != 0:
        print("FAIL: scripts/run_blocked_probes.py")
        return rc

    print("[7/8] prove gate")
    if (REPO_ROOT / "scripts" / "prove_gate.py").exists():
        rc = run([sys.executable, "scripts/prove_gate.py"], quiet=False)
        if rc != 0:
            print("FAIL: scripts/prove_gate.py")
            return rc
    else:
        print("  notice: scripts/prove_gate.py not present yet; skipping")

    print("[8/8] oracle harness")
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
