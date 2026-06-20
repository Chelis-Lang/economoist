#!/usr/bin/env python3
"""Audit version pin consistency and workaround citations for economoist."""

import argparse
import re
import sys
from pathlib import Path


def find_repo_root() -> Path:
    d = Path.cwd()
    while d != d.parent:
        if (d / "reef.toml").exists():
            return d
        d = d.parent
    sys.exit("error: cannot find repo root (no reef.toml)")


def read_reef_pin(root: Path) -> str:
    text = (root / "reef.toml").read_text()
    m = re.search(r'compiler\s*=\s*"=([^"]+)"', text)
    if not m:
        sys.exit("error: cannot parse compiler pin from reef.toml")
    return m.group(1)


# A workflow "installs a toolchain" if it downloads the released chelis tarball
# or builds chelis from source. Contract section 2 requires every such workflow
# to carry a matching literal CHELIS_TAG/CHELIS_VERSION env pair, guarded
# offline. These markers identify those steps without running the workflow; a
# workflow with no chelis CI in it (so nothing to pin) is correctly exempt.
TOOLCHAIN_INSTALL_MARKERS = (
    "gh release download",          # download the published chelis tarball
    "repository: Chelis-Lang/chelis",  # checkout chelis source to build it
    "cargo build --release -p chelis-cli",  # build chelis from source
)


def installs_toolchain(text: str) -> bool:
    return any(marker in text for marker in TOOLCHAIN_INSTALL_MARKERS)


def workflow_files(root: Path) -> list[Path]:
    wf_dir = root / ".github" / "workflows"
    if not wf_dir.exists():
        sys.exit(f"error: {wf_dir} not found")
    return sorted(wf_dir.glob("*.yml")) + sorted(wf_dir.glob("*.yaml"))


def read_workflow_pins(text: str) -> dict:
    """Collect the literal CHELIS_TAG / CHELIS_VERSION env pins in one workflow.

    Keyed by the env NAME. Both a bare CHELIS_VERSION (e.g. 0.8.0) and a tagged
    CHELIS_TAG (e.g. v0.8.0) are normalized to the bare version before
    comparison with the reef.toml pin. Only literal `NAME: <value>` forms are
    read (the YAML env block); runtime `echo "NAME=..." >> $GITHUB_ENV`
    derivations are deliberately ignored, because the guard runs offline and
    cannot evaluate them -- that is exactly the silent-skip gap this closes.
    """
    pins: dict[str, str] = {}
    for m in re.finditer(r'CHELIS_TAG:\s*v?([\d.]+)', text):
        pins["CHELIS_TAG"] = m.group(1)
    for m in re.finditer(r'CHELIS_VERSION:\s*v?([\d.]+)', text):
        pins["CHELIS_VERSION"] = m.group(1)
    return pins


def check_pins(root: Path) -> bool:
    reef_pin = read_reef_pin(root)
    ok = True
    guarded = []
    for wf in workflow_files(root):
        text = wf.read_text()
        pins = read_workflow_pins(text)
        toolchain = installs_toolchain(text)

        if toolchain:
            # Every toolchain-installing workflow MUST carry both literal pins.
            for required in ("CHELIS_TAG", "CHELIS_VERSION"):
                if required not in pins:
                    print(f"MISSING: {wf.name} installs a toolchain but has no "
                          f"literal {required} env pin")
                    ok = False

        # Any literal pin present (toolchain-installing or not) must match reef.
        for name, val in pins.items():
            if val != reef_pin:
                print(f"MISMATCH: reef.toml={reef_pin} but {wf.name}:{name}={val}")
                ok = False

        if toolchain:
            guarded.append(wf.name)

    if not guarded:
        print("WARNING: no toolchain-installing workflow found to guard")
        ok = False

    if ok:
        print(f"All pins consistent: {reef_pin}")
        print(f"Guarded toolchain workflows ({len(guarded)}): {', '.join(guarded)}")
    return ok


def scan_citations(root: Path, strict: bool) -> bool:
    pattern = re.compile(r'chelis#(\d+)')
    citations: dict[str, list[str]] = {}
    for ext in ("*.rs", "*.ch", "*.py", "*.md"):
        for f in root.rglob(ext):
            if ".git" in f.parts or "target" in f.parts or "node_modules" in f.parts:
                continue
            try:
                text = f.read_text()
            except (UnicodeDecodeError, PermissionError):
                continue
            for m in pattern.finditer(text):
                citations.setdefault(m.group(0), []).append(str(f.relative_to(root)))
    if not citations:
        print("No chelis#NNN citations found.")
        return True
    print(f"\nFound {len(citations)} distinct citation(s):")
    for cit, files in sorted(citations.items()):
        print(f"  {cit}: {', '.join(files[:5])}")
    if strict:
        print("\n--strict: treating all citations as potentially stale (exit 1)")
        return False
    return True


def main() -> None:
    parser = argparse.ArgumentParser(description="Audit economoist version pins and workaround citations.")
    parser.add_argument("--pins-only", action="store_true", help="Only check pin consistency (CI mode)")
    parser.add_argument("--strict", action="store_true", help="Exit 1 on any stale citation (full mode)")
    args = parser.parse_args()

    root = find_repo_root()
    ok = check_pins(root)

    if not args.pins_only:
        ok = scan_citations(root, args.strict) and ok

    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
