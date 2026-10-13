#!/usr/bin/env python3
"""Check the separate Gordon Beacon box lane against the pinned compiler."""

from __future__ import annotations

import json
import os
from pathlib import Path
import re
import shutil
import struct
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
EXPECTED = {
    "gordon_pv_box_lower": ("passed", "lower"),
    "gordon_pv_box_upper": ("passed", "upper"),
    "gordon_pv_box_lower_wrong": ("failed", "lower"),
    "gordon_pv_box_upper_wrong": ("failed", "upper"),
}
BOUNDS = {
    "gordon_pv_box_lower": (">=", 6.0),
    "gordon_pv_box_upper": ("<=", 26.0),
    "gordon_pv_box_lower_wrong": (">=", 7.0),
    "gordon_pv_box_upper_wrong": ("<=", 24.0),
}
GOAL_PREFIX = (
    "forall(d: f32, r: f32, g: f32) where "
    "d >= 0.5f32, d <= 1.0f32, r >= 0.08f32, r <= 0.1f32, "
    "g >= 0.02f32, g <= 0.04f32: (Economoist.Growth.gordon_pv(d, r, g) "
)


def f32(value: float) -> float:
    return struct.unpack(">f", struct.pack(">f", value))[0]


EXPECTED_BOX = {
    "d": {"lo": f32(0.5), "hi": f32(1.0)},
    "r": {"lo": f32(0.08), "hi": f32(0.10)},
    "g": {"lo": f32(0.02), "hi": f32(0.04)},
}


def expected_goal(name: str) -> str:
    comparison, bound = BOUNDS[name]
    return f"{GOAL_PREFIX}{comparison} {bound}f32)"


def expected_source_bound(name: str) -> dict[str, str]:
    return {"dtype": "f64", "bits": struct.pack(">d", BOUNDS[name][1]).hex()}


def check_records(records: list[dict]) -> list[str]:
    errors: list[str] = []
    properties = [record for record in records if record.get("kind") == "property"]
    summaries = [record for record in records if record.get("kind") == "summary"]
    names = [record.get("name") for record in properties]
    if len(summaries) != 1 or len(records) != 5 or len(names) != len(set(names)) or set(names) != set(EXPECTED):
        errors.append("expected one summary and exactly four distinct Gordon properties")
    elif any(summaries[0].get(key) != expected for key, expected in
             (("passed", 2), ("failed", 2), ("unsupported", 0), ("errors", 0), ("total", 4))):
        errors.append("summary counts do not match the four Gordon outcomes")
    for record in properties:
        name = record.get("name")
        if name not in EXPECTED:
            continue
        status, side = EXPECTED[name]
        evidence = record.get("engine_evidence") or {}
        binding = evidence.get("source_binding") or {}
        declarations = binding.get("declarations") or []
        if (record.get("status") != status or record.get("proof_tier") != "beacon"
                or record.get("samples") != 0 or record.get("arith_model") != "real"
                or (status == "passed" and "real_arithmetic" not in record.get("qualifiers", []))):
            errors.append(f"{name}: expected {status} with zero-sample real Beacon evidence")
        if (evidence.get("bound_side") != side
                or evidence.get("input_box") != EXPECTED_BOX
                or evidence.get("source_bound") != expected_source_bound(name)
                or record.get("goal") != expected_goal(name)
                or evidence.get("float_execution_covered") is not False
                or len(declarations) != 1
                or declarations[0].get("name") != "Economoist.Growth.gordon_pv"
                or not declarations[0].get("sha256")):
            errors.append(f"{name}: source binding, bound side or arithmetic model is missing")
        if status == "passed":
            if (evidence.get("beacon_evidence") or {}).get("verdict") != "certified":
                errors.append(f"{name}: Beacon did not certify the box")
        elif ((record.get("counterexample") or {}).get("confirmed") is not True
              or (evidence.get("beacon_evidence") or {}).get("verdict") != "refuted"):
            errors.append(f"{name}: no confirmed Beacon false-control witness")
    return errors


def main() -> int:
    pin = re.search(r'compiler\s*=\s*"=([0-9.]+)"', (ROOT / "reef.toml").read_text())
    if pin is None:
        sys.exit("beacon_gate: missing exact compiler pin")
    configured = os.environ.get("CHELIS_BIN") or shutil.which("chelis")
    binary = Path(configured) if configured else Path.home() / ".chelis" / "toolchains" / pin.group(1) / "bin" / "chelis"
    beacon = os.environ.get("CHELIS_BEACON_BIN")
    if not binary.is_file() or not beacon or not Path(beacon).is_file():
        sys.exit("beacon_gate: install the pinned Chelis and set CHELIS_BEACON_BIN")
    version = subprocess.run([str(binary), "--version"], capture_output=True, text=True)
    if version.returncode != 0 or version.stdout.strip() != f"chelis {pin.group(1)}":
        sys.exit("beacon_gate: Chelis binary does not match the package pin")
    result = subprocess.run(
        [str(binary), "prove", "beacon_properties/gordon_box.ch", "--tier",
         "beacon-only", "--json"], cwd=ROOT, capture_output=True, text=True,
        env=os.environ.copy(),
    )
    records = []
    try:
        records = [json.loads(line) for line in result.stdout.splitlines()]
    except json.JSONDecodeError as exc:
        sys.exit(f"beacon_gate: malformed compiler JSON: {exc}")
    errors = check_records(records)
    if result.returncode not in (0, 1):
        errors.append(f"compiler exited {result.returncode}: {result.stderr.strip()}")
    if errors:
        print("FAIL: Gordon Beacon box")
        for error in errors:
            print(f"  {error}")
        return 1
    print("PASS: Gordon Beacon box and false controls")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
