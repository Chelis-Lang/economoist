#!/usr/bin/env python3
"""Run blocked probes: .ch files under tests_blocked/ that should fail with a pinned diagnostic."""

import argparse
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


def find_repo_root() -> Path:
    d = Path.cwd()
    while d != d.parent:
        if (d / "reef.toml").exists():
            return d
        d = d.parent
    sys.exit("error: cannot find repo root (no reef.toml)")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run blocked probes under tests_blocked/.")
    parser.parse_args()

    root = find_repo_root()
    chelis = os.environ.get("CHELIS_BIN", "chelis")
    tests_dir = root / "tests_blocked"

    ch_files = sorted(tests_dir.rglob("*.ch")) if tests_dir.exists() else []
    if not ch_files:
        print("No .ch files found in tests_blocked/. Exiting OK.")
        sys.exit(0)

    fix_detected = []
    drifted = []

    for ch in ch_files:
        expect = ch.with_suffix(".expect")
        if not expect.exists():
            drifted.append((ch, "missing .expect sidecar"))
            continue
        lines = expect.read_text().splitlines()
        pinned_diag = lines[0].strip()
        instructions = "\n".join(lines[1:]).strip() if len(lines) > 1 else ""

        try:
            with tempfile.TemporaryDirectory(prefix="economoist-blocked-probe-") as tmp:
                probe = Path(tmp) / ch.name
                shutil.copy2(ch, probe)
                result = subprocess.run(
                    [chelis, "check", probe.name],
                    cwd=tmp,
                    capture_output=True, text=True, timeout=30,
                )
        except FileNotFoundError:
            sys.exit(f"error: '{chelis}' not found. Set CHELIS_BIN or add chelis to PATH.")
        except subprocess.TimeoutExpired:
            drifted.append((ch, "timeout"))
            continue

        rel = ch.relative_to(root)

        if result.returncode == 0:
            fix_detected.append((ch, instructions))
            print(f"  FIX-detected  {rel}")
            if instructions:
                print(f"    De-narrowing: {instructions}")
            continue

        output = result.stdout + result.stderr
        if pinned_diag in output:
            print(f"  OK            {rel}")
        else:
            drifted.append((ch, f"expected '{pinned_diag}' but got different failure"))
            print(f"  DRIFTED       {rel}")

    if fix_detected or drifted:
        print(f"\nResults: {len(fix_detected)} FIX-detected, {len(drifted)} DRIFTED")
        for path, instr in fix_detected:
            print(f"  FIX-detected: {path.relative_to(root)}")
        for path, reason in drifted:
            print(f"  DRIFTED: {path.relative_to(root)}: {reason}")
        sys.exit(1)

    print(f"\nAll {len(ch_files)} blocked probe(s) OK (still failing with pinned diagnostic).")


if __name__ == "__main__":
    main()
