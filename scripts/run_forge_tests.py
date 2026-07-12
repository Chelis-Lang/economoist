#!/usr/bin/env python3
"""Executable forge negatives for the metamorphic anti-vacuity check.

The syntactic anti-vacuity check (prove_gate's "the goal calls the output fn")
is forgeable: a canceling call `F(x) - F(x) < c` or a reflexive `F(x) == F(x)`
references F textually and passes the goal-string check AND an honest violating
control, yet is true for ANY F -- a vacuous green that does not test the model.
This harness builds a tiny throwaway package with exactly those forge greens plus
an honest control, and asserts prove_gate's metamorphic check (re-prove with F's
body substituted, require the verdict to flip) REJECTS the forges and ACCEPTS the
honest green. It is the adversarial negative that unit tests over the real corpus
would miss.

Python-stdlib-only. Exit 0 only if the metamorphic check behaves as required.
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import prove_gate as pg  # noqa: E402

REEF = '''\
[package]
name = "forge"
version = "0.0.0"
compiler = "=0.14.0"
module_prefix = "Forge"
additional_sources = ["properties"]

[dependencies]
chelis-std = { version = "0.4.0" }
'''

MODEL = '''\
module Forge.Model
export (ff)
def ff(x: f32) -> f32 = (x * x)
'''

# Three greens, all proven with the real ff, all passing the goal-string check
# (each calls ff) and trivially pairable with an honest violating control:
#   forge_canceling / forge_reflexive : model-INDEPENDENT (true for any ff) -- the
#     metamorphic check must REJECT (no substitution flips them).
#   honest_positive : model-DEPENDENT (ff := -x makes it false) -- must be ACCEPTED.
PROPS = '''\
module Forge.Properties.Forge
import Forge.Model (ff)
@property forge_canceling forall(x: f32) where (x > 0.0):
  ((ff(x) - ff(x)) < 1.0)
@property forge_reflexive forall(x: f32) where (x > 0.0):
  (ff(x) == ff(x))
@property honest_positive forall(x: f32) where (x > 1.0):
  (ff(x) > 0.0)
'''


def main() -> int:
    binary = pg.resolve_bin()
    with tempfile.TemporaryDirectory(prefix="forge-pkg-") as tmp:
        pkg = Path(tmp)
        (pkg / "src").mkdir()
        (pkg / "properties").mkdir()
        (pkg / "reef.toml").write_text(REEF)
        (pkg / "src" / "model.ch").write_text(MODEL)
        (pkg / "properties" / "forge.ch").write_text(PROPS)

        expectations = [
            ("forge_canceling", False, "canceling F(x)-F(x) is model-independent -> must be REJECTED"),
            ("forge_reflexive", False, "reflexive F(x)==F(x) is model-independent -> must be REJECTED"),
            ("honest_positive", True, "F(x)>0 depends on F -> must be ACCEPTED"),
        ]
        failures = []
        for name, want_flip, why in expectations:
            got_flip, detail = pg.metamorphic_flips(binary, pkg, "ff", "properties/forge.ch", name)
            verdict = "ACCEPT" if got_flip else "REJECT"
            ok = got_flip == want_flip
            print(f"  {'OK  ' if ok else 'FAIL'} {name:16} metamorphic={verdict:6} ({why})")
            if not ok:
                failures.append(f"{name}: metamorphic returned flip={got_flip}, expected {want_flip} -- {detail}")

    if failures:
        print(f"\nrun_forge_tests FAILED with {len(failures)} finding(s):")
        for f in failures:
            print(f"  FAIL {f}")
        return 1
    print("run_forge_tests OK: the metamorphic check rejects the canceling/reflexive forges and accepts the honest green.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
