#!/usr/bin/env python3
"""Regression tests for the forge package's compiler pin."""

from __future__ import annotations

import importlib.util
import subprocess
import unittest
from pathlib import Path
from unittest import mock


SCRIPT = Path(__file__).with_name("run_forge_tests.py")
SPEC = importlib.util.spec_from_file_location("run_forge_tests", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
FORGE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(FORGE)


class ForgeManifestTests(unittest.TestCase):
    def test_manifest_pin_comes_from_resolved_binary(self) -> None:
        version = subprocess.CompletedProcess(
            args=["candidate-chelis", "--version"],
            returncode=0,
            stdout="chelis 9.8.7\n",
            stderr="",
        )
        with mock.patch.object(FORGE.subprocess, "run", return_value=version) as run:
            reef = FORGE.reef_for_binary("candidate-chelis")

        run.assert_called_once_with(
            ["candidate-chelis", "--version"],
            capture_output=True,
            text=True,
            check=True,
        )
        self.assertIn('compiler = "=9.8.7"', reef)
        self.assertNotIn('compiler = "=0.14.0"', reef)
        self.assertNotIn("__COMPILER_VERSION__", reef)

    def test_unexpected_version_output_is_rejected(self) -> None:
        version = subprocess.CompletedProcess(
            args=["candidate-chelis", "--version"],
            returncode=0,
            stdout="not-chelis 9.8.7\n",
            stderr="",
        )
        with mock.patch.object(FORGE.subprocess, "run", return_value=version):
            with self.assertRaisesRegex(ValueError, "unexpected compiler version"):
                FORGE.reef_for_binary("candidate-chelis")


if __name__ == "__main__":
    unittest.main()
