#!/usr/bin/env python3
"""Build chelis-smt from source with the smt feature (requires cvc5 build deps)."""

import argparse
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

INSTALL_BASE = Path.home() / ".local" / "share" / "chelis"
CLONE_DIR = Path.home() / ".local" / "share" / "chelis" / "_src"

PREREQS = ["cmake", "g++", "cargo"]


def check_prereqs() -> None:
    print("Checking prerequisites...")
    missing = [p for p in PREREQS if shutil.which(p) is None]
    # libclang check
    if not any(Path(d).glob("libclang*") for d in ["/usr/lib", "/usr/lib/x86_64-linux-gnu", "/usr/lib64"] if Path(d).exists()):
        missing.append("libclang-dev")
    if missing:
        sys.exit(f"error: missing prerequisites: {', '.join(missing)}\n"
                 f"Install with: sudo apt-get install cmake g++ libclang-dev")
    print("All prerequisites found.")


def read_version_from_reef(reef_path: Path) -> str:
    text = reef_path.read_text()
    m = re.search(r'compiler\s*=\s*"=([^"]+)"', text)
    if not m:
        sys.exit(f"error: cannot parse compiler pin from {reef_path}")
    return m.group(1)


def find_reef_toml() -> Path:
    d = Path.cwd()
    while d != d.parent:
        p = d / "reef.toml"
        if p.exists():
            return p
        d = d.parent
    sys.exit("error: reef.toml not found in any parent directory")


def build(version: str) -> None:
    check_prereqs()

    tag = f"v{version}"
    src = CLONE_DIR / "chelis"
    src.mkdir(parents=True, exist_ok=True)

    if (src / ".git").exists():
        print(f"Fetching and checking out {tag}...")
        subprocess.run(["git", "fetch", "--tags"], cwd=src, check=True)
        subprocess.run(["git", "checkout", tag], cwd=src, check=True)
    else:
        print(f"Cloning Chelis-Lang/chelis at {tag}...")
        subprocess.run(
            ["git", "clone", "--branch", tag, "--depth", "1",
             "https://github.com/Chelis-Lang/chelis.git", str(src)],
            check=True,
        )

    print("Building chelis-cli with --features smt ...")
    subprocess.run(
        ["cargo", "build", "--release", "-p", "chelis-cli", "--features", "smt"],
        cwd=src,
        check=True,
    )

    # Install binary
    built = src / "target" / "release" / "chelis"
    if not built.exists():
        sys.exit(f"error: expected binary at {built}")

    dest = INSTALL_BASE / version / "chelis-smt"
    shutil.copy2(built, dest)
    dest.chmod(0o755)
    print(f"Installed chelis-smt to {dest}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Build chelis-smt from source with the smt feature (linked against cvc5)."
    )
    parser.add_argument("--version", help="Override version (default: read from reef.toml)")
    args = parser.parse_args()

    version = args.version or read_version_from_reef(find_reef_toml())
    build(version)


if __name__ == "__main__":
    main()
