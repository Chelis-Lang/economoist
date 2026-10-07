#!/usr/bin/env python3
"""Run every Chelis example in the book against this checkout's source.

Each ```chelis block in docs/book/src is a complete `src/main.ch` for a
consumer project that depends on Economoist. When the block is followed by a
```text block, that text is the command's real output: `chelis prove
src/main.ch` for a block that states a `@property`, `chelis eval --file
src/main.ch` otherwise. The script builds and publishes this checkout into a
throwaway Reef registry (HOME points at a temporary directory, so the user's
~/.chelis/reef is never touched), creates one consumer project per example,
and requires: `chelis fmt --check` clean, `chelis check` score 1, and output
identical to the text block.

The book is rendered from the chelis.ch docs. A failure here means the site
page is wrong (or the API changed without a book update); fix the site page
and re-render.

Usage: check_book_examples.py [--chelis PATH] [--keep]
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import tomllib
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
BOOK = REPO / "docs" / "book" / "src"
FENCE = re.compile(r"^```(\w*)\s*$")


def examples() -> list[tuple[str, str, str | None]]:
    """(location, chelis source, expected output or None) for each block."""
    found = []
    for page in sorted(BOOK.rglob("*.md")):
        lines = page.read_text().splitlines()
        blocks: list[tuple[int, str, list[str]]] = []
        i = 0
        while i < len(lines):
            m = FENCE.match(lines[i])
            if m:
                j = i + 1
                while j < len(lines) and not lines[j].startswith("```"):
                    j += 1
                blocks.append((i + 1, m.group(1), lines[i + 1:j]))
                i = j
            i += 1
        for k, (line, lang, body) in enumerate(blocks):
            if lang != "chelis":
                continue
            expected = None
            if k + 1 < len(blocks) and blocks[k + 1][1] == "text":
                expected = "\n".join(blocks[k + 1][2])
            found.append((f"{page.relative_to(REPO)}:{line}", "\n".join(body) + "\n", expected))
    return found


def resolve_chelis(explicit: str | None) -> str:
    if explicit:
        return explicit
    # chelisup's shim resolves toolchains under $HOME, which this script
    # replaces; ask it for the concrete binary first.
    chelisup = shutil.which("chelisup")
    if chelisup:
        out = subprocess.run([chelisup, "which"], cwd=REPO, capture_output=True, text=True)
        path = out.stdout.strip().splitlines()[-1] if out.returncode == 0 and out.stdout.strip() else ""
        if path and Path(path).exists():
            return path
    found = shutil.which("chelis")
    if not found:
        sys.exit("check_book_examples: chelis not found on PATH")
    return found


def run(cmd: list[str], cwd: Path, env: dict[str, str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, cwd=cwd, env=env, capture_output=True, text=True)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--chelis", help="chelis binary (default: the toolchain this checkout pins)")
    ap.add_argument("--keep", action="store_true", help="keep the temporary directory")
    args = ap.parse_args()

    chelis = resolve_chelis(args.chelis)
    manifest = tomllib.loads((REPO / "reef.toml").read_text())["package"]
    name, version, compiler = manifest["name"], manifest["version"], manifest["compiler"]

    tmp = Path(tempfile.mkdtemp(prefix="book-examples-"))
    env = dict(os.environ, HOME=str(tmp / "home"))
    (tmp / "home").mkdir()
    failures: list[str] = []
    try:
        for step in (["reef", "build", "--no-auto-fetch", str(REPO)], ["reef", "publish", str(REPO)]):
            r = run([chelis, *step], REPO, env)
            if r.returncode != 0:
                print(r.stdout + r.stderr, file=sys.stderr)
                sys.exit(f"check_book_examples: `chelis {' '.join(step)}` failed")

        cases = examples()
        if not cases:
            sys.exit(f"check_book_examples: no chelis examples found under {BOOK.relative_to(REPO)}")
        for n, (where, source, expected) in enumerate(cases):
            proj = tmp / f"ex{n}"
            r = run([chelis, "reef", "init", "demo", "--module-prefix", "Demo", "--output", str(proj)], tmp, env)
            if r.returncode != 0:
                sys.exit(f"check_book_examples: reef init failed: {r.stderr}")
            toml = (proj / "reef.toml").read_text()
            toml = re.sub(r'(?m)^compiler = ".*"$', f'compiler = "{compiler}"', toml)
            toml = toml.replace("[dependencies]\n", f'[dependencies]\n{name} = {{ version = "{version}" }}\n', 1)
            (proj / "reef.toml").write_text(toml)
            (proj / "src" / "main.ch").write_text(source)

            r = run([chelis, "fmt", "--check", "src/main.ch"], proj, env)
            if r.returncode != 0:
                failures.append(f"{where}: not `chelis fmt` clean\n{r.stdout}{r.stderr}")
            r = run([chelis, "check", "src/main.ch"], proj, env)
            try:
                score = json.loads(r.stdout[r.stdout.index("{"):]).get("score")
            except ValueError:
                score = None
            if score != 1:
                failures.append(f"{where}: `chelis check` score {score}\n{r.stdout}{r.stderr}")
                continue
            if expected is None:
                continue
            is_prove = re.search(r"(?m)^@property\b", source) is not None
            cmd = ["prove", "src/main.ch"] if is_prove else ["eval", "--file", "src/main.ch"]
            r = run([chelis, *cmd], proj, env)
            got = "\n".join(line.rstrip() for line in r.stdout.strip("\n").splitlines())
            want = "\n".join(line.rstrip() for line in expected.strip("\n").splitlines())
            if got != want:
                failures.append(
                    f"{where}: `chelis {' '.join(cmd)}` output differs\n--- book\n{want}\n--- actual\n{got}\n{r.stderr}")
        for f in failures:
            print(f"FAIL {f}")
        print(f"book-examples: {len(cases)} examples, {len(failures)} failures")
        return 1 if failures else 0
    finally:
        if args.keep:
            print(f"kept {tmp}")
        else:
            shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
