#!/usr/bin/env python3
"""Numerical oracle harness for Economoist, stdlib only.

Two validation layers, kept distinct from the prover:
  1. The shell's exported operators are imported and evaluated through
     `chelis eval --file`, then compared against recorded analytic-mirror goldens
     within a precision-derived tolerance. The compiler resolves the Reef
     package graph and the harness evaluates the exported model function.
  2. The executable test suite under tests/ is run through `chelis test --json`,
     which exercises the real exported functions; it must report zero failures.

Each analytic mirror and the exported function are compared with the same
recorded golden, across two input configurations per operator. The gate uses
only the standard library.

The harness validates numbers. The structural properties are validated by the
prover (scripts/prove_gate.py). A matching number is not a proof.
"""

from __future__ import annotations

import json
import math
import os
import re
import subprocess
import struct
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]


def resolve_bin() -> str:
    """CHELIS_SMT_BIN/CHELIS_BIN override, else the reef.toml-pinned release
    install (~/.chelis/toolchains/<pin>/bin/chelis),
    else `chelis` on PATH. The release binary supplies every command."""
    from shutil import which
    for env in ("CHELIS_BIN", "CHELIS_SMT_BIN"):
        v = os.environ.get(env)
        if v and (Path(v).expanduser().is_file() or which(v)):
            return str(Path(v).expanduser())
    m = re.search(r'compiler\s*=\s*"=([^"]+)"', (REPO_ROOT / "reef.toml").read_text())
    if m:
        cand = Path.home() / ".chelis" / "toolchains" / m.group(1) / "bin" / "chelis"
        if cand.is_file():
            return str(cand)
    if which("chelis"):
        return "chelis"
    sys.exit("error: no chelis binary found; set CHELIS_SMT_BIN or CHELIS_BIN")


def f32(x: float) -> str:
    return f"cast({x!r}, f32)"


NEXT_MASS = ("Economoist.Markov", "next_mass")
GORDON = ("Economoist.Growth", "gordon_pv")
BELLMAN = ("Economoist.Bellman", "bellman_state0")


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


def eval_imported_root(binary: str, module: str, names: tuple[str, ...], expr: str):
    """Evaluate one binding against the real package graph through eval --file."""
    source = f"import {module} ({', '.join(names)})\n\nbench = {expr}\n"
    path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".ch", prefix="economoist_oracle_", dir=REPO_ROOT,
            encoding="utf-8", delete=False,
        ) as handle:
            handle.write(source)
            path = Path(handle.name)
        formatted = subprocess.run(
            [binary, "fmt", "--inplace", str(path)], capture_output=True, text=True,
        )
        if formatted.returncode != 0:
            raise RuntimeError(f"generated eval probe did not format: {formatted.stderr.strip()}")
        proc = subprocess.run(
            [binary, "eval", "--file", str(path), "--json"],
            cwd=REPO_ROOT, capture_output=True, text=True,
        )
        if proc.returncode != 0:
            raise RuntimeError(f"eval --file failed: {proc.stderr.strip()}")
        return json.loads(proc.stdout)["roots"][0]["value"]["value"]
    finally:
        if path is not None:
            path.unlink(missing_ok=True)


def eval_value(binary: str, model: tuple[str, str], args: tuple) -> float:
    module, function = model
    expr = function + "(" + ", ".join(f32(a) for a in args) + ")"
    return scalar_value(eval_imported_root(binary, module, (function,), expr))


def scalar_value(value: object) -> float:
    """Decode a scalar or rank-zero tensor from compiler JSON."""
    if isinstance(value, dict) and "bits" in value:
        dtype, bits = value.get("dtype"), value["bits"]
        width = {"f32": 8, "f64": 16}.get(dtype)
        if width is None or not isinstance(bits, str) or not re.fullmatch(rf"[0-9a-fA-F]{{{width}}}", bits):
            raise ValueError(f"invalid exact scalar compiler value: {value!r}")
        return struct.unpack("!f" if dtype == "f32" else "!d", bytes.fromhex(bits))[0]
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return float(value)
    if not isinstance(value, dict) or value.get("shape") != []:
        raise ValueError(f"expected scalar compiler value, got {value!r}")
    data = value.get("data")
    if isinstance(data, dict):
        if "bits" in data:
            bits = data["bits"]
            if not isinstance(bits, list) or len(bits) != 1:
                raise ValueError(f"expected one scalar element, got {value!r}")
            return scalar_value({"dtype": data.get("dtype"), "bits": bits[0]})
        data = data.get("values")
    if (
        isinstance(data, list)
        and len(data) == 1
        and isinstance(data[0], (int, float))
        and not isinstance(data[0], bool)
    ):
        return float(data[0])
    raise ValueError(f"expected scalar compiler value, got {value!r}")


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
        expr = (f"grad(fn (d: f32, r: f32, g: f32) -> gordon_pv(d, r, g), wrt={wrt})"
                f"({f32(2.0)}, {f32(0.1)}, {f32(0.05)})")
        try:
            value = eval_imported_root(binary, "Economoist.Growth", ("gordon_pv",), expr)
            data = scalar_value(value)
        except Exception as exc:  # noqa: BLE001
            failures.append(f"grad dP/d{wrt}: could not evaluate imported model ({exc})")
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
