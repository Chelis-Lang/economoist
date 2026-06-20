#!/usr/bin/env python3
"""The SMT-green gate: the spine of Economoist.

Every economic property in this shell must discharge at the SMT tier as a
genuine unqualified green (cvc5, over the reals, zero fuzz samples, no contract
assumption). A property that comes back sampled (fuzz), unsupported, or
contract-qualified is a bug, not a result. This gate enforces that, plus the
non-vacuity and soundness-dependence probes and the honesty-boundary name lint.

It reads the newline-delimited JSON that `chelis prove --json` emits and checks,
per record:

  Economic greens (src/ invariant-producer obligations, and the real properties
  in properties/): status==passed, proof_tier=="smt", samples==0,
  composite_verdict=="proven"; properties carry no assumptions (no contract);
  obligations carry only SMT-discharged invariant assumptions with established
  non-vacuity (the legitimate input invariant, not a fuzz-validated contract).

  Non-vacuity witnesses (properties/ names ending `_guards_satisfiable`): must be
  refuted at the SMT tier, so cvc5 exhibits a guard-satisfying model and the
  matching green is not vacuous.

  Soundness twins / controls (demos/): names ending `_wrong` must be refuted;
  names ending `_control` must pass.

  Name lint: no @property/def/type identifier in src/, properties/, or demos/ may
  name a held-out limit theorem (converge, stationary, fixed_point, ergodic,
  limit, iterate). Each docs/models/*.md that makes a universal-dimension claim
  must carry a held-out caveat in the same file.

Exit 0 only if every check passes.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

FORBIDDEN_NAME = re.compile(r"(converge|stationary|fixed_point|ergodic|limit|iterat)", re.I)
DECL_NAME = re.compile(r"^\s*(?:@property|def|type)\s+([A-Za-z_][A-Za-z0-9_]*)")
UNIVERSAL_CLAIM = re.compile(r"(for all n|general[- ]n|any dimension|all dimensions|universal theorem)", re.I)
HELD_OUT = re.compile(r"held[- ]out", re.I)


def resolve_bin() -> str:
    for env in ("CHELIS_SMT_BIN", "CHELIS_BIN"):
        v = os.environ.get(env)
        if v and (Path(v).expanduser().is_file() or _on_path(v)):
            return str(Path(v).expanduser())
    default = Path.home() / ".local/share/chelis/0.8.0/chelis-smt"
    if default.is_file():
        return str(default)
    for cand in ("chelis-smt", "chelis"):
        if _on_path(cand):
            return cand
    sys.exit("error: no chelis smt binary found; set CHELIS_SMT_BIN")


def _on_path(name: str) -> bool:
    from shutil import which
    return which(name) is not None


def run_prove(binary: str, ch: Path, tier: str) -> list[dict]:
    proc = subprocess.run(
        [binary, "prove", str(ch), "--json", "--tier", tier, "--smt-timeout", "15000"],
        cwd=REPO_ROOT, capture_output=True, text=True,
    )
    records = []
    for line in proc.stdout.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            records.append(json.loads(line))
        except json.JSONDecodeError:
            pass
    if proc.returncode not in (0, 1):  # 1 = a property refuted (expected for witnesses/twins)
        sys.stderr.write(proc.stdout + proc.stderr)
    return records


def _assumptions_clean(r: dict) -> tuple[bool, str]:
    """Every assumption must be a legitimate precondition or input invariant,
    SMT-discharged (never a fuzz-validated contract), with non-vacuity
    established. The prover attaches a `preconditions:` assumption to every
    guarded property and runs its non-vacuity check with cvc5; a fuzz-validated
    contract (the over-firing abstraction this shell forbids) shows up as
    discharge.method != "smt" and composite_verdict != "proven"."""
    for a in r.get("assumptions", []):
        method = a.get("discharge", {}).get("method")
        if method != "smt":
            return False, f"assumption '{a.get('name')}' discharged by {method}, not smt (contract over-firing)"
        nv = a.get("non_vacuity")
        if nv is not None and nv.get("status") != "established":
            return False, f"assumption '{a.get('name')}' non-vacuity not established (vacuous guards?)"
    return True, ""


def green_property(r: dict) -> tuple[bool, str]:
    if r.get("status") != "passed":
        return False, f"status={r.get('status')} reason={r.get('reason')}"
    if r.get("proof_tier") != "smt":
        return False, f"proof_tier={r.get('proof_tier')} (amber/fuzz is a bug here)"
    if r.get("samples", -1) != 0:
        return False, f"samples={r.get('samples')} (nonzero fuzz samples)"
    if r.get("composite_verdict") != "proven":
        return False, f"composite_verdict={r.get('composite_verdict')} (must be unqualified proven)"
    if r.get("arith_model") != "real":
        return False, f"arith_model={r.get('arith_model')} (must be real; the proof is over the reals)"
    ok, why = _assumptions_clean(r)
    if not ok:
        return False, why
    return True, "smt-green"


def green_obligation(r: dict) -> tuple[bool, str]:
    if r.get("status") != "passed":
        return False, f"status={r.get('status')} reason={r.get('reason')}"
    if r.get("proof_tier") != "smt" or r.get("arith_model") != "real":
        return False, f"proof_tier={r.get('proof_tier')} arith_model={r.get('arith_model')}"
    if r.get("samples", -1) != 0 or r.get("composite_verdict") != "proven":
        return False, f"samples={r.get('samples')} verdict={r.get('composite_verdict')}"
    ok, why = _assumptions_clean(r)
    if not ok:
        return False, why
    return True, "smt-green obligation"


def gate_file(binary: str, ch: Path, tier: str, failures: list[str]) -> None:
    rel = ch.relative_to(REPO_ROOT)
    records = run_prove(binary, ch, tier)
    seen = 0
    for r in records:
        kind = r.get("kind")
        name = r.get("name", "")
        if kind == "error":
            failures.append(f"{rel}: prove error: {r.get('reason')}")
            continue
        if kind == "obligation":
            seen += 1
            ok, why = green_obligation(r)
            if not ok:
                failures.append(f"{rel}: obligation {name}: {why}")
        elif kind == "property":
            seen += 1
            if name.endswith("_guards_satisfiable"):
                if not (r.get("status") == "failed" and r.get("proof_tier") == "smt"):
                    failures.append(f"{rel}: non-vacuity witness {name} did not refute at smt: status={r.get('status')} tier={r.get('proof_tier')}")
            elif ch.parent.name == "demos" and name.endswith("_wrong"):
                if r.get("status") != "failed":
                    failures.append(f"{rel}: soundness twin {name} did not refute: status={r.get('status')}")
            elif ch.parent.name == "demos" and name.endswith("_control"):
                if r.get("status") != "passed":
                    failures.append(f"{rel}: control {name} did not pass: status={r.get('status')} reason={r.get('reason')}")
            elif ch.parent.name == "demos":
                failures.append(f"{rel}: demo property {name} must end in _wrong or _control (classification discipline)")
            else:
                ok, why = green_property(r)
                if not ok:
                    failures.append(f"{rel}: property {name}: {why}")
    if seen == 0 and ch.parent.name in ("properties", "demos"):
        failures.append(f"{rel}: no property or obligation records found")


def name_lint(failures: list[str]) -> None:
    for d in ("src", "properties", "demos"):
        for ch in sorted((REPO_ROOT / d).glob("*.ch")):
            for i, line in enumerate(ch.read_text().splitlines(), 1):
                m = DECL_NAME.match(line)
                if m and FORBIDDEN_NAME.search(m.group(1)):
                    failures.append(f"{ch.relative_to(REPO_ROOT)}:{i}: identifier '{m.group(1)}' names a held-out limit theorem; rename to its single-step content")


def doc_lint(failures: list[str]) -> None:
    models = REPO_ROOT / "docs" / "models"
    for md in sorted(models.glob("*.md")) if models.exists() else []:
        text = md.read_text()
        if UNIVERSAL_CLAIM.search(text) and not HELD_OUT.search(text):
            failures.append(f"{md.relative_to(REPO_ROOT)}: makes a universal-dimension claim without a held-out caveat in the same file")


def main() -> int:
    binary = resolve_bin()
    print(f"prove_gate using {binary}")
    failures: list[str] = []

    for d, tier in (("src", "smt-only"), ("properties", "smt-only"), ("demos", "auto")):
        for ch in sorted((REPO_ROOT / d).glob("*.ch")):
            gate_file(binary, ch, tier, failures)

    name_lint(failures)
    doc_lint(failures)

    if failures:
        print(f"\nprove_gate FAILED with {len(failures)} finding(s):")
        for f in failures:
            print(f"  FAIL {f}")
        return 1
    print("prove_gate OK: every economic property is an unqualified SMT green; witnesses refute; twins refute; controls pass; name and doc lints clean.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
