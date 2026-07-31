#!/usr/bin/env python3
"""Producer-side contract gate for Economoist (characterization contract v1.0).

Validates docs/cnote-import-surface.json against the frozen contract
`chelis-shell.invariant-surface/1.0` (c-note/docs/contracts/
characterization_contract_v1.md, section 3) WITHOUT running the prover -- a fast
offline job wired into ci.yml. It checks, mechanically:

  - schema_id / schema_version literals;
  - pkg_version and chelis_pin agree with reef.toml (freshness -- the exact rot
    the unconsumed v1 manifest suffered);
  - every model kind is in the frozen taxonomy; every param domain uses only the
    closed key set {gt, gte, lt, lte, rel};
  - every model output_fn is a real exported def in src/;
  - every invariant names one exact anchor_model whose output_fn it certifies;
  - every invariant.property resolves to a real @property in the named file;
  - every control (satisfying + violating) names a real @property in the canon
    files (properties/, demos/, sampled/);
  - every structured precondition appears (normalized) in the property's
    where-clause text (prove --json has no structured preconditions field);
  - expected_tier_per_pin has an entry for the current pin;
  - every below-`proven` expected tier carries a tier_upgrade_trigger citation
    (narrowing-citation rule, mechanized).

The keystone verdict/tier enforcement against the release binary lives in
scripts/prove_gate.py; this gate is the offline manifest-consistency half.

Python-stdlib-only per repo policy. Exit 0 only if every check passes.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
MANIFEST = REPO_ROOT / "docs" / "cnote-import-surface.json"

SCHEMA_ID = "chelis-shell.invariant-surface"
SCHEMA_VERSION = "1.0"

# Frozen kind taxonomy (contract section 1). Additive-only; economoist uses the
# econ.* subset.
KIND_TAXONOMY = frozenset({
    "finance.option_pricer.european_call",
    "finance.option_pricer.european_put",
    "finance.option_pricer.european_call_forward",
    "finance.lattice_pricer.european_call_fixed_depth",
    "econ.perpetuity_pv",
    "econ.dp_operator.fixed_dim",
    "econ.markov_step.fixed_dim",
})

# Frozen tier tokens (contract section 1). `proven` is the unqualified green.
TIER_TOKENS = frozenset({
    "proven", "proven_modulo_contract", "sound_approximate",
    "fuzz_validated", "disproved", "unknown", "error",
})
PROVEN_TIER = "proven"

DOMAIN_KEYS = frozenset({"gt", "gte", "lt", "lte", "rel"})
OP_SYMBOL = {"gt": ">", "gte": ">=", "lt": "<", "lte": "<=", "eq": "=="}

# Canon source dirs whose @property declarations back the manifest invariants.
CANON_DIRS = ("properties", "demos", "sampled")


def read_reef() -> tuple[str, str]:
    text = (REPO_ROOT / "reef.toml").read_text()
    ver = re.search(r'^version\s*=\s*"([^"]+)"', text, re.M)
    pin = re.search(r'compiler\s*=\s*"=([^"]+)"', text)
    if not ver or not pin:
        sys.exit("contract_gate: cannot parse version/compiler from reef.toml")
    return ver.group(1), pin.group(1)


def module_name(ch: Path) -> str | None:
    match = re.search(r"^\s*module\s+(\S+)", ch.read_text(), re.M)
    return match.group(1) if match else None


def exported_defs() -> set[tuple[str, str]]:
    """Every exact `(module, def)` pair in src/."""
    names: set[tuple[str, str]] = set()
    for ch in sorted((REPO_ROOT / "src").glob("*.ch")):
        module = module_name(ch)
        if module is None:
            continue
        for m in re.finditer(r'^\s*def\s+([A-Za-z_][A-Za-z0-9_]*)\s*\(', ch.read_text(), re.M):
            names.add((module, m.group(1)))
    return names


def property_blocks() -> tuple[dict[str, tuple[str, str]], set[str]]:
    """Map every @property NAME in the canon dirs to (relative_file, where_clause).

    The where-clause is the text between `where` and the FIRST `:` after it (the
    guards contain no `:`, while the forall param list does -- so the first colon
    after `where` is the guards/goal separator)."""
    blocks: dict[str, tuple[str, str]] = {}
    duplicates: set[str] = set()
    decl = re.compile(r'@property\s+([A-Za-z_][A-Za-z0-9_]*)\b')
    for d in CANON_DIRS:
        for ch in sorted((REPO_ROOT / d).glob("*.ch")):
            text = ch.read_text()
            rel = str(ch.relative_to(REPO_ROOT))
            starts = [(m.start(), m.group(1)) for m in decl.finditer(text)]
            for i, (pos, name) in enumerate(starts):
                end = starts[i + 1][0] if i + 1 < len(starts) else len(text)
                block = text[pos:end]
                where = ""
                wm = re.search(r'\bwhere\b', block)
                if wm:
                    after = block[wm.end():]
                    colon = after.find(":")
                    where = after[:colon] if colon != -1 else after
                if name in blocks:
                    duplicates.add(name)
                else:
                    blocks[name] = (rel, where)
    return blocks, duplicates


def _norm(s: str) -> str:
    """Strip whitespace and parentheses so a structured precondition reconstructs
    to a substring of the normalized where-clause regardless of nesting/spacing."""
    return re.sub(r'[\s()]', "", s)


def split_guards(where: str) -> list[str]:
    """Split a where-clause into its individual guards on top-level commas (guards
    are boolean scalar expressions, so a comma at paren-depth 0 separates them)."""
    out, depth, cur = [], 0, ""
    for ch in where:
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
        if ch == "," and depth == 0:
            out.append(cur)
            cur = ""
        else:
            cur += ch
    if cur.strip():
        out.append(cur)
    return [g for g in out if g.strip()]


def precond_string(pc: dict) -> str:
    op = OP_SYMBOL.get(pc["op"])
    if op is None:
        return f"<bad-op:{pc.get('op')}>"
    rhs = pc["rhs"]
    if "const" in rhs:
        rhs_s = repr(float(rhs["const"]))
    elif "input" in rhs:
        rhs_s = str(rhs["input"])
    elif "expr" in rhs:
        # A margin/relational RHS expression, written LEFT-ASSOCIATED (binary
        # nesting) to match the prover's canonical where-clause text, e.g.
        # `g + 0.01` for a guard `(r > (g + 0.01))`.
        rhs_s = rhs["expr"]
    else:
        rhs_s = "<bad-rhs>"
    return f"{pc['lhs']}{op}{rhs_s}"


def duplicate_identity_failures(manifest: dict) -> list[str]:
    failures: list[str] = []
    for key, label, consequence in (
        ("models", "model", "anchor_model identity is ambiguous"),
        ("invariants", "invariant", "consumer identity is ambiguous"),
    ):
        seen: set[str | None] = set()
        for entry in manifest.get(key, []):
            identity = entry.get("id")
            if identity in seen:
                failures.append(
                    f"duplicate {label} id {identity!r}; {consequence}"
                )
            seen.add(identity)
    return failures


def honesty_self_test() -> None:
    forged = {
        "models": [{"id": "same"}, {"id": "same"}],
        "invariants": [{"id": "same"}, {"id": "same"}],
    }
    assert duplicate_identity_failures(forged) == [
        "duplicate model id 'same'; anchor_model identity is ambiguous",
        "duplicate invariant id 'same'; consumer identity is ambiguous",
    ]


def main() -> int:
    failures: list[str] = []
    honesty_self_test()
    manifest = json.loads(MANIFEST.read_text())
    failures.extend(duplicate_identity_failures(manifest))
    reef_version, reef_pin = read_reef()

    # Schema + freshness.
    if manifest.get("schema_id") != SCHEMA_ID:
        failures.append(f"schema_id={manifest.get('schema_id')!r}, expected {SCHEMA_ID!r}")
    if manifest.get("schema_version") != SCHEMA_VERSION:
        failures.append(f"schema_version={manifest.get('schema_version')!r}, expected {SCHEMA_VERSION!r}")
    if manifest.get("pkg") != "economoist":
        failures.append(f"pkg={manifest.get('pkg')!r}, expected 'economoist'")
    if manifest.get("pkg_version") != reef_version:
        failures.append(f"pkg_version={manifest.get('pkg_version')!r} != reef.toml version {reef_version!r} (stale manifest)")
    if manifest.get("chelis_pin") != reef_pin:
        failures.append(f"chelis_pin={manifest.get('chelis_pin')!r} != reef.toml pin {reef_pin!r} (stale manifest)")

    exports = exported_defs()
    props, duplicate_props = property_blocks()
    for name in sorted(duplicate_props):
        failures.append(
            f"property {name!r} is declared in multiple canonical files; "
            "exact compiler attribution would be ambiguous"
        )

    model_ids: set[str] = set()
    models_by_id: dict[str, dict] = {}
    for m in manifest.get("models", []):
        mid = m.get("id", "<unnamed>")
        model_ids.add(mid)
        models_by_id[mid] = m
        if m.get("kind") not in KIND_TAXONOMY:
            failures.append(f"model {mid}: kind {m.get('kind')!r} not in frozen taxonomy")
        of = m.get("output_fn")
        module = m.get("module")
        if (module, of) not in exports:
            failures.append(
                f"model {mid}: exact output {module!r}:{of!r} is not an exported def in src/"
            )
        for p in m.get("params", []):
            bad = set(p.get("domain", {})) - DOMAIN_KEYS
            if bad:
                failures.append(f"model {mid} param {p.get('name')}: domain has non-contract keys {sorted(bad)}")

    if not manifest.get("invariants"):
        failures.append("no invariants in manifest")

    invariant_ids: set[str] = set()
    for inv in manifest.get("invariants", []):
        iid = inv.get("id")
        invariant_ids.add(iid)

    for inv in manifest.get("invariants", []):
        iid = inv.get("id", "<unnamed>")
        prop = inv.get("property", {})
        pname = prop.get("name")
        pfile = prop.get("file")

        # Property resolves to a real @property in the named file.
        if pname not in props:
            failures.append(f"{iid}: property {pname!r} not found as an @property in canon dirs")
        elif pfile and props[pname][0] != pfile:
            failures.append(f"{iid}: property {pname!r} is in {props[pname][0]}, manifest says {pfile}")
        elif pfile:
            source_path = REPO_ROOT / pfile
            actual_module = module_name(source_path) if source_path.is_file() else None
            if prop.get("module") != actual_module:
                failures.append(
                    f"{iid}: property module {prop.get('module')!r} != "
                    f"{pfile} module {actual_module!r}"
                )
        if pname != inv.get("controls", {}).get("satisfying", {}).get("name"):
            failures.append(
                f"{iid}: satisfying control must be the attributed property "
                f"{pname!r}"
            )

        # Controls exist.
        ctl = inv.get("controls", {})
        for role in ("satisfying", "violating"):
            cname = ctl.get(role, {}).get("name")
            if cname not in props:
                failures.append(f"{iid}: {role} control {cname!r} not found as an @property")
        viol = ctl.get("violating", {})
        if viol.get("witness_required") is not True:
            failures.append(f"{iid}: violating control must set witness_required: true")

        # kind_applies_to are real kinds.
        for k in inv.get("kind_applies_to", []):
            if k not in KIND_TAXONOMY:
                failures.append(f"{iid}: kind_applies_to {k!r} not in taxonomy")

        # Direct proof attribution is exact-model, not "some exported function."
        anchor_model = inv.get("anchor_model")
        if anchor_model not in models_by_id:
            failures.append(
                f"{iid}: anchor_model {anchor_model!r} is not a manifest model"
            )

        # Preconditions cross-check the property's where-clause -- BOTH directions.
        if pname in props:
            where_clause = props[pname][1]
            where_norm = _norm(where_clause)
            declared_norm = {_norm(precond_string(pc)) for pc in inv.get("preconditions", [])}
            # (a) Soundness: every declared precondition appears in the where-clause
            #     (the manifest cannot claim a guard the proof does not carry).
            for pc in inv.get("preconditions", []):
                recon = _norm(precond_string(pc))
                if recon not in where_norm:
                    failures.append(f"{iid}: precondition {precond_string(pc)!r} not found in {pname} where-clause")
            # (b) Completeness: every guard in the where-clause is declared (the
            #     manifest cannot UNDER-declare, which would let the consumer derive
            #     a validity region WIDER than the proof covers -- the forge the
            #     red-team found). declared preconditions must COVER the where-clause.
            for guard in split_guards(where_clause):
                gnorm = _norm(guard)
                if gnorm and gnorm not in declared_norm:
                    failures.append(f"{iid}: property {pname} where-clause guard {guard.strip()!r} is NOT declared in the manifest preconditions (under-declaration widens the derived validity region)")

        # expected_tier_per_pin: entry for current pin, valid token, trigger for amber.
        etp = inv.get("expected_tier_per_pin", {})
        if reef_pin not in etp:
            failures.append(f"{iid}: expected_tier_per_pin has no entry for current pin {reef_pin}")
        else:
            tier = etp[reef_pin]
            if tier not in TIER_TOKENS:
                failures.append(f"{iid}: expected tier {tier!r} not a frozen tier token")
            if tier != PROVEN_TIER and not inv.get("tier_upgrade_trigger"):
                failures.append(f"{iid}: below-proven tier {tier!r} carries no tier_upgrade_trigger citation")

        # Defective-model invariants must name a real defective model.
        dm = inv.get("defective_model")
        if dm is not None and dm not in model_ids:
            failures.append(f"{iid}: defective_model {dm!r} is not a manifest model")

        # nests_inside (org-implication pointer) must name a real invariant, so it
        # cannot silently rot to a renamed/deleted invariant id.
        ni = inv.get("nests_inside")
        if ni is not None and ni not in invariant_ids:
            failures.append(f"{iid}: nests_inside {ni!r} is not a manifest invariant id")

    if failures:
        print(f"contract_gate FAILED with {len(failures)} finding(s):")
        for f in failures:
            print(f"  FAIL {f}")
        return 1
    n_models = len(manifest.get("models", []))
    n_inv = len(manifest.get("invariants", []))
    print(f"contract_gate OK: manifest {SCHEMA_ID}/{SCHEMA_VERSION} consistent at pin {reef_pin} "
          f"({n_models} models, {n_inv} invariants; properties/controls resolve, preconditions COVER "
          f"their where-clauses both directions, output_fns exported, tiers cited).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
