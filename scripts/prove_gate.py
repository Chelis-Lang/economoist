#!/usr/bin/env python3
"""The SMT-green gate: the spine of Economoist.

Every economic property in this shell must discharge at the SMT tier as a
genuine unqualified green (cvc5, over the reals, zero fuzz samples, no contract
assumption). A property that comes back sampled (fuzz), unsupported, or
contract-qualified is a bug, not a result. This gate enforces that, plus the
non-vacuity and soundness-dependence probes and the honesty-boundary name lint.

The unqualified-green verdict token is `proven_modulo_real_arithmetic` (chelis
0.9.0): cvc5 proved the goal in real arithmetic and is honest that it did not
also discharge the f32 rounding behaviour, which is exactly this shell's stated
boundary ("proven over the reals, not f32"). The older plain `proven` token is
also accepted. A qualified token -- `fuzz_validated`, `sound_approximate`,
`proven_modulo_fuzz_validated_contract` -- is a weaker result and stays a bug
here. See UNQUALIFIED_GREEN_VERDICTS below.

It reads the newline-delimited JSON that `chelis prove --json` emits and checks,
per record:

  Economic greens (src/ invariant-producer obligations, and the real properties
  in properties/): status==passed, proof_tier=="smt", samples==0,
  composite_verdict in UNQUALIFIED_GREEN_VERDICTS; properties carry no
  assumptions (no contract); obligations carry only SMT-discharged invariant
  assumptions with established non-vacuity (the legitimate input invariant, not
  a fuzz-validated contract).

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

# The two unqualified-green verdict tokens this shell accepts. From chelis 0.9.0
# a genuine SMT discharge over the reals reports `proven_modulo_real_arithmetic`
# (the prover proved the goal in real arithmetic and is honest that it has not
# also discharged the f32 rounding behaviour); `proven` is the older unqualified
# token, kept for forward/backward overlap. Both are unqualified greens for a
# shell whose stated boundary is "proven over the reals, not f32". Every other
# token -- `fuzz_validated`, `sound_approximate`,
# `proven_modulo_fuzz_validated_contract` -- is a weaker, qualified result and
# stays REJECTED: economoist's honesty boundary is pure SMT over the reals with
# no fuzz fallback and no contract assumption.
UNQUALIFIED_GREEN_VERDICTS = frozenset({"proven_modulo_real_arithmetic", "proven"})

FORBIDDEN_NAME = re.compile(r"(converge|stationary|fixed_point|ergodic|limit|iterat)", re.I)
DECL_NAME = re.compile(r"^\s*(?:@property|def|type)\s+([A-Za-z_][A-Za-z0-9_]*)")
UNIVERSAL_CLAIM = re.compile(r"(for all n|general[- ]n|any dimension|all dimensions|universal theorem)", re.I)
HELD_OUT = re.compile(r"held[- ]out", re.I)
# chelis#426: comparing/subtracting two calls of an ITE-bodied operator def at a
# goal site false-proves. The sound form inlines the operator arithmetic, so a
# property/demo goal must never CALL one of these operators.
ITE_OPERATOR_CALL = re.compile(r"\bbellman_state\d\w*\s*\(")


def resolve_bin() -> str:
    """Resolve the chelis binary: CHELIS_SMT_BIN/CHELIS_BIN override, else the
    reef.toml-pinned release install (~/.local/share/chelis/<pin>/bin/chelis, or
    the top-level layout), else `chelis` on PATH. SMT ships in the release binary
    as of chelis v0.11.0 (chelis#422 resolved), so there is no separate
    from-source smt binary to prefer any more."""
    for env in ("CHELIS_SMT_BIN", "CHELIS_BIN"):
        v = os.environ.get(env)
        if v and (Path(v).expanduser().is_file() or _on_path(v)):
            return str(Path(v).expanduser())
    m = re.search(r'compiler\s*=\s*"=([^"]+)"', (REPO_ROOT / "reef.toml").read_text())
    if m:
        base = Path.home() / ".local/share/chelis" / m.group(1)
        for cand in (base / "bin" / "chelis", base / "chelis"):
            if cand.is_file():
                return str(cand)
    if _on_path("chelis"):
        return "chelis"
    sys.exit("error: no chelis binary found; set CHELIS_SMT_BIN or CHELIS_BIN")


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
    discharge.method != "smt" and a composite_verdict outside
    UNQUALIFIED_GREEN_VERDICTS."""
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
    if r.get("composite_verdict") not in UNQUALIFIED_GREEN_VERDICTS:
        return False, f"composite_verdict={r.get('composite_verdict')} (must be an unqualified green: {sorted(UNQUALIFIED_GREEN_VERDICTS)})"
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
    if r.get("samples", -1) != 0 or r.get("composite_verdict") not in UNQUALIFIED_GREEN_VERDICTS:
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


def unsound_pattern_lint(failures: list[str]) -> None:
    """Guard against the chelis#426 vacuous-green pattern: a property or demo goal
    must inline the operator arithmetic, never CALL an ITE-bodied operator def
    (comparing/subtracting two such calls reports a false `proven`). Comments are
    ignored so the explanatory notes about the bug do not trip the lint."""
    for d in ("properties", "demos"):
        for ch in sorted((REPO_ROOT / d).glob("*.ch")):
            for i, line in enumerate(ch.read_text().splitlines(), 1):
                code = line.split("--", 1)[0]
                if ITE_OPERATOR_CALL.search(code):
                    failures.append(f"{ch.relative_to(REPO_ROOT)}:{i}: goal calls an ITE-bodied operator ({code.strip()[:48]}); inline the arithmetic instead (chelis#426 two-call false-proven)")


def doc_lint(failures: list[str]) -> None:
    models = REPO_ROOT / "docs" / "models"
    for md in sorted(models.glob("*.md")) if models.exists() else []:
        text = md.read_text()
        if UNIVERSAL_CLAIM.search(text) and not HELD_OUT.search(text):
            failures.append(f"{md.relative_to(REPO_ROOT)}: makes a universal-dimension claim without a held-out caveat in the same file")


def honesty_boundary_self_test() -> None:
    """The honesty boundary, checked before any prove runs: green_property and
    green_obligation accept ONLY the two unqualified-green tokens and reject
    every qualified verdict, even one that wears a clean smt/real/zero-sample
    mask. This is the negative probe for the 0.9.0 verdict-taxonomy widening:
    membership in UNQUALIFIED_GREEN_VERDICTS must not have leaked into a fuzz or
    contract verdict. Raises AssertionError (caught and reported by main) on any
    drift, so a future widening of the accept set cannot pass silently."""

    def rec(verdict: str) -> dict:
        # An otherwise-perfect smt/real/zero-sample record; only the verdict varies.
        return {"status": "passed", "proof_tier": "smt", "samples": 0,
                "arith_model": "real", "composite_verdict": verdict, "assumptions": []}

    accept = ("proven_modulo_real_arithmetic", "proven")
    reject = ("fuzz_validated", "sound_approximate",
              "proven_modulo_fuzz_validated_contract", "failed", "unsupported")

    for v in accept:
        for name, fn in (("green_property", green_property), ("green_obligation", green_obligation)):
            ok, why = fn(rec(v))
            assert ok, f"honesty self-test: {name} rejected unqualified-green verdict {v!r}: {why}"
    for v in reject:
        for name, fn in (("green_property", green_property), ("green_obligation", green_obligation)):
            ok, _ = fn(rec(v))
            assert not ok, f"honesty self-test: {name} ACCEPTED qualified verdict {v!r} (honesty boundary breached)"
    # A genuinely fuzz-tier record (a goal that fell back to fuzz, or output from
    # a build without the smt feature) must be rejected by the tier check too,
    # independent of its verdict.
    ok, _ = green_property({"status": "passed", "proof_tier": "fuzz", "samples": 100,
                            "arith_model": "real", "composite_verdict": "fuzz_validated",
                            "assumptions": []})
    assert not ok, "honesty self-test: green_property accepted a fuzz-tier record"


def main() -> int:
    failures: list[str] = []
    try:
        honesty_boundary_self_test()
    except AssertionError as e:
        print(f"prove_gate FAILED: {e}")
        return 1

    binary = resolve_bin()
    print(f"prove_gate using {binary}")

    for d, tier in (("src", "smt-only"), ("properties", "smt-only"), ("demos", "auto")):
        for ch in sorted((REPO_ROOT / d).glob("*.ch")):
            gate_file(binary, ch, tier, failures)

    name_lint(failures)
    unsound_pattern_lint(failures)
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
