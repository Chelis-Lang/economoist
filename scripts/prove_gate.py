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
     references the shipped output fn. From Chelis 0.17.2 onward chelis#922's
     linker-owned `dependency_graph` is mandatory and authoritative; the
     prover-emitted goal remains a compatibility oracle only at older pins;
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
    dependency_graph: dict | None = None
    for line in proc.stdout.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            r = json.loads(line)
        except json.JSONDecodeError:
            continue
        if r.get("kind") in ("property", "obligation"):
            collect_prover_record(records, r)
        elif r.get("kind") == "error":
            records.setdefault("__errors__", {"reasons": []})["reasons"].append(r.get("reason"))
        elif r.get("kind") == "summary":
            graph = r.get("dependency_graph")
            if isinstance(graph, dict):
                dependency_graph = graph
    if dependency_graph is not None:
        for record in records.values():
            if record.get("kind") in ("property", "obligation"):
                record["_dependency_graph"] = dependency_graph
    if proc.returncode not in (0, 1, 2, 3) and not records:
        sys.stderr.write(proc.stdout + proc.stderr)
    return records


def collect_prover_record(records: dict[str, dict], record: dict) -> None:
    """Collect one proof record without allowing ambiguous last-write-wins."""
    name = record.get("name", "")
    if name in records:
        records.setdefault("__errors__", {"reasons": []})["reasons"].append(
            f"duplicate prover record name {name!r} in one compiler invocation"
        )
        return
    records[name] = record


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


def compiler_graph_directly_references(
    record: dict,
    *,
    property_name: str,
    property_module: str,
    property_file: str,
    output_fn: str,
    output_module: str,
    package: str,
) -> tuple[bool | None, str]:
    """Check a direct model binding against chelis#922's linker-owned graph.

    `None` means the current compiler did not provide a complete graph and the
    caller must use the compatibility oracle. Once a complete graph is present,
    missing nodes or edges fail closed rather than silently falling back to
    source/goal reconstruction.
    """
    graph = record.get("_dependency_graph")
    if not isinstance(graph, dict) or graph.get("status") != "complete":
        return None, "compiler dependency graph unavailable at this pin"

    declarations = graph.get("declarations")
    edges = graph.get("edges")
    if not isinstance(declarations, list) or not isinstance(edges, list):
        return False, "complete compiler dependency graph lacks declarations/edges arrays"

    property_ids = {
        node.get("id")
        for node in declarations
        if isinstance(node, dict)
        and node.get("kind") == "property"
        and node.get("name") == property_name
        and node.get("module") == property_module
        and node.get("package") == package
        and isinstance(node.get("source"), dict)
        and node["source"].get("file") == property_file
    }
    output_ids = {
        node.get("id")
        for node in declarations
        if isinstance(node, dict)
        and node.get("kind") == "function"
        and node.get("name") == output_fn
        and node.get("module") == output_module
        and node.get("package") == package
    }
    if not property_ids:
        return (
            False,
            "compiler dependency graph has no exact property declaration for "
            f"{package}:{property_module}:{property_file}:{property_name}",
        )
    if not output_ids:
        return (
            False,
            "compiler dependency graph has no exact model declaration for "
            f"{package}:{output_module}:{output_fn}",
        )
    if any(
        edge.get("from") in property_ids and edge.get("to") in output_ids
        for edge in edges
        if isinstance(edge, dict)
    ):
        return True, "linker-owned direct dependency edge present"
    return False, "compiler dependency graph has no direct property -> output-function edge"


def direct_binding_references(
    record: dict,
    *,
    property_name: str,
    property_module: str,
    property_file: str,
    output_fn: str,
    output_module: str,
    package: str,
    pin: str,
) -> tuple[bool, str]:
    """Require compiler-owned attribution at pins that promise chelis#922."""
    graph_ok, graph_detail = compiler_graph_directly_references(
        record,
        property_name=property_name,
        property_module=property_module,
        property_file=property_file,
        output_fn=output_fn,
        output_module=output_module,
        package=package,
    )
    if graph_ok is not None:
        return graph_ok, graph_detail

    match = re.fullmatch(r"(\d+)\.(\d+)\.(\d+)", pin)
    if match is None:
        return False, f"cannot determine dependency-graph contract for pin {pin!r}"
    version = tuple(int(part) for part in match.groups())
    if version >= (0, 17, 2):
        return (
            False,
            f"compiler dependency graph is required at pin {pin}, but unavailable",
        )

    goal = re.sub(r"\s+", "", record.get("goal", ""))
    if f"{output_fn}(" in goal:
        return True, "legacy compiler-emitted goal references shipped output function"
    return (
        False,
        f"satisfying control {property_name} goal references no shipped output fn "
        "(legacy compatibility vacuity tell)",
    )


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
    models_by_id = {m["id"]: m for m in manifest.get("models", [])}
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
        # Anti-vacuity. For `direct`, chelis#922's complete linker-owned graph is
        # mandatory from 0.17.2 onward. Only older pins fall back to the
        # compiler-emitted goal string; ownership is never reconstructed from
        # source.
        # `equivalent-form` deliberately inlines a shipped body and therefore
        # requires a narrowing citation plus its corrupt-flip control.
        binding = inv.get("binding", {})
        ref_mode = binding.get("references_output_fn")
        if ref_mode == "equivalent-form":
            if not binding.get("equivalent_form_citation"):
                failures.append(f"{iid}: references_output_fn 'equivalent-form' but no equivalent_form_citation")
        else:
            model = models_by_id.get(inv.get("anchor_model"))
            if model is None:
                failures.append(
                    f"{iid}: anchor_model {inv.get('anchor_model')!r} does not resolve"
                )
                continue
            sat_origin = sat.get("_origin", {})
            binding_ok, binding_detail = direct_binding_references(
                sat,
                property_name=sat_name,
                property_module=sat_origin.get("module", ""),
                property_file=sat_origin.get("file", ""),
                output_fn=model["output_fn"],
                output_module=model["module"],
                package=manifest.get("pkg", ""),
                pin=pin,
            )
            if not binding_ok:
                failures.append(f"{iid}: {binding_detail}")
            violating_model_id = inv.get("defective_model") or inv.get(
                "anchor_model"
            )
            violating_model = models_by_id.get(violating_model_id)
            if violating_model is None:
                failures.append(
                    f"{iid}: violating model {violating_model_id!r} does not resolve"
                )
            else:
                viol_origin = viol.get("_origin", {})
                violating_ok, violating_detail = direct_binding_references(
                    viol,
                    property_name=viol_name,
                    property_module=viol_origin.get("module", ""),
                    property_file=viol_origin.get("file", ""),
                    output_fn=violating_model["output_fn"],
                    output_module=violating_model["module"],
                    package=manifest.get("pkg", ""),
                    pin=pin,
                )
                if not violating_ok:
                    failures.append(
                        f"{iid}: violating control attribution: {violating_detail}"
                    )
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
    duplicate_records: dict[str, dict] = {}
    collect_prover_record(
        duplicate_records, {"kind": "property", "name": "duplicate", "status": "passed"}
    )
    collect_prover_record(
        duplicate_records, {"kind": "property", "name": "duplicate", "status": "failed"}
    )
    assert duplicate_records["duplicate"]["status"] == "passed"
    assert duplicate_records["__errors__"]["reasons"] == [
        "duplicate prover record name 'duplicate' in one compiler invocation"
    ], "same-invocation duplicate proof records did not fail closed"
    ok, _ = green_property(rec("fuzz", ["fuzz"]))
    assert not ok, "green_property accepted a fuzz-tier record"
    ok, _ = green_property(rec("smt", ["real_arithmetic", "fuzz"]))
    assert not ok, "green_property accepted a contract-qualified record"
    ok, _ = green_property(rec("smt", ["real_arithmetic"]))
    assert ok, "green_property rejected a clean unqualified green"
    masked = rec("fuzz", ["fuzz"])
    masked["composite_verdict"] = "proven_modulo_real_arithmetic"
    assert classify_tier(masked) == "fuzz_validated", "composite_verdict must not promote a fuzz record"
    graph_record = {
        "_dependency_graph": {
            "status": "complete",
            "declarations": [
                {
                    "id": "p",
                    "kind": "property",
                    "name": "sensitivity",
                    "module": "Economoist.Sampled.Growth_sensitivity",
                    "package": "economoist",
                    "source": {"file": "sampled/growth_sensitivity.ch"},
                },
                {
                    "id": "f",
                    "kind": "function",
                    "name": "gordon_pv",
                    "module": "Economoist.Growth",
                    "package": "economoist",
                },
            ],
            "edges": [{"from": "p", "to": "f"}],
        }
    }
    exact = {
        "property_name": "sensitivity",
        "property_module": "Economoist.Sampled.Growth_sensitivity",
        "property_file": "sampled/growth_sensitivity.ch",
        "output_fn": "gordon_pv",
        "output_module": "Economoist.Growth",
        "package": "economoist",
    }
    ok, _ = compiler_graph_directly_references(graph_record, **exact)
    assert ok is True, "linker-owned direct edge was rejected"
    graph_record["_dependency_graph"]["edges"] = []
    ok, _ = compiler_graph_directly_references(graph_record, **exact)
    assert ok is False, "complete graph without a direct edge did not fail closed"
    ok, _ = compiler_graph_directly_references({}, **exact)
    assert ok is None, "missing compiler graph must select the compatibility oracle"
    unavailable = {
        "goal": "(gordon_pv(d, r, g) > 0.0)",
        "_dependency_graph": {"status": "unavailable"},
    }
    ok, _ = direct_binding_references(unavailable, **exact, pin="0.17.4")
    assert not ok, "0.17.2+ direct binding accepted an unavailable compiler graph"
    ok, _ = direct_binding_references(unavailable, **exact, pin="0.17.1")
    assert ok, "pre-chelis#922 pin rejected the compiler-emitted goal oracle"
    ok, _ = direct_binding_references(unavailable, **exact, pin="not-a-version")
    assert not ok, "malformed pin bypassed the dependency-graph contract"
    wrong_model = {
        "goal": "(gordon_pv(d, r, g) > 0.0)",
        "_dependency_graph": {
            "status": "complete",
            "declarations": [
                *graph_record["_dependency_graph"]["declarations"],
                {
                    "id": "m",
                    "kind": "function",
                    "name": "next_mass",
                    "module": "Economoist.Markov",
                    "package": "economoist",
                },
            ],
            "edges": [{"from": "p", "to": "m"}],
        },
    }
    ok, _ = direct_binding_references(wrong_model, **exact, pin="0.17.4")
    assert not ok, "direct binding accepted an edge to the wrong shipped model"
    decoy_property = {
        "_dependency_graph": {
            "status": "complete",
            "declarations": [
                {
                    "id": "p",
                    "kind": "property",
                    "name": "sensitivity",
                    "module": "Attacker.Decoy",
                    "package": "economoist",
                    "source": {"file": "sampled/attacker.ch"},
                },
                graph_record["_dependency_graph"]["declarations"][1],
            ],
            "edges": [{"from": "p", "to": "f"}],
        }
    }
    ok, _ = direct_binding_references(decoy_property, **exact, pin="0.17.4")
    assert not ok, "direct binding accepted a same-name property from a decoy module"
    decoy_function = {
        "_dependency_graph": {
            "status": "complete",
            "declarations": [
                graph_record["_dependency_graph"]["declarations"][0],
                graph_record["_dependency_graph"]["declarations"][1],
                {
                    "id": "attacker",
                    "kind": "function",
                    "name": "gordon_pv",
                    "module": "Attacker.Decoy",
                    "package": "economoist",
                },
            ],
            "edges": [{"from": "p", "to": "attacker"}],
        }
    }
    ok, _ = direct_binding_references(decoy_function, **exact, pin="0.17.4")
    assert not ok, "direct binding accepted a same-name function from a decoy module"


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
    """Three distinct well-typed f32 alternative bodies: identity of the first
    param, its negation, and a distinct constant. Enough diversity that any
    genuinely F-dependent goal is disproved under at least one substitution, while
    a canceling (`F(x)-F(x)`) or reflexive (`F(x)==F(x)`) goal is disproved under
    none (it stays true, or degenerates to unsupported, for every body)."""
    p0 = params[0]
    return [f"{p0}", f"(0.0 - {p0})", "cast(1.0, f32)"]


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
    models_by_id = {m["id"]: m for m in manifest.get("models", [])}
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
        model = models_by_id.get(inv.get("anchor_model"))
        if model is None:
            continue  # contract/gate_manifest already report the unresolved model
        output_fn = model["output_fn"]
        checked += 1
        ok, detail = metamorphic_flips(
            binary, REPO_ROOT, output_fn, prop_file, prop_name
        )
        if not ok:
            failures.append(f"{inv['id']}: metamorphic anti-vacuity -- {detail}; a green that survives every model substitution is vacuous")
    return checked


# ----------------------------------------------------------------------------
def add_records(
    all_records: dict[str, dict],
    records: dict[str, dict],
    source_file: Path,
    failures: list[str],
) -> None:
    """Attach the exact compilation-unit identity to each prover record.

    Dependency edges still come exclusively from the compiler graph. The
    invocation identity selects the exact declaration within that graph and
    prevents a same-name declaration in another module from satisfying it.
    """
    source_text = source_file.read_text()
    module_match = re.search(r"^\s*module\s+(\S+)", source_text, re.M)
    module = module_match.group(1) if module_match else ""
    relative_file = str(source_file.relative_to(REPO_ROOT))
    for name, record in records.items():
        if name == "__errors__":
            continue
        if name in all_records:
            failures.append(
                f"duplicate proof record name {name!r} across canonical compilation units"
            )
            continue
        record["_origin"] = {"module": module, "file": relative_file}
        all_records[name] = record


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
            add_records(all_records, recs, ch, failures)

    for ch in sorted((REPO_ROOT / "demos").glob("*.ch")):
        recs = run_prove(binary, ch, "smt-only", smt_timeout=15000)
        gate_proven_file(recs, ch, failures)
        add_records(all_records, recs, ch, failures)

    # Sampled properties run in their real package context and may import the
    # shipped model directly. Economoist#13 established direct imported-grad
    # execution at the 0.17.1 pin; chelis#924's prepared-context work ships in
    # the pinned release. Copying source into a scratch package would discard
    # exactly the linker behavior this gate must exercise.
    for ch in sorted((REPO_ROOT / "sampled").glob("*.ch")):
        recs = run_prove(binary, ch, "fuzz-only", samples=500)
        gate_sampled_file(recs, ch, failures)
        add_records(all_records, recs, ch, failures)

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
