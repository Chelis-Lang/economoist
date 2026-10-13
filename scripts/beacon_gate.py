#!/usr/bin/env python3
"""Check the separate Gordon Beacon box lane against the pinned compiler."""

from __future__ import annotations

import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
EXPECTED = {
    "gordon_pv_box_lower": ("passed", "lower"),
    "gordon_pv_box_upper": ("passed", "upper"),
    "gordon_pv_box_lower_wrong": ("failed", "lower"),
    "gordon_pv_box_upper_wrong": ("failed", "upper"),
}


def check_records(records: list[dict]) -> list[str]:
    errors: list[str] = []
    properties = [record for record in records if record.get("kind") == "property"]
    summaries = [record for record in records if record.get("kind") == "summary"]
    names = [record.get("name") for record in properties]
    if len(summaries) != 1 or len(names) != len(set(names)) or set(names) != set(EXPECTED):
        errors.append("expected one summary and exactly four distinct Gordon properties")
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
                or evidence.get("float_execution_covered") is not False
                or len(declarations) != 1
                or declarations[0].get("name") != "Economoist.Growth.gordon_pv"
                or not declarations[0].get("sha256")):
            errors.append(f"{name}: source binding, bound side or arithmetic model is missing")
        if status == "passed":
            if (evidence.get("beacon_evidence") or {}).get("verdict") != "certified":
                errors.append(f"{name}: Beacon did not certify the box")
        elif (record.get("counterexample") or {}).get("confirmed") is not True:
            errors.append(f"{name}: no confirmed false-control witness")
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
