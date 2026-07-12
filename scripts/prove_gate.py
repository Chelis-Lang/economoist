#!/usr/bin/env python3
"""The SMT-green keystone gate: the spine of Economoist, manifest-driven.

Every economic property in the `properties/` tree must discharge at the SMT tier
as a genuine unqualified green (cvc5, over the reals, zero fuzz, no contract). The
weaker `sampled/` tree is honest amber (fuzz-validated). This gate enforces both,
DRIVEN BY docs/cnote-import-surface.json (the characterization contract manifest,
chelis-shell.invariant-surface/1.0), against the pinned RELEASE binary.

Per the contract, an achieved tier is classified from `proof_tier` + assumption
discharge methods + `qualifiers`, NEVER from the `composite_verdict` string (a
verdict token may demote a result, never promote it). For each manifest invariant
the gate checks:

  1. satisfying control holds, classified tier == expected_tier_per_pin[pin]
     (drift in EITHER direction fails -- better-than-expected means "run the
     de-narrowing motion"); assumptions' non_vacuity established; the goal
     references the shipped output fn (anti-vacuity, read from the prover-emitted
     goal string because dependency_edges does not cross the module import
     boundary -- docs/issue_drafts/dependency_edges_imports.md);
  2. violating control breaks with a concrete in-domain witness. For a defective
     model (in-region defect) the witness must satisfy every precondition AND the
     f32 re-execution of the shipped body at the witness must reproduce the break;
     for an out-of-region break the witness must violate a precondition; for a
     fuzz-lane break the counterexample is in-domain f32 by construction.
  3. (properties/ proven greens) METAMORPHIC anti-vacuity: re-proving the same
     goal with the referenced output fn's body substituted by distinct
     alternatives must flip the verdict (proven -> disproved) under at least one,
     so the green genuinely depends on the model. A canceling `F(x)-F(x)` or
     reflexive `F(x)==F(x)` goal survives every substitution and is rejected --
     the syntactic goal-string reference check alone cannot catch that.

Beyond the manifest it keeps the shell's structural discipline: every
`properties/` green is SMT/real/zero-sample; `*_guards_satisfiable` witnesses
refute at SMT; `demos/` names end `_wrong` (refute) or `_control` (pass);
`sampled/` greens are fuzz-passed and never collide with a `properties/` green;
name lint (no held-out limit-theorem identifiers) and doc lint run over
`src/ properties/ demos/ sampled/`; and an honesty self-test runs first.

Python-stdlib-only. Exit 0 only if every check passes.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from fractions import Fraction
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
MANIFEST = REPO_ROOT / "docs" / "cnote-import-surface.json"

FORBIDDEN_NAME = re.compile(r"(converge|stationary|fixed_point|ergodic|limit|iterat)", re.I)
DECL_NAME = re.compile(r"^\s*(?:@property|def|type)\s+([A-Za-z_][A-Za-z0-9_]*)")
UNIVERSAL_CLAIM = re.compile(r"(for all n|general[- ]n|any dimension|all dimensions|universal theorem)", re.I)
HELD_OUT = re.compile(r"held[- ]out", re.I)


# ----------------------------------------------------------------------------
# Binary resolution (env-first -> reef.toml-pinned release install -> PATH).
# SMT ships in the release binary since chelis v0.11.0 (chelis#422 resolved).
# ----------------------------------------------------------------------------
def resolve_bin() -> str:
    # Env precedence is CHELIS_BIN then CHELIS_SMT_BIN, uniform across every
    # economoist script (the CHELIS_SMT_BIN alias survives from the pre-0.11.0
    # two-binary era).
    for env in ("CHELIS_BIN", "CHELIS_SMT_BIN"):
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
    sys.exit("error: no chelis binary found; set CHELIS_BIN")


def _on_path(name: str) -> bool:
    return shutil.which(name) is not None


def assert_version(binary: str, pin: str) -> None:
    """Post-resolution guard: the resolved binary must be the reef-pinned version,
    so a stale `chelis` on PATH cannot silently gate a different compiler."""
    got = subprocess.run([binary, "--version"], capture_output=True, text=True).stdout.strip()
    if got != f"chelis {pin}":
        sys.exit(f"prove_gate: resolved binary reports {got!r}, expected 'chelis {pin}' (reef pin); set CHELIS_BIN")


# ----------------------------------------------------------------------------
# Prove + classify.
# ----------------------------------------------------------------------------
def run_prove(binary: str, ch: Path, tier: str, *, samples: int | None = None,
              smt_timeout: int = 15000, cwd: Path | None = None) -> dict[str, dict]:
    """Prove a file; return {property_name: record} for kind==property/obligation.
    Prover errors are collected under the '__errors__' key."""
    cmd = [binary, "prove", str(ch), "--json", "--tier", tier]
    if samples is not None:
        cmd += ["--samples", str(samples), "--seed", "0"]
    else:
        cmd += ["--smt-timeout", str(smt_timeout)]
    proc = subprocess.run(cmd, cwd=str(cwd or REPO_ROOT), capture_output=True, text=True)
    records: dict[str, dict] = {}
    for line in proc.stdout.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            r = json.loads(line)
        except json.JSONDecodeError:
            continue
        if r.get("kind") in ("property", "obligation"):
            records[r.get("name", "")] = r
        elif r.get("kind") == "error":
            records.setdefault("__errors__", {"reasons": []})["reasons"].append(r.get("reason"))
    if proc.returncode not in (0, 1, 2, 3) and not records:
        sys.stderr.write(proc.stdout + proc.stderr)
    return records


def classify_tier(r: dict) -> str:
    """Classify the achieved tier from proof_tier + assumptions + qualifiers,
    NEVER from composite_verdict (contract classification rule)."""
    status = r.get("status")
    tier = r.get("proof_tier")
    quals = set(r.get("qualifiers") or [])
    if status == "passed":
        if tier == "smt":
            if any(q.startswith("contract:") or q == "fuzz" for q in quals):
                return "proven_modulo_contract"
            for a in r.get("assumptions", []):
                if a.get("discharge", {}).get("method") not in ("smt", None):
                    return "proven_modulo_contract"
            return "proven"
        if tier == "fuzz":
            return "fuzz_validated"
        return "unknown"
    if status == "failed":
        return "disproved"
    if status == "unsupported":
        return "unsupported"
    if status == "error":
        return "error"
    return "unknown"


def assumptions_clean(r: dict) -> tuple[bool, str]:
    for a in r.get("assumptions", []):
        method = a.get("discharge", {}).get("method")
        if method != "smt":
            return False, f"assumption '{a.get('name')}' discharged by {method}, not smt"
        nv = a.get("non_vacuity")
        if nv is not None and nv.get("status") != "established":
            return False, f"assumption '{a.get('name')}' non-vacuity not established"
    return True, ""


# ----------------------------------------------------------------------------
# Structural discipline over the proven files (properties/ demos/ src obligations).
# ----------------------------------------------------------------------------
def green_property(r: dict) -> tuple[bool, str]:
    if classify_tier(r) != "proven":
        return False, f"tier={classify_tier(r)} (status={r.get('status')}, proof_tier={r.get('proof_tier')}); properties/ must be unqualified SMT green"
    if r.get("samples", -1) != 0:
        return False, f"samples={r.get('samples')} (nonzero fuzz samples)"
    if r.get("arith_model") != "real":
        return False, f"arith_model={r.get('arith_model')} (must be real)"
    ok, why = assumptions_clean(r)
    return (ok, "smt-green" if ok else why)


def green_obligation(r: dict) -> tuple[bool, str]:
    if classify_tier(r) != "proven":
        return False, f"tier={classify_tier(r)} (obligation must be unqualified SMT green)"
    if r.get("samples", -1) != 0 or r.get("arith_model") != "real":
        return False, f"samples={r.get('samples')} arith_model={r.get('arith_model')}"
    ok, why = assumptions_clean(r)
    return (ok, "smt-green obligation" if ok else why)


def gate_proven_file(records: dict, ch: Path, failures: list[str]) -> None:
    rel = ch.relative_to(REPO_ROOT)
    seen = 0
    for name, r in records.items():
        if name == "__errors__":
            for reason in r.get("reasons", []):
                failures.append(f"{rel}: prove error: {reason}")
            continue
        if r.get("kind") == "obligation":
            seen += 1
            ok, why = green_obligation(r)
            if not ok:
                failures.append(f"{rel}: obligation {name}: {why}")
        elif r.get("kind") == "property":
            seen += 1
            if name.endswith("_guards_satisfiable"):
                if not (r.get("status") == "failed" and r.get("proof_tier") == "smt"):
                    failures.append(f"{rel}: non-vacuity witness {name} did not refute at smt: status={r.get('status')} tier={r.get('proof_tier')}")
            elif ch.parent.name == "demos":
                if name.endswith("_wrong"):
                    if r.get("status") != "failed":
                        failures.append(f"{rel}: soundness twin {name} did not refute: status={r.get('status')}")
                elif name.endswith("_control"):
                    if r.get("status") != "passed":
                        failures.append(f"{rel}: control {name} did not pass: status={r.get('status')} reason={r.get('reason')}")
                else:
                    failures.append(f"{rel}: demo property {name} must end in _wrong or _control")
            else:
                ok, why = green_property(r)
                if not ok:
                    failures.append(f"{rel}: property {name}: {why}")
    if seen == 0 and ch.parent.name in ("properties", "demos"):
        failures.append(f"{rel}: no property or obligation records found")


def gate_sampled_file(records: dict, ch: Path, failures: list[str]) -> None:
    """sampled/: greens must be fuzz-passed (fuzz_validated); _wrong must refute."""
    rel = ch.relative_to(REPO_ROOT)
    seen = 0
    for name, r in records.items():
        if name == "__errors__":
            for reason in r.get("reasons", []):
                failures.append(f"{rel}: prove error: {reason}")
            continue
        if r.get("kind") != "property":
            continue
        seen += 1
        if name.endswith("_wrong"):
            if r.get("status") != "failed" or not r.get("counterexample"):
                failures.append(f"{rel}: sampled twin {name} did not refute with a counterexample: status={r.get('status')}")
        elif classify_tier(r) != "fuzz_validated":
            failures.append(f"{rel}: sampled green {name}: tier={classify_tier(r)} (must be fuzz_validated: proof_tier fuzz, passed)")
    if seen == 0:
        failures.append(f"{rel}: no property records found")


# ----------------------------------------------------------------------------
# Witness evaluation (in-domain check + f32 re-execution).
# ----------------------------------------------------------------------------
_VAR_EXPR = re.compile(r"^[\w\s+\-*/.()]+$")


def _val(s: str) -> Fraction:
    """Parse a counterexample value. cvc5 emits exact reals as SMT-LIB
    S-expressions -- `(/ 1 2)`, `(- 1.0)`, `(/ (- 1) 2)` -- as well as plain
    decimals/integers; both must land as an exact Fraction."""
    s = s.strip()
    if s.startswith("("):
        return _parse_sexpr(s)
    try:
        return Fraction(s)
    except (ValueError, ZeroDivisionError):
        return Fraction(float(s))


def _parse_sexpr(s: str) -> Fraction:
    toks = re.findall(r"\(|\)|[^\s()]+", s)
    pos = [0]

    def parse() -> Fraction:
        t = toks[pos[0]]
        pos[0] += 1
        if t == "(":
            op = toks[pos[0]]
            pos[0] += 1
            args = []
            while toks[pos[0]] != ")":
                args.append(parse())
            pos[0] += 1  # consume ')'
            if op == "/":
                return args[0] / args[1]
            if op == "*":
                r = Fraction(1)
                for a in args:
                    r *= a
                return r
            if op == "+":
                return sum(args, Fraction(0))
            if op == "-":
                return -args[0] if len(args) == 1 else args[0] - sum(args[1:], Fraction(0))
            raise ValueError(f"unknown S-expr op {op!r}")
        try:
            return Fraction(t)
        except (ValueError, ZeroDivisionError):
            return Fraction(float(t))

    return parse()


def eval_arith(expr: str, env: dict[str, Fraction]) -> Fraction:
    if not _VAR_EXPR.match(expr):
        raise ValueError(f"unsafe expr {expr!r}")
    return eval(expr, {"__builtins__": {}}, dict(env))  # noqa: S307 -- whitelisted chars, trusted manifest


def precond_holds(pc: dict, env: dict[str, Fraction]) -> bool:
    lhs = eval_arith(pc["lhs"], env)
    rhs = pc["rhs"]
    if "const" in rhs:
        rv = Fraction(str(rhs["const"]))
    elif "input" in rhs:
        rv = env[rhs["input"]]
    else:  # {"expr": ...} -- a margin/relational RHS such as "g + 0.01"
        rv = eval_arith(rhs["expr"], env)
    op = pc["op"]
    return {"gt": lhs > rv, "gte": lhs >= rv, "lt": lhs < rv,
            "lte": lhs <= rv, "eq": lhs == rv}[op]


def witness_env(cx: dict) -> dict[str, Fraction]:
    env: dict[str, Fraction] = {}
    for k, v in cx.items():
        try:
            env[k] = _val(str(v))
        except Exception:  # noqa: BLE001
            pass
    return env


def _safe_precond(pc: dict, env: dict[str, Fraction]) -> bool:
    try:
        return precond_holds(pc, env)
    except Exception:  # noqa: BLE001
        return False


def output_fn_body(fn: str) -> tuple[list[str], str] | None:
    """Parse `def fn(params) -> ret = body` from src/; return (param_names, body)."""
    for ch in sorted((REPO_ROOT / "src").glob("*.ch")):
        m = re.search(rf'^\s*def\s+{re.escape(fn)}\s*\(([^)]*)\)\s*->\s*[^=]+=\s*(.+)$',
                      ch.read_text(), re.M)
        if m:
            params = [p.split(":")[0].strip() for p in m.group(1).split(",") if p.strip()]
            return params, m.group(2).strip()
    return None


def f32_reexec_positive_break(binary: str, fn: str, cx: dict) -> tuple[bool, str]:
    """Evaluate the shipped output_fn body at the witness in f32 and confirm the
    positivity break (value <= 0.0). Substitutes each param with cast(value, f32)
    into the exported single-expression body (eval does not resolve the import, so
    the inline body is used -- textually the shipped def)."""
    parsed = output_fn_body(fn)
    if parsed is None:
        return False, f"could not parse body of {fn} from src/"
    params, body = parsed
    expr = body
    for p in params:
        if p not in cx:
            return False, f"witness has no value for parameter {p}"
        expr = re.sub(rf'\b{re.escape(p)}\b', f"cast({float(_val(str(cx[p])))!r}, f32)", expr)
    proc = subprocess.run([binary, "eval", "--json", expr], capture_output=True, text=True)
    if proc.returncode != 0:
        return False, f"eval failed: {proc.stderr.strip()[:120]}"
    try:
        value = float(json.loads(proc.stdout)["roots"][0]["value"]["value"])
    except Exception as exc:  # noqa: BLE001
        return False, f"could not parse eval output ({exc})"
    if value <= 0.0:
        return True, f"f32 value {value:.6g} <= 0 confirms the in-region positivity break"
    return False, f"f32 re-execution gave {value:.6g} > 0 -- break did NOT reproduce in-domain"


# ----------------------------------------------------------------------------
# Manifest-driven invariant enforcement.
# ----------------------------------------------------------------------------
def gate_manifest(binary: str, manifest: dict, records: dict[str, dict],
                  pin: str, failures: list[str]) -> int:
    output_fns = {m["output_fn"] for m in manifest.get("models", [])}
    checked = 0
    for inv in manifest.get("invariants", []):
        iid = inv["id"]
        ctl = inv["controls"]
        sat_name = ctl["satisfying"]["name"]
        viol_name = ctl["violating"]["name"]
        expected = inv.get("expected_tier_per_pin", {}).get(pin)

        sat = records.get(sat_name)
        viol = records.get(viol_name)
        if sat is None:
            failures.append(f"{iid}: satisfying control {sat_name} produced no record")
            continue
        if viol is None:
            failures.append(f"{iid}: violating control {viol_name} produced no record")
            continue
        checked += 1

        # (1) satisfying: tier match (drift either direction fails), passes,
        # references a shipped output fn, assumptions clean.
        got = classify_tier(sat)
        if got != expected:
            failures.append(f"{iid}: tier drift -- {sat_name} classified {got!r}, manifest expects {expected!r} (run the de-narrowing motion)")
        if sat.get("status") != "passed":
            failures.append(f"{iid}: satisfying control {sat_name} did not pass: {sat.get('status')}")
        # anti-vacuity. `direct` must reference a shipped output fn in its goal
        # (read from the prover-emitted goal string, since dependency_edges does
        # not cross the module import boundary). `equivalent-form` deliberately
        # inlines the shipped body (e.g. grad-through-import does not lower), so
        # it is anti-vacuous by its probe citation plus the corrupt-flip control;
        # the citation must be present.
        binding = inv.get("binding", {})
        ref_mode = binding.get("references_output_fn")
        goal = re.sub(r"\s+", "", sat.get("goal", ""))
        if ref_mode == "equivalent-form":
            if not binding.get("equivalent_form_citation"):
                failures.append(f"{iid}: references_output_fn 'equivalent-form' but no equivalent_form_citation")
        elif not any(f"{fn}(" in goal for fn in output_fns):
            failures.append(f"{iid}: satisfying control {sat_name} goal references no shipped output fn (vacuity tell)")
        if expected == "proven":
            ok, why = assumptions_clean(sat)
            if not ok:
                failures.append(f"{iid}: {sat_name}: {why}")

        # (2) violating: breaks with an in-domain witness.
        if viol.get("status") != "failed":
            failures.append(f"{iid}: violating control {viol_name} did not refute: {viol.get('status')}")
            continue
        cx = viol.get("counterexample")
        if not cx:
            failures.append(f"{iid}: violating control {viol_name} refuted without a counterexample")
            continue
        env = witness_env(cx)
        preconds = inv.get("preconditions", [])
        defective = inv.get("defective_model")

        if viol.get("proof_tier") == "fuzz":
            pass  # fuzz counterexample is in-domain f32 by construction (contract).
        elif defective:
            unmet = [precond_string(pc) for pc in preconds if not _safe_precond(pc, env)]
            if unmet:
                failures.append(f"{iid}: in-region-defect witness {cx} does NOT satisfy preconditions {unmet}")
            model = next((m for m in manifest["models"] if m["id"] == defective), None)
            if model:
                ok, why = f32_reexec_positive_break(binary, model["output_fn"], cx)
                if not ok:
                    failures.append(f"{iid}: {why}")
        else:
            # out-of-region break: the witness must VIOLATE at least one
            # precondition (leave the validity region). An eval error here is
            # fail-closed -- we cannot confirm the witness leaves the region -- so
            # it is reported, not silently skipped (matching the in-region path).
            evaluated: list[bool | None] = []
            for pc in preconds:
                try:
                    evaluated.append(precond_holds(pc, env))
                except Exception as exc:  # noqa: BLE001
                    failures.append(f"{iid}: out-of-region check could not evaluate precondition {precond_string(pc)!r} at witness {cx}: {exc}")
                    evaluated.append(None)
            if evaluated and all(v is True for v in evaluated):
                failures.append(f"{iid}: out-of-region witness {cx} satisfies ALL preconditions (should leave the region)")
    return checked


def precond_string(pc: dict) -> str:
    sym = {"gt": ">", "gte": ">=", "lt": "<", "lte": "<=", "eq": "=="}[pc["op"]]
    rhs = pc["rhs"]
    if "const" in rhs:
        rv = repr(float(rhs["const"]))
    elif "input" in rhs:
        rv = str(rhs["input"])
    else:
        rv = rhs["expr"]
    return f"{pc['lhs']} {sym} {rv}"


# ----------------------------------------------------------------------------
# Lints.
# ----------------------------------------------------------------------------
def name_lint(failures: list[str]) -> None:
    for d in ("src", "properties", "demos", "sampled"):
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


def collision_lint(failures: list[str]) -> None:
    """No sampled/ property name collides with a properties/ green (contract)."""
    def names(d: str) -> set[str]:
        s: set[str] = set()
        for ch in (REPO_ROOT / d).glob("*.ch"):
            s |= set(re.findall(r'@property\s+([A-Za-z_]\w*)', ch.read_text()))
        return s
    for n in sorted(names("properties") & names("sampled")):
        failures.append(f"sampled/ property {n} collides with a properties/ green (name must be distinct)")


# ----------------------------------------------------------------------------
# Honesty self-test (runs first).
# ----------------------------------------------------------------------------
def honesty_self_test() -> None:
    def rec(tier, quals, status="passed", assumptions=None):
        return {"status": status, "proof_tier": tier, "samples": 0 if tier == "smt" else 500,
                "arith_model": "real", "qualifiers": quals, "assumptions": assumptions or []}

    assert classify_tier(rec("smt", ["real_arithmetic"])) == "proven"
    assert classify_tier(rec("smt", ["real_arithmetic", "fuzz"])) == "proven_modulo_contract"
    assert classify_tier(rec("fuzz", ["fuzz", "fuzz_base"])) == "fuzz_validated"
    assert classify_tier(rec("fuzz", [], status="failed")) == "disproved"
    ok, _ = green_property(rec("fuzz", ["fuzz"]))
    assert not ok, "green_property accepted a fuzz-tier record"
    ok, _ = green_property(rec("smt", ["real_arithmetic", "fuzz"]))
    assert not ok, "green_property accepted a contract-qualified record"
    ok, _ = green_property(rec("smt", ["real_arithmetic"]))
    assert ok, "green_property rejected a clean unqualified green"
    masked = rec("fuzz", ["fuzz"])
    masked["composite_verdict"] = "proven_modulo_real_arithmetic"
    assert classify_tier(masked) == "fuzz_validated", "composite_verdict must not promote a fuzz record"


# ----------------------------------------------------------------------------
# Metamorphic anti-vacuity: a properties/ green must DEPEND on the model.
# ----------------------------------------------------------------------------
# The goal-string reference check ("the goal calls the output fn") is syntactic
# and forgeable: a canceling call `F(x) - F(x) < c` or a reflexive `F(x) == F(x)`
# references F textually but is true for ANY F, so it stays proven even against a
# deliberately broken model body -- the exact surface a red-team defeated
# engine-side. This check is semantic: re-prove the SAME goal with F's body
# replaced by DISTINCT alternative bodies and require the verdict to CHANGE
# (proven -> disproved) under at least one substitution. A goal whose truth is
# model-independent survives every substitution, so the gate rejects it.


def _src_file_of(fn: str, pkg_dir: Path) -> Path | None:
    for ch in sorted((pkg_dir / "src").glob("*.ch")):
        if re.search(rf'^\s*def\s+{re.escape(fn)}\s*\(', ch.read_text(), re.M):
            return ch
    return None


def _fn_params(src_text: str, fn: str) -> list[str]:
    m = re.search(rf'def\s+{re.escape(fn)}\s*\(([^)]*)\)', src_text)
    return [p.split(":")[0].strip() for p in m.group(1).split(",") if p.strip()] if m else []


def _alt_bodies(params: list[str]) -> list[str]:
    """Distinct well-typed f32 bodies over the fn's own params. A model-dependent
    goal changes verdict under at least one; a canceling/reflexive goal under none."""
    p0 = params[0]
    if len(params) >= 2:
        p1 = params[1]
        return [f"(0.0 - {p0})", f"({p0} + {p1})", f"({p0} - {p1})"]
    return [f"(0.0 - {p0})", f"({p0} + {p0})", f"({p0} * {p0})"]


def _substitute_body(src_text: str, fn: str, new_body: str) -> str:
    pat = re.compile(rf'^(\s*def\s+{re.escape(fn)}\s*\([^)]*\)\s*->\s*[^=]+=\s*).*$', re.M)
    return pat.sub(lambda m: m.group(1) + new_body, src_text, count=1)


def _copy_package(pkg_dir: Path, dst: Path) -> None:
    shutil.copy(pkg_dir / "reef.toml", dst / "reef.toml")
    for d in ("src", "properties", "demos", "sampled", "tests"):
        s = pkg_dir / d
        if s.is_dir():
            shutil.copytree(s, dst / d)


_meta_cache: dict[tuple, dict[str, dict]] = {}


def _reprove_substituted(binary: str, pkg_dir: Path, fn: str, alt_body: str,
                         prop_file_rel: str) -> dict[str, dict]:
    """Copy the package, replace fn's body with alt_body in its src file, and
    re-prove prop_file_rel; return {property_name: record}. Cached per (fn, alt,
    file) since several invariants share an output fn and property file."""
    key = (str(pkg_dir), fn, alt_body, prop_file_rel)
    if key in _meta_cache:
        return _meta_cache[key]
    src_file = _src_file_of(fn, pkg_dir)
    result: dict[str, dict] = {}
    if src_file is not None:
        src_rel = src_file.relative_to(pkg_dir)
        with tempfile.TemporaryDirectory(prefix="econ-meta-") as tmp:
            tmpd = Path(tmp)
            _copy_package(pkg_dir, tmpd)
            target = tmpd / src_rel
            target.write_text(_substitute_body(target.read_text(), fn, alt_body))
            result = run_prove(binary, tmpd / prop_file_rel, "smt-only", smt_timeout=20000, cwd=tmpd)
    _meta_cache[key] = result
    return result


def metamorphic_flips(binary: str, pkg_dir: Path, fn: str, prop_file_rel: str,
                      prop_name: str) -> tuple[bool, str]:
    """True if SOME distinct substitution of fn's body flips prop_name from proven
    to disproved -- the goal's truth genuinely depends on fn."""
    src_file = _src_file_of(fn, pkg_dir)
    if src_file is None:
        return False, f"output fn {fn} not found in {pkg_dir}/src"
    params = _fn_params(src_file.read_text(), fn)
    if not params:
        return False, f"could not parse params of {fn}"
    tried = []
    for alt in _alt_bodies(params):
        rec = _reprove_substituted(binary, pkg_dir, fn, alt, prop_file_rel).get(prop_name)
        status = rec.get("status") if rec else "no-record"
        tried.append(f"{fn}:={alt} -> {status}")
        if status == "failed":  # disproved for the alternative model: genuine dependence
            return True, f"flips under {fn}:={alt}"
    return False, f"NO substitution flipped {prop_name} (model-independent): {tried}"


def gate_metamorphic(binary: str, manifest: dict, records: dict[str, dict],
                     pin: str, failures: list[str]) -> int:
    """Run the metamorphic anti-vacuity check on every properties/ proven,
    direct-call invariant."""
    output_fns = {m["output_fn"] for m in manifest.get("models", [])}
    checked = 0
    for inv in manifest.get("invariants", []):
        if inv.get("expected_tier_per_pin", {}).get(pin) != "proven":
            continue
        if inv.get("binding", {}).get("references_output_fn") != "direct":
            continue
        prop = inv.get("property", {})
        prop_file, prop_name = prop.get("file", ""), prop.get("name")
        if not prop_file.startswith("properties/"):
            continue
        sat = records.get(inv["controls"]["satisfying"]["name"])
        if sat is None:
            continue
        goal = re.sub(r"\s+", "", sat.get("goal", ""))
        matched = sorted((fn for fn in output_fns if f"{fn}(" in goal), key=len, reverse=True)
        if not matched:
            continue  # the goal-string check already flagged a goal that calls no output fn
        checked += 1
        ok, detail = metamorphic_flips(binary, REPO_ROOT, matched[0], prop_file, prop_name)
        if not ok:
            failures.append(f"{inv['id']}: metamorphic anti-vacuity -- {detail}; a green that survives every model substitution is vacuous")
    return checked


# ----------------------------------------------------------------------------
def main() -> int:
    failures: list[str] = []
    try:
        honesty_self_test()
    except AssertionError as e:
        print(f"prove_gate FAILED (honesty self-test): {e}")
        return 1

    binary = resolve_bin()
    manifest = json.loads(MANIFEST.read_text())
    pin = manifest["chelis_pin"]
    assert_version(binary, pin)
    print(f"prove_gate using {binary} (manifest {manifest['schema_id']}/{manifest['schema_version']}, pin {pin})")

    all_records: dict[str, dict] = {}

    for d in ("src", "properties"):
        for ch in sorted((REPO_ROOT / d).glob("*.ch")):
            recs = run_prove(binary, ch, "smt-only", smt_timeout=20000)
            gate_proven_file(recs, ch, failures)
            all_records.update({k: v for k, v in recs.items() if k != "__errors__"})

    for ch in sorted((REPO_ROOT / "demos").glob("*.ch")):
        recs = run_prove(binary, ch, "smt-only", smt_timeout=15000)
        gate_proven_file(recs, ch, failures)
        all_records.update({k: v for k, v in recs.items() if k != "__errors__"})

    # sampled: proven STANDALONE in a scratch dir outside the repo. Package
    # auto-detection changes prove semantics: an in-package grad goal hangs even
    # with the body inlined (no imports) -- standalone returns in ~5s, in-package
    # does not return (docs/issue_drafts/grad_inpackage_hang.md; distinct from the
    # grad-through-import hang). auto tier so the grad goals degrade to fuzz.
    with tempfile.TemporaryDirectory(prefix="econ-sampled-") as tmp:
        for ch in sorted((REPO_ROOT / "sampled").glob("*.ch")):
            dst = Path(tmp) / ch.name
            shutil.copy(ch, dst)
            recs = run_prove(binary, dst, "auto", samples=500, cwd=Path(tmp))
            gate_sampled_file(recs, ch, failures)
            all_records.update({k: v for k, v in recs.items() if k != "__errors__"})

    checked = gate_manifest(binary, manifest, all_records, pin, failures)
    meta_checked = gate_metamorphic(binary, manifest, all_records, pin, failures)

    name_lint(failures)
    doc_lint(failures)
    collision_lint(failures)

    if failures:
        print(f"\nprove_gate FAILED with {len(failures)} finding(s):")
        for f in failures:
            print(f"  FAIL {f}")
        return 1
    print(f"prove_gate OK: {checked} manifest invariants match their expected tier and break with in-domain "
          f"witnesses; {meta_checked} properties/ greens pass the metamorphic anti-vacuity check (verdict flips "
          f"under a model substitution); every properties/ green is an unqualified SMT green; sampled/ greens are "
          f"honest fuzz amber; witnesses/twins/controls behave; name, doc, and collision lints clean.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
