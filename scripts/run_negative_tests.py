#!/usr/bin/env python3
"""Run negative tests: each .ch file under tests_neg/ must fail with the expected diagnostic."""

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path


def find_repo_root() -> Path:
    d = Path.cwd()
    while d != d.parent:
        if (d / "reef.toml").exists():
            return d
        d = d.parent
    sys.exit("error: cannot find repo root (no reef.toml)")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run negative tests under tests_neg/.")
    parser.parse_args()

    root = find_repo_root()
    chelis = os.environ.get("CHELIS_BIN", "chelis")
    tests_dir = root / "tests_neg"

    ch_files = sorted(tests_dir.rglob("*.ch")) if tests_dir.exists() else []
    if not ch_files:
        print("No .ch files found in tests_neg/. Exiting OK.")
        sys.exit(0)

    failures = []
    for ch in ch_files:
        expect = ch.with_suffix(".expect")
        if not expect.exists():
            failures.append((ch, "missing .expect sidecar"))
            continue
        expected_diag = expect.read_text().splitlines()[0].strip()

        try:
            result = subprocess.run(
                [chelis, "test", str(ch), "--json"],
                capture_output=True, text=True, timeout=30,
            )
        except FileNotFoundError:
            sys.exit(f"error: '{chelis}' not found. Set CHELIS_BIN or add chelis to PATH.")
        except subprocess.TimeoutExpired:
            failures.append((ch, "timeout"))
            continue

        if result.returncode == 0:
            failures.append((ch, "expected failure but test passed"))
            continue

        output = result.stdout + result.stderr
        if expected_diag not in output:
            failures.append((ch, f"wrong diagnostic; expected '{expected_diag}' in output"))
            continue

        print(f"  OK  {ch.relative_to(root)}")

    if failures:
        print(f"\n{len(failures)} FAILURE(s):")
        for path, reason in failures:
            print(f"  FAIL {path.relative_to(root)}: {reason}")
        sys.exit(1)

    print(f"\nAll {len(ch_files)} negative test(s) passed.")


if __name__ == "__main__":
    main()
