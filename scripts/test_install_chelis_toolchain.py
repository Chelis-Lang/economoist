#!/usr/bin/env python3
"""Regression tests for the release-toolchain install layout."""

from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path
from unittest import mock


SCRIPT = Path(__file__).with_name("install_chelis_toolchain.py")
SPEC = importlib.util.spec_from_file_location("install_chelis_toolchain", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
INSTALLER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(INSTALLER)


class InstallerLayoutTests(unittest.TestCase):
    def test_launcher_resolves_release_binary_under_bin(self) -> None:
        self.assertIn(
            '$HOME/.local/share/chelis/$VER/bin/chelis',
            INSTALLER.LAUNCHER_SCRIPT,
        )
        self.assertNotIn(
            '$HOME/.local/share/chelis/$VER/chelis"',
            INSTALLER.LAUNCHER_SCRIPT,
        )

    def test_existing_release_layout_skips_download(self) -> None:
        with tempfile.TemporaryDirectory() as raw_tmp:
            tmp = Path(raw_tmp)
            install_base = tmp / "toolchains"
            binary = install_base / "0.17.4" / "bin" / "chelis"
            binary.parent.mkdir(parents=True)
            binary.write_bytes(b"release binary")
            launcher = tmp / "bin" / "chelis"

            with (
                mock.patch.object(INSTALLER, "INSTALL_BASE", install_base),
                mock.patch.object(INSTALLER, "LAUNCHER_PATH", launcher),
                mock.patch.object(INSTALLER.subprocess, "run") as run,
            ):
                INSTALLER.install("0.17.4", set_default=False)

            run.assert_not_called()
            self.assertEqual(launcher.read_text(), INSTALLER.LAUNCHER_SCRIPT)
            self.assertTrue(launcher.stat().st_mode & 0o100)


if __name__ == "__main__":
    unittest.main()
