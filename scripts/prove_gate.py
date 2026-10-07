#!/usr/bin/env python3
"""Check Economoist's manifest against the pinned compiler.

Positive properties in `properties/` must prove by SMT over the reals without
samples or contract qualifiers; their guard-satisfiability and wrong-claim
controls must refute. The positive f32 AD check in `sampled/` is fuzz-validated
and its wrong-sign control must refute. The gate reads
docs/cnote-import-surface.json (chelis-shell.invariant-surface/1.0) and runs
the pinned release binary.

Per the contract, an achieved tier is classified from `proof_tier` + assumption
discharge methods + `qualifiers`, NEVER from the `composite_verdict` string (a
verdict token may demote a result, never promote it). For each manifest invariant
the gate checks:

  1. satisfying control holds, classified tier == expected_tier_per_pin[pin]
     (drift in either direction fails); assumptions' non_vacuity established;
     the property
     references the shipped output fn through the complete linker-owned
     `dependency_graph`; an unavailable graph fails closed;
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

from copy import deepcopy
from dataclasses import dataclass
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from fractions import Fraction
from pathlib import Path

try:
    from .oracle_harness import scalar_value
except ImportError:
    from oracle_harness import scalar_value

REPO_ROOT = Path(__file__).resolve().parents[1]
MANIFEST = REPO_ROOT / "docs" / "cnote-import-surface.json"

FORBIDDEN_NAME = re.compile(r"(converge|stationary|fixed_point|ergodic|limit|iterat)", re.I)
DECL_NAME = re.compile(r"^\s*(?:@property|def|type)\s+([A-Za-z_][A-Za-z0-9_]*)")
UNIVERSAL_CLAIM = re.compile(r"(for all n|general[- ]n|any dimension|all dimensions|universal theorem)", re.I)
HELD_OUT = re.compile(r"held[- ]out", re.I)


# ----------------------------------------------------------------------------
# Binary resolution (env-first -> reef.toml-pinned release install -> PATH).
# ----------------------------------------------------------------------------
def resolve_bin() -> str:
    # Env precedence is CHELIS_BIN then CHELIS_SMT_BIN, uniform across the
    # package scripts.
    for env in ("CHELIS_BIN", "CHELIS_SMT_BIN"):
        v = os.environ.get(env)
        if v and (Path(v).expanduser().is_file() or _on_path(v)):
            return str(Path(v).expanduser())
    m = re.search(r'compiler\s*=\s*"=([^"]+)"', (REPO_ROOT / "reef.toml").read_text())
    if m:
        cand = Path.home() / ".chelis" / "toolchains" / m.group(1) / "bin" / "chelis"
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


def _graph_text(value: object, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} must be a nonempty string")
    return value


def _graph_span_integer(value: object, field: str) -> int:
    if type(value) is not int or value < 0:
        raise ValueError(f"{field} must be a nonnegative integer")
    return value


@dataclass(frozen=True)
class GraphDeclaration:
    id: str
    name: str
    kind: str
    package: str
    module: str
    source_file: str
    span_offset: int
    span_len: int

    @property
    def semantic_key(self) -> tuple[str, str, str, str]:
        return self.package, self.module, self.kind, self.name

    @classmethod
    def from_wire(cls, node: object) -> "GraphDeclaration":
        if not isinstance(node, dict):
            raise ValueError("declaration must be an object")
        fields = {
            field: _graph_text(node.get(field), f"declaration.{field}")
            for field in ("id", "name", "kind", "package", "module")
        }
        source = node.get("source")
        if not isinstance(source, dict):
            raise ValueError("declaration.source must be an object")
        source_file = _graph_text(source.get("file"), "declaration.source.file")
        if (
            source_file.startswith("/")
            or "\\" in source_file
            or any(part in ("", ".", "..") for part in source_file.split("/"))
        ):
            raise ValueError("declaration.source.file must be a package-relative path")
        span = source.get("span")
        if not isinstance(span, dict):
            raise ValueError("declaration.source.span must be an object")
        return cls(
            **fields,
            source_file=source_file,
            span_offset=_graph_span_integer(
                span.get("offset"), "declaration.source.span.offset"
            ),
            span_len=_graph_span_integer(span.get("len"), "declaration.source.span.len"),
        )


@dataclass(frozen=True)
class ValidatedDependencyGraph:
    by_semantic_key: dict[tuple[str, str, str, str], GraphDeclaration]
    edges: frozenset[tuple[str, str]]

    @classmethod
    def from_wire(cls, wire: object) -> "ValidatedDependencyGraph":
        if not isinstance(wire, dict) or wire.get("status") != "complete":
            raise ValueError("complete compiler dependency graph is required")
        declarations = wire.get("declarations")
        edges = wire.get("edges")
        if not isinstance(declarations, list) or not isinstance(edges, list):
            raise ValueError("complete graph requires declarations/edges arrays")

        by_id: dict[str, GraphDeclaration] = {}
        by_key: dict[tuple[str, str, str, str], GraphDeclaration] = {}
        for raw_node in declarations:
            node = GraphDeclaration.from_wire(raw_node)
            if node.id in by_id:
                raise ValueError(f"duplicate declaration ID {node.id!r}")
            if node.semantic_key in by_key:
                raise ValueError(f"duplicate declaration identity {node.semantic_key!r}")
            by_id[node.id] = node
            by_key[node.semantic_key] = node

        validated_edges: set[tuple[str, str]] = set()
        for raw_edge in edges:
            if not isinstance(raw_edge, dict):
                raise ValueError("edge must be an object")
            source_id = _graph_text(raw_edge.get("from"), "edge.from")
            target_id = _graph_text(raw_edge.get("to"), "edge.to")
            if source_id not in by_id or target_id not in by_id:
                raise ValueError("edge endpoint lacks a declaration")
            validated_edges.add((source_id, target_id))
        return cls(by_semantic_key=by_key, edges=frozenset(validated_edges))


def compiler_graph_directly_references(
    record: dict,
    *,
    property_name: str,
    property_module: str,
    property_file: str,
    output_fn: str,
    output_module: str,
    package: str,
) -> tuple[bool, str]:
    """Require an exact property-to-export edge after validating the whole graph."""
    try:
        graph = ValidatedDependencyGraph.from_wire(record.get("_dependency_graph"))
    except ValueError as exc:
        return False, f"invalid compiler dependency graph: {exc}"

    property_node = graph.by_semantic_key.get(
        (package, property_module, "property", property_name)
    )
    if property_node is None or property_node.source_file != property_file:
        return (
            False,
            "compiler dependency graph has no exact property declaration for "
            f"{package}:{property_module}:{property_file}:{property_name}",
        )
    output_node = graph.by_semantic_key.get(
        (package, output_module, "function", output_fn)
    )
    if output_node is None:
        return (
            False,
            "compiler dependency graph has no exact model declaration for "
            f"{package}:{output_module}:{output_fn}",
        )
    if (property_node.id, output_node.id) in graph.edges:
        return True, "linker-owned direct dependency edge present"
    return False, "compiler dependency graph has no direct property -> output-function edge"


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


def f32_reexec_positive_break(binary: str, model: dict, cx: dict) -> tuple[bool, str]:
    """Import and evaluate the shipped output function at an f32 witness."""
    fn = model["output_fn"]
    args: list[str] = []
    for param in model.get("params", []):
        p = param["name"]
        if p not in cx:
            return False, f"witness has no value for parameter {p}"
        args.append(f"cast({float(_val(str(cx[p])))!r}, f32)")
    source = f'import {model["module"]} ({fn})\n\nbreak_value = {fn}({", ".join(args)})\n'
    path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".ch", prefix="economoist_break_", dir=REPO_ROOT,
            encoding="utf-8", delete=False,
        ) as handle:
            handle.write(source)
            path = Path(handle.name)
        formatted = subprocess.run(
            [binary, "fmt", "--inplace", str(path)], capture_output=True, text=True,
        )
        if formatted.returncode != 0:
            return False, f"could not format f32 re-execution probe: {formatted.stderr.strip()[:120]}"
        proc = subprocess.run(
            [binary, "eval", "--file", str(path), "--json"], cwd=REPO_ROOT,
            capture_output=True, text=True,
        )
        if proc.returncode != 0:
            return False, f"eval --file failed: {proc.stderr.strip()[:120]}"
        value = scalar_value(json.loads(proc.stdout)["roots"][0]["value"]["value"])
    except Exception as exc:  # noqa: BLE001
        return False, f"could not parse eval output ({exc})"
    finally:
        if path is not None:
            path.unlink(missing_ok=True)
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
            failures.append(f"{iid}: result drift -- {sat_name} classified {got!r}, manifest expects {expected!r}; review the changed result")
        if sat.get("status") != "passed":
            failures.append(f"{iid}: satisfying control {sat_name} did not pass: {sat.get('status')}")
        # Anti-vacuity: direct bindings require a complete linker-owned
        # declaration graph. No source or goal-string fallback is accepted.
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
            binding_ok, binding_detail = compiler_graph_directly_references(
                sat,
                property_name=sat_name,
                property_module=sat_origin.get("module", ""),
                property_file=sat_origin.get("file", ""),
                output_fn=model["output_fn"],
                output_module=model["module"],
                package=manifest.get("pkg", ""),
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
                violating_ok, violating_detail = compiler_graph_directly_references(
                    viol,
                    property_name=viol_name,
                    property_module=viol_origin.get("module", ""),
                    property_file=viol_origin.get("file", ""),
                    output_fn=violating_model["output_fn"],
                    output_module=violating_model["module"],
                    package=manifest.get("pkg", ""),
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
                ok, why = f32_reexec_positive_break(binary, model, cx)
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
    book = REPO_ROOT / "docs" / "book" / "src"
    for md in sorted(book.rglob("*.md")) if book.exists() else []:
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
                    "source": {
                        "file": "sampled/growth_sensitivity.ch",
                        "span": {"offset": 10, "len": 80},
                    },
                },
                {
                    "id": "f",
                    "kind": "function",
                    "name": "gordon_pv",
                    "module": "Economoist.Growth",
                    "package": "economoist",
                    "source": {
                        "file": "src/growth.ch",
                        "span": {"offset": 20, "len": 40},
                    },
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
    graph = graph_record["_dependency_graph"]
    duplicate_property = deepcopy(graph)
    duplicate_property["edges"] = []
    decoy = deepcopy(graph["declarations"][0])
    decoy["id"] = "decl:forged-other-property"
    decoy["source"]["span"] = {"offset": 999999, "len": 1}
    duplicate_property["declarations"].append(decoy)
    duplicate_property["edges"].append({"from": decoy["id"], "to": "f"})
    assert {"from": "p", "to": "f"} not in duplicate_property["edges"]
    ok, detail = compiler_graph_directly_references(
        {"_dependency_graph": duplicate_property}, **exact
    )
    assert not ok and "duplicate declaration identity" in detail, (
        "duplicate semantic property and decoy edge forged a direct dependency"
    )
    for removed_path in (("source",), ("source", "span")):
        missing_function_source = deepcopy(graph)
        field = missing_function_source["declarations"][1]
        for part in removed_path[:-1]:
            field = field[part]
        del field[removed_path[-1]]
        ok, detail = compiler_graph_directly_references(
            {"_dependency_graph": missing_function_source}, **exact
        )
        assert not ok and "declaration.source" in detail, (
            f"function declaration missing {removed_path} forged a binding"
        )
    missing_identity = {
        "_dependency_graph": {
            "status": "complete",
            "declarations": [
                {key: value for key, value in node.items() if key != "id"}
                for node in graph_record["_dependency_graph"]["declarations"]
            ],
            "edges": [{}],
        }
    }
    ok, _ = compiler_graph_directly_references(missing_identity, **exact)
    assert not ok, "missing declaration IDs and edge endpoints forged a direct dependency"
    missing_endpoints = {
        "_dependency_graph": {
            **graph_record["_dependency_graph"],
            "edges": [{}],
        }
    }
    ok, _ = compiler_graph_directly_references(missing_endpoints, **exact)
    assert not ok, "missing edge endpoints passed with valid declaration IDs"
    no_edge = deepcopy(graph)
    no_edge["edges"] = []
    ok, _ = compiler_graph_directly_references({"_dependency_graph": no_edge}, **exact)
    assert ok is False, "complete graph without a direct edge did not fail closed"
    assert ValidatedDependencyGraph.from_wire(
        {"status": "complete", "declarations": [], "edges": []}
    ).by_semantic_key == {}, "complete empty graph was treated as a malformed wire"
    unavailable = {
        "goal": "(gordon_pv(d, r, g) > 0.0)",
        "_dependency_graph": {"status": "unavailable"},
    }
    ok, _ = compiler_graph_directly_references(unavailable, **exact)
    assert ok is False, "goal text promoted a record without a complete graph"
    ok, _ = compiler_graph_directly_references({}, **exact)
    assert ok is False, "missing compiler graph passed direct attribution"
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
                    "source": {
                        "file": "src/markov.ch",
                        "span": {"offset": 5, "len": 30},
                    },
                },
            ],
            "edges": [{"from": "p", "to": "m"}],
        },
    }
    ok, detail = compiler_graph_directly_references(wrong_model, **exact)
    assert not ok and "no direct property" in detail, (
        "direct binding accepted an edge to the wrong shipped model"
    )
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
                    "source": {
                        "file": "sampled/attacker.ch",
                        "span": {"offset": 10, "len": 80},
                    },
                },
                graph_record["_dependency_graph"]["declarations"][1],
            ],
            "edges": [{"from": "p", "to": "f"}],
        }
    }
    ok, detail = compiler_graph_directly_references(decoy_property, **exact)
    assert not ok and "no exact property" in detail, (
        "direct binding accepted a same-name property from a decoy module"
    )
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
                    "source": {
                        "file": "src/attacker.ch",
                        "span": {"offset": 20, "len": 40},
                    },
                },
            ],
            "edges": [{"from": "p", "to": "attacker"}],
        }
    }
    ok, detail = compiler_graph_directly_references(decoy_function, **exact)
    assert not ok and "no direct property" in detail, (
        "direct binding accepted a same-name function from a decoy module"
    )

    # These wires retain the genuine direct edge. Every malformed declaration
    # and edge must be rejected before that edge can serve as provenance.
    malformed_wires: list[tuple[str, dict, str]] = []
    duplicate_id = deepcopy(graph)
    unrelated = deepcopy(graph["declarations"][0])
    unrelated["name"] = "other_property"
    duplicate_id["declarations"].append(deepcopy(unrelated))
    malformed_wires.append(("duplicate ID", duplicate_id, "duplicate declaration ID"))

    duplicate_other_key = deepcopy(graph)
    unrelated["id"] = "other"
    duplicate_other_key["declarations"].append(deepcopy(unrelated))
    other_duplicate = deepcopy(unrelated)
    other_duplicate["id"] = "other_again"
    duplicate_other_key["declarations"].append(other_duplicate)
    malformed_wires.append(
        ("duplicate unrelated semantic key", duplicate_other_key, "duplicate declaration identity")
    )

    missing_unrelated_span = deepcopy(graph)
    unrelated["id"] = "other"
    unrelated.pop("source")
    missing_unrelated_span["declarations"].append(unrelated)
    malformed_wires.append(
        ("missing unrelated source", missing_unrelated_span, "declaration.source")
    )

    invalid_name = deepcopy(graph)
    invalid_name["declarations"][1]["name"] = None
    malformed_wires.append(("non-string name", invalid_name, "declaration.name"))
    invalid_file = deepcopy(graph)
    invalid_file["declarations"][1]["source"]["file"] = "../growth.ch"
    malformed_wires.append(("non-relative source file", invalid_file, "package-relative path"))
    invalid_span = deepcopy(graph)
    invalid_span["declarations"][1]["source"]["span"]["offset"] = True
    malformed_wires.append(("boolean span offset", invalid_span, "span.offset"))
    negative_span = deepcopy(graph)
    negative_span["declarations"][1]["source"]["span"]["len"] = -1
    malformed_wires.append(("negative span length", negative_span, "span.len"))
    malformed_edge = deepcopy(graph)
    malformed_edge["edges"].append([])
    malformed_wires.append(("non-object edge", malformed_edge, "edge must be an object"))
    dangling_edge = deepcopy(graph)
    dangling_edge["edges"].append({"from": "p", "to": "missing"})
    malformed_wires.append(("dangling endpoint", dangling_edge, "edge endpoint"))

    for label, wire, reason in malformed_wires:
        ok, detail = compiler_graph_directly_references(
            {"_dependency_graph": wire}, **exact
        )
        assert not ok and reason in detail, f"{label} wire accepted or misclassified: {detail}"


# ----------------------------------------------------------------------------
# Metamorphic anti-vacuity: a properties/ green must DEPEND on the model.
# ----------------------------------------------------------------------------
# A dependency edge alone does not prove the goal depends on the model's
# behavior: a canceling call `F(x) - F(x) < c` or a reflexive `F(x) == F(x)`
# calls F but is true for ANY F, so it stays proven even against a
# deliberately broken model body. This check is semantic: re-prove the SAME goal with F's body
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
    return [f"{p0}", f"(0.0 - {p0})", "1.0f32"]


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
    # shipped model directly. Import and package-context behavior are part of
    # this acceptance surface.
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
    print(f"prove_gate OK: {checked} manifest invariants match their expected results and "
          f"violating controls refute; {meta_checked} positive properties change verdict "
          f"under model substitution; positive properties have unqualified SMT results, "
          f"sampled f32 AD is fuzz-validated, and source lints pass.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
