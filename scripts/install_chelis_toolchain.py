#!/usr/bin/env python3
"""Install the Chelis release toolchain for the version pinned in reef.toml."""

import argparse
import hashlib
import os
import re
import shutil
import subprocess
import sys
import tempfile
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
BIN="$HOME/.local/share/chelis/$VER/bin/chelis"
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


def release_asset_name(version: str) -> str:
    return f"chelis-v{version}-linux-x86_64-glibc2.31.tar.gz"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_sidecar(sidecar: Path, expected_name: str) -> str:
    fields = sidecar.read_text(encoding="utf-8").strip().split()
    if len(fields) != 2 or fields[1].lstrip("*") != expected_name:
        sys.exit(f"error: malformed checksum sidecar {sidecar}")
    digest = fields[0].lower()
    if not re.fullmatch(r"[0-9a-f]{64}", digest):
        sys.exit(f"error: malformed sha256 digest in {sidecar}")
    return digest


def backup_path(dest: Path) -> Path:
    return dest.with_name(f".{dest.name}.previous")


def recover_interrupted_install(dest: Path) -> None:
    backup = backup_path(dest)
    if not dest.exists() and backup.exists():
        os.replace(backup, dest)


def replace_install(staged: Path, dest: Path) -> None:
    """Replace dest while preserving the prior install on every raised error."""
    backup = backup_path(dest)
    if backup.exists():
        shutil.rmtree(backup)
    if dest.exists():
        os.replace(dest, backup)
    try:
        os.replace(staged, dest)
    except BaseException:
        if dest.exists():
            shutil.rmtree(dest)
        if backup.exists():
            os.replace(backup, dest)
        raise
    if backup.exists():
        shutil.rmtree(backup)


def install(version: str, set_default: bool) -> None:
    dest = INSTALL_BASE / version
    asset = release_asset_name(version)
    print(f"Downloading official chelis v{version} release asset {asset}...")
    INSTALL_BASE.mkdir(parents=True, exist_ok=True)
    recover_interrupted_install(dest)
    with tempfile.TemporaryDirectory(
        prefix=f".chelis-{version}-", dir=INSTALL_BASE
    ) as raw_tmp:
        tmp = Path(raw_tmp)
        subprocess.run(
            [
                "gh",
                "release",
                "download",
                f"v{version}",
                "--repo",
                "Chelis-Lang/chelis",
                "--pattern",
                asset,
                "--pattern",
                f"{asset}.sha256",
                "--dir",
                str(tmp),
            ],
            check=True,
        )
        tarball = tmp / asset
        sidecar = tmp / f"{asset}.sha256"
        expected = read_sidecar(sidecar, asset)
        actual = sha256_file(tarball)
        if actual != expected:
            sys.exit(
                f"error: sha256 mismatch for {asset}: expected {expected}, got {actual}"
            )
        staged = tmp / "staged"
        staged.mkdir()
        subprocess.run(
            [
                "tar",
                "xzf",
                str(tarball),
                "-C",
                str(staged),
                "--strip-components=1",
            ],
            check=True,
        )
        binary = staged / "bin" / "chelis"
        reported = subprocess.check_output([str(binary), "--version"], text=True).strip()
        if reported != f"chelis {version}":
            sys.exit(
                f"error: extracted toolchain reports {reported!r}, "
                f"expected 'chelis {version}'"
            )
        (staged / ".release-sha256").write_text(f"{actual}\n", encoding="utf-8")
        replace_install(staged, dest)
    print(f"Installed verified chelis {version} release to {dest}")

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
