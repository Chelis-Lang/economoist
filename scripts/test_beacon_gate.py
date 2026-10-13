"""Negative controls for the separate Beacon proof gate."""

from __future__ import annotations

import copy
import importlib.util
import unittest
from pathlib import Path


SPEC = importlib.util.spec_from_file_location("beacon_gate", Path(__file__).with_name("beacon_gate.py"))
assert SPEC is not None and SPEC.loader is not None
GATE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(GATE)


class BeaconGateTests(unittest.TestCase):
    def test_rejects_missing_source_binding_and_false_witness(self) -> None:
        records = []
        for name, (status, side) in GATE.EXPECTED.items():
            evidence = {
                "bound_side": side, "float_execution_covered": False,
                "source_binding": {"declarations": [{
                    "name": "Economoist.Growth.gordon_pv", "sha256": "source",
                }]},
                "beacon_evidence": {"verdict": "certified"},
            }
            records.append({
                "kind": "property", "name": name, "status": status,
                "proof_tier": "beacon", "samples": 0, "arith_model": "real",
                "qualifiers": ["real_arithmetic"], "engine_evidence": evidence,
                "counterexample": {"confirmed": True} if status == "failed" else None,
            })
        records.append({"kind": "summary"})
        self.assertEqual(GATE.check_records(records), [])
        wrong = copy.deepcopy(records)
        wrong[0]["engine_evidence"]["source_binding"]["declarations"] = []
        self.assertTrue(GATE.check_records(wrong))
        wrong = copy.deepcopy(records)
        wrong[2]["counterexample"] = None
        self.assertTrue(GATE.check_records(wrong))


if __name__ == "__main__":
    unittest.main()
