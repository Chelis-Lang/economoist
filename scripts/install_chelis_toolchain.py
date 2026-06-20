#!/usr/bin/env python3
"""Install the Chelis release toolchain for the version pinned in reef.toml."""

import argparse
import os
import re
import subprocess
import sys
from pathlib import Path

INSTALL_BASE = Path.home() / ".local" / "share" / "chelis"
LAUNCHER_PATH = Path.home() / ".local" / "bin" / "chelis"

LAUNCHER_SCRIPT = '''\
#!/bin/sh
# Pin-resolving Chelis launcher.
# Resolution order: CHELIS_TOOLCHAIN env > nearest reef.toml > default

resolve_version() {
  if [ -n "$CHELIS_TOOLCHAIN" ]; then
    echo "$CHELIS_TOOLCHAIN"; return
  fi
  dir="$PWD"
  while [ "$dir" != "/" ]; do
    if [ -f "$dir/reef.toml" ]; then
      ver=$(grep -oP 'compiler\\s*=\\s*"=\\K[^"]+' "$dir/reef.toml" 2>/dev/null)
      if [ -n "$ver" ]; then echo "$ver"; return; fi
    fi
    dir=$(dirname "$dir")
  done
  if [ -f "$HOME/.local/share/chelis/default" ]; then
    cat "$HOME/.local/share/chelis/default"; return
  fi
  echo "error: no chelis version resolved" >&2; exit 1
}

VER=$(resolve_version)
BIN="$HOME/.local/share/chelis/$VER/chelis"
if [ ! -x "$BIN" ]; then
  echo "error: chelis $VER not installed at $BIN" >&2; exit 1
fi
exec "$BIN" "$@"
'''


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


def install(version: str, set_default: bool) -> None:
    dest = INSTALL_BASE / version
    if dest.exists() and (dest / "chelis").exists():
        print(f"chelis {version} already installed at {dest}")
    else:
        dest.mkdir(parents=True, exist_ok=True)
        print(f"Downloading chelis v{version} release tarball...")
        subprocess.run(
            ["gh", "release", "download", f"v{version}",
             "--repo", "Chelis-Lang/chelis",
             "--pattern", "chelis-*-linux-x86_64.tar.gz",
             "--dir", str(dest)],
            check=True,
        )
        # Extract
        tarballs = list(dest.glob("chelis-*-linux-x86_64.tar.gz"))
        if not tarballs:
            sys.exit("error: no tarball downloaded")
        subprocess.run(
            ["tar", "xzf", str(tarballs[0]), "-C", str(dest), "--strip-components=1"],
            check=True,
        )
        for tb in tarballs:
            tb.unlink()
        print(f"Installed chelis {version} to {dest}")

    # Write launcher
    LAUNCHER_PATH.parent.mkdir(parents=True, exist_ok=True)
    LAUNCHER_PATH.write_text(LAUNCHER_SCRIPT)
    LAUNCHER_PATH.chmod(0o755)
    print(f"Launcher written to {LAUNCHER_PATH}")

    if set_default:
        (INSTALL_BASE / "default").write_text(version)
        print(f"Default set to {version}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Install the Chelis release toolchain from the pinned version in reef.toml."
    )
    parser.add_argument("--set-default", action="store_true",
                        help="Set this version as the machine default")
    parser.add_argument("--version", help="Override version (default: read from reef.toml)")
    args = parser.parse_args()

    version = args.version or read_version_from_reef(find_reef_toml())
    install(version, args.set_default)


if __name__ == "__main__":
    main()
