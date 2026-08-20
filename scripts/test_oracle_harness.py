#!/usr/bin/env python3
"""Regression tests for compiler JSON value decoding in the oracle gate."""

from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


SCRIPT = Path(__file__).with_name("oracle_harness.py")
SPEC = importlib.util.spec_from_file_location("oracle_harness", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
ORACLE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(ORACLE)


class ScalarValueTests(unittest.TestCase):
    def test_decodes_current_typed_tensor_scalar(self) -> None:
        value = {"shape": [], "data": {"dtype": "f32", "values": [-800.0]}}
        self.assertEqual(ORACLE.scalar_value(value), -800.0)

    def test_decodes_legacy_tensor_scalar(self) -> None:
        self.assertEqual(ORACLE.scalar_value({"shape": [], "data": [800.0]}), 800.0)

    def test_rejects_non_scalar_tensor(self) -> None:
        value = {"shape": [2], "data": {"dtype": "f32", "values": [1.0, 2.0]}}
        with self.assertRaisesRegex(ValueError, "scalar"):
            ORACLE.scalar_value(value)


if __name__ == "__main__":
    unittest.main()
