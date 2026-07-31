#!/usr/bin/env python3
"""Regression tests for the release-toolchain install layout."""

from __future__ import annotations

import importlib.util
import hashlib
import os
import shutil
import subprocess
import tarfile
import tempfile
import unittest
from pathlib import Path
from unittest import mock


SCRIPT = Path(__file__).with_name("install_chelis_toolchain.py")
REPO_ROOT = SCRIPT.parents[1]
SPEC = importlib.util.spec_from_file_location("install_chelis_toolchain", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
INSTALLER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(INSTALLER)


class InstallerLayoutTests(unittest.TestCase):
    def test_composite_action_verifies_payload_before_extracting(self) -> None:
        action = (
            REPO_ROOT / ".github" / "actions" / "install-chelis" / "action.yml"
        ).read_text(encoding="utf-8")
        self.assertIn("default: linux-x86_64-glibc2.31", action)
        self.assertIn('key: chelis-toolchain-sha256-v1-', action)
        self.assertIn('--pattern "$asset.sha256"', action)
        self.assertIn('shasum -a 256 -c "$asset.sha256"', action)
        self.assertIn('sha256sum -c "$asset.sha256"', action)
        self.assertLess(
            action.index('sha256sum -c "$asset.sha256"'),
            action.index('tar -xzf "/tmp/chelis-toolchain/$asset"'),
        )

    def test_release_workflow_verifies_compatibility_asset_before_extracting(
        self,
    ) -> None:
        workflow = (REPO_ROOT / ".github" / "workflows" / "release.yml").read_text(
            encoding="utf-8"
        )
        self.assertIn(
            'asset="chelis-${CHELIS_TAG}-linux-x86_64-glibc2.31.tar.gz"',
            workflow,
        )
        self.assertIn('--pattern "${asset}.sha256"', workflow)
        self.assertLess(
            workflow.index('sha256sum -c "${asset}.sha256"'),
            workflow.index('tar -xzf "/tmp/chelis-toolchain/${asset}"'),
        )
        self.assertIn(
            "chelis-${CHELIS_TAG}-linux-x86_64-glibc2.31/bin",
            workflow,
        )

    def test_linux_asset_is_compatibility_build(self) -> None:
        self.assertEqual(
            INSTALLER.release_asset_name("0.17.4"),
            "chelis-v0.17.4-linux-x86_64-glibc2.31.tar.gz",
        )

    def test_sidecar_parser_requires_exact_asset_name(self) -> None:
        with tempfile.TemporaryDirectory() as raw_tmp:
            sidecar = Path(raw_tmp) / "asset.sha256"
            digest = "a" * 64
            sidecar.write_text(f"{digest}  wanted.tar.gz\n")
            self.assertEqual(
                INSTALLER.read_sidecar(sidecar, "wanted.tar.gz"),
                digest,
            )
            with self.assertRaises(SystemExit):
                INSTALLER.read_sidecar(sidecar, "other.tar.gz")

    def test_launcher_resolves_release_binary_under_bin(self) -> None:
        self.assertIn(
            '$HOME/.local/share/chelis/$VER/bin/chelis',
            INSTALLER.LAUNCHER_SCRIPT,
        )
        self.assertNotIn(
            '$HOME/.local/share/chelis/$VER/chelis"',
            INSTALLER.LAUNCHER_SCRIPT,
        )

    def make_release_fixture(
        self, root: Path, *, version: str = "0.17.4", valid_checksum: bool = True
    ) -> tuple[Path, Path]:
        asset = INSTALLER.release_asset_name(version)
        payload_root = root / f"chelis-v{version}-linux-x86_64-glibc2.31"
        binary = payload_root / "bin" / "chelis"
        binary.parent.mkdir(parents=True)
        binary.write_text(f"#!/bin/sh\necho 'chelis {version}'\n", encoding="utf-8")
        binary.chmod(0o755)
        tarball = root / asset
        with tarfile.open(tarball, "w:gz") as archive:
            archive.add(payload_root, arcname=payload_root.name)
        digest = hashlib.sha256(tarball.read_bytes()).hexdigest()
        if not valid_checksum:
            digest = "0" * 64
        sidecar = root / f"{asset}.sha256"
        sidecar.write_text(f"{digest}  {asset}\n", encoding="utf-8")
        return tarball, sidecar

    def run_fixture_install(
        self,
        fixture_root: Path,
        install_base: Path,
        launcher: Path,
    ) -> list[list[str]]:
        real_run = subprocess.run
        calls: list[list[str]] = []

        def run(command: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
            calls.append(command)
            if command[0] == "gh":
                target = Path(command[command.index("--dir") + 1])
                for source in fixture_root.glob("chelis-*.tar.gz*"):
                    shutil.copy2(source, target / source.name)
                return subprocess.CompletedProcess(command, 0)
            return real_run(command, **kwargs)

        with (
            mock.patch.object(INSTALLER, "INSTALL_BASE", install_base),
            mock.patch.object(INSTALLER, "LAUNCHER_PATH", launcher),
            mock.patch.object(INSTALLER.subprocess, "run", side_effect=run),
        ):
            INSTALLER.install("0.17.4", set_default=False)
        return calls

    def test_existing_install_is_reauthenticated_and_replaced(self) -> None:
        with tempfile.TemporaryDirectory() as raw_tmp:
            tmp = Path(raw_tmp)
            fixture = tmp / "fixture"
            fixture.mkdir()
            tarball, _ = self.make_release_fixture(fixture)
            install_base = tmp / "toolchains"
            binary = install_base / "0.17.4" / "bin" / "chelis"
            binary.parent.mkdir(parents=True)
            binary.write_text("#!/bin/sh\necho candidate\n", encoding="utf-8")
            launcher = tmp / "bin" / "chelis"

            calls = self.run_fixture_install(fixture, install_base, launcher)
            self.assertTrue(any(command[0] == "gh" for command in calls))
            self.assertEqual(
                subprocess.check_output([str(binary), "--version"], text=True).strip(),
                "chelis 0.17.4",
            )
            self.assertEqual(
                (binary.parent.parent / ".release-sha256").read_text().strip(),
                hashlib.sha256(tarball.read_bytes()).hexdigest(),
            )
            self.assertEqual(launcher.read_text(), INSTALLER.LAUNCHER_SCRIPT)
            self.assertTrue(launcher.stat().st_mode & 0o100)

    def test_checksum_failure_preserves_existing_install(self) -> None:
        with tempfile.TemporaryDirectory() as raw_tmp:
            tmp = Path(raw_tmp)
            fixture = tmp / "fixture"
            fixture.mkdir()
            self.make_release_fixture(fixture, valid_checksum=False)
            install_base = tmp / "toolchains"
            binary = install_base / "0.17.4" / "bin" / "chelis"
            binary.parent.mkdir(parents=True)
            binary.write_text("known-good", encoding="utf-8")
            with self.assertRaisesRegex(SystemExit, "sha256 mismatch"):
                self.run_fixture_install(fixture, install_base, tmp / "launcher")
            self.assertEqual(binary.read_text(encoding="utf-8"), "known-good")

    def test_failed_final_replace_rolls_back_previous_install(self) -> None:
        with tempfile.TemporaryDirectory() as raw_tmp:
            tmp = Path(raw_tmp)
            dest = tmp / "0.17.4"
            dest.mkdir()
            (dest / "identity").write_text("old", encoding="utf-8")
            staged = tmp / "staged"
            staged.mkdir()
            (staged / "identity").write_text("new", encoding="utf-8")
            real_replace = os.replace

            def fail_staged_replace(source: object, target: object) -> None:
                if Path(source) == staged:
                    raise OSError("injected rename failure")
                real_replace(source, target)

            with (
                mock.patch.object(
                    INSTALLER.os, "replace", side_effect=fail_staged_replace
                ),
                self.assertRaisesRegex(OSError, "injected rename failure"),
            ):
                INSTALLER.replace_install(staged, dest)

            self.assertEqual((dest / "identity").read_text(encoding="utf-8"), "old")

    def test_interrupted_replace_recovers_backup(self) -> None:
        with tempfile.TemporaryDirectory() as raw_tmp:
            dest = Path(raw_tmp) / "0.17.4"
            backup = INSTALLER.backup_path(dest)
            backup.mkdir()
            (backup / "identity").write_text("old", encoding="utf-8")
            INSTALLER.recover_interrupted_install(dest)
            self.assertEqual((dest / "identity").read_text(encoding="utf-8"), "old")


if __name__ == "__main__":
    unittest.main()
