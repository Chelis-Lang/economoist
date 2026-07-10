#!/usr/bin/env python3
"""Numerical oracle harness for Economoist (E6), stdlib only.

Two validation layers, kept distinct from the prover:
  1. The shell's displayed single-expression operators are evaluated through
     `chelis eval` and compared against recorded analytic-mirror goldens within a
     precision-derived tolerance. The eval expression is the identical body the
     module ships (single-expression discipline), with the local fmax helper
     inlined as the if/then/else it is defined as.
  2. The executable test suite under tests/ is run through `chelis test --json`,
     which exercises the real exported functions; it must report zero failures.

The goldens are recorded here once and compared against, never recomputed and
self-agreed: each analytic mirror is asserted to reproduce its recorded golden,
and the shell's eval output is compared to the same recorded golden. QuantEcon
is an out-of-band research cross-check, not a shipped dependency, so it is not
imported here (this gate is stdlib only).

The harness validates numbers. The structural properties are validated by the
prover (scripts/prove_gate.py). A matching number is not a proof.
"""

from __future__ import annotations

import json
import math
import os
import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]


def resolve_bin() -> str:
    """CHELIS_SMT_BIN/CHELIS_BIN override, else the reef.toml-pinned release
    install (~/.local/share/chelis/<pin>/bin/chelis, or the top-level layout),
    else `chelis` on PATH. SMT ships in the release binary since chelis v0.11.0
    (chelis#422 resolved); there is no separate from-source smt binary."""
    from shutil import which
    for env in ("CHELIS_SMT_BIN", "CHELIS_BIN"):
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
    sys.exit("error: no chelis binary found; set CHELIS_SMT_BIN or CHELIS_BIN")


def f32(x: float) -> str:
    return f"cast({x!r}, f32)"


# Displayed single-expression bodies, identical to the shipped module sources
# (Economoist.Markov.next_mass, Economoist.Growth.gordon_pv,
# Economoist.Bellman.bellman_state0 with fmax inlined as its if/then/else).
NEXT_MASS = ("(fn (p: f32, q: f32, ta: f32, tb: f32) -> ((p * ta) + (q * tb)))", ("p", "q", "ta", "tb"))
GORDON = ("(fn (d: f32, r: f32, g: f32) -> (d / (r - g)))", ("d", "r", "g"))
_A0 = "(r0 + (g * ((p00 * v0) + (p01 * v1))))"
_A1 = "(r1 + (g * ((p10 * v0) + (p11 * v1))))"
BELLMAN = (
    f"(fn (v0: f32, v1: f32, r0: f32, p00: f32, p01: f32, r1: f32, p10: f32, p11: f32, g: f32) -> "
    f"(if ({_A0} >= {_A1}) then {_A0} else {_A1}))",
    ("v0", "v1", "r0", "p00", "p01", "r1", "p10", "p11", "g"),
)


def mirror_next_mass(p, q, ta, tb):
    return p * ta + q * tb


def mirror_gordon(d, r, g):
    return d / (r - g)


def mirror_bellman(v0, v1, r0, p00, p01, r1, p10, p11, g):
    a0 = r0 + g * (p00 * v0 + p01 * v1)
    a1 = r1 + g * (p10 * v0 + p11 * v1)
    return max(a0, a1)


# Recorded goldens: at least two distinct configurations per operator, so no
# single golden stands in for an oracle (contract section 9).
CASES = [
    ("next_mass case A", NEXT_MASS, mirror_next_mass, (0.6, 0.4, 0.7, 0.2), 0.5),
    ("next_mass case B", NEXT_MASS, mirror_next_mass, (0.2, 0.8, 0.5, 0.25), 0.3),
    ("gordon_pv case A", GORDON, mirror_gordon, (2.0, 0.1, 0.05), 40.0),
    ("gordon_pv case B", GORDON, mirror_gordon, (3.0, 0.08, 0.03), 60.0),
    ("bellman_state0 case A", BELLMAN, mirror_bellman, (1.0, 2.0, 0.5, 0.7, 0.3, 0.4, 0.2, 0.8, 0.9), 2.02),
    ("bellman_state0 case B", BELLMAN, mirror_bellman, (0.0, 0.0, 1.0, 0.5, 0.5, 0.25, 0.5, 0.5, 0.5), 1.0),
]


def tol_for(expected: float) -> float:
    # f32 carries roughly seven significant digits.
    return max(1e-5 * abs(expected), 1e-5)


def eval_value(binary: str, lam: str, args: tuple) -> float:
    expr = lam[0] + "(" + ", ".join(f32(a) for a in args) + ")"
    proc = subprocess.run([binary, "eval", "--json", expr], capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(f"eval failed: {proc.stderr.strip()}")
    data = json.loads(proc.stdout)
    return float(data["roots"][0]["value"]["value"])


def run_tests(binary: str) -> tuple[int, int]:
    proc = subprocess.run([binary, "test", "tests/", "--json"], cwd=REPO_ROOT, capture_output=True, text=True)
    passed = failed = 0
    for line in proc.stdout.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rec = json.loads(line)
        except json.JSONDecodeError:
            continue
        if "summary" in rec:
            passed = rec["summary"].get("passed", 0)
            failed = rec["summary"].get("failed", 0)
    return passed, failed


def main() -> int:
    binary = resolve_bin()
    print(f"oracle_harness using {binary}")
    failures: list[str] = []

    for label, lam, mirror, args, golden in CASES:
        mirror_val = mirror(*args)
        if not math.isclose(mirror_val, golden, rel_tol=1e-9, abs_tol=1e-9):
            failures.append(f"{label}: analytic mirror {mirror_val} does not reproduce recorded golden {golden}")
            continue
        try:
            got = eval_value(binary, lam, args)
        except Exception as exc:  # noqa: BLE001
            failures.append(f"{label}: {exc}")
            continue
        tol = tol_for(golden)
        if abs(got - golden) > tol:
            failures.append(f"{label}: eval {got} differs from golden {golden} by more than {tol}")
        else:
            print(f"  OK  {label}: eval={got:.7g} golden={golden:.7g} tol={tol:.1e}")

    # E4 comparative statics: gate that the AD grad demo reproduces the signs the
    # SMT properties (gordon_dP_dr_negative, gordon_dP_dg_positive) prove, so a
    # transcription error in the documented demo cannot pass silently. grad
    # differentiates the same displayed gordon_pv body, at D=2, r=0.1, g=0.05;
    # the analytic derivative is -/+ D/(r-g)^2 = -/+ 800.
    for wrt, want_negative, approx in (("r", True, -800.0), ("g", False, 800.0)):
        expr = (f"grad(fn (d: f32, r: f32, g: f32) -> (d / (r - g)), wrt={wrt})"
                f"({f32(2.0)}, {f32(0.1)}, {f32(0.05)})")
        proc = subprocess.run([binary, "eval", "--json", expr], capture_output=True, text=True)
        try:
            value = json.loads(proc.stdout)["roots"][0]["value"]["value"]
            data = value["data"][0] if isinstance(value, dict) else float(value)
        except Exception as exc:  # noqa: BLE001
            failures.append(f"grad dP/d{wrt}: could not parse eval output ({exc}): {proc.stderr.strip()}")
            continue
        sign_ok = (data < 0.0) if want_negative else (data > 0.0)
        if sign_ok and abs(data - approx) <= 1.0:
            sign = "negative" if want_negative else "positive"
            print(f"  OK  grad dP/d{wrt} = {data:.6g} ({sign}, matches gordon_dP_d{wrt}_{sign})")
        else:
            failures.append(f"grad dP/d{wrt} = {data} does not match the proven sign and magnitude (~{approx})")

    passed, failed = run_tests(binary)
    print(f"  test suite: {passed} passed, {failed} failed")
    if failed:
        failures.append(f"test suite reported {failed} failure(s)")

    if failures:
        print(f"\noracle_harness FAILED with {len(failures)} finding(s):")
        for f in failures:
            print(f"  FAIL {f}")
        return 1
    print("oracle_harness OK: shell numerics match recorded analytic-mirror goldens and the test suite is green.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
