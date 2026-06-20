#!/usr/bin/env python3
"""Enforce the spec feedback cycle (see CONTRIBUTING.md) in CI.

Fails when either:
  1. the feedback register has an untriaged ('open') or undecided/incomplete
     report — maintainer discipline, nothing silently dropped; or
  2. a tracked implementation no longer conforms to the CURRENT spec version —
     the "teeth": a spec change that breaks a consumer must surface.

This is a DELIBERATE hard gate: the spec's CI stays red until every implementation
re-conforms. The learning loop only closes when consumers stay green, so the spec
cannot quietly advance past its implementations — they always get a vote.

The gate is SELF-SUFFICIENT: it cross-checks each conformance report against the
spec's own requirement IDs (it does not assume an earlier validate step ran). All
malformed/missing inputs fail CLEANLY via fail(), never a raw traceback.

Source of truth: feedback/register.json plus the REAL aggregated consumer
reports in conformance/*.yaml. pyyaml only (already a dependency); no network.
"""
import json
import pathlib
import sys

import yaml

ROOT = pathlib.Path(__file__).resolve().parent.parent
REGISTER = ROOT / "feedback" / "register.json"
REQUIREMENTS = ROOT / "spec" / "requirements.json"
CONFORMANCE_DIR = ROOT / "conformance"

VALID_STATUS = {"open", "triaged", "discussing", "accepted", "rejected", "done"}
VALID_DECISION = {"update", "discuss", "reject"}
# A fully-recorded report carries these (matches the schema in CONTRIBUTING.md);
# `decision`/`rationale` are validated separately by state below.
REQUIRED_FIELDS = ("id", "reporter", "spec_rule", "summary")


def fail(msg: str) -> None:
    print(f"FEEDBACK CHECK FAILED: {msg}", file=sys.stderr)
    sys.exit(1)


def _load_json(path: pathlib.Path, what: str):
    try:
        return json.loads(path.read_text())
    except FileNotFoundError:
        fail(f"{what} not found at {path}")
    except json.JSONDecodeError as e:
        fail(f"{what} is not valid JSON ({path}): {e}")


def check_register(register_path: pathlib.Path = REGISTER) -> int:
    """Validate every report is fully recorded, triaged, and decided."""
    data = _load_json(register_path, "feedback register")
    items = data.get("items", []) if isinstance(data, dict) else None
    if not isinstance(items, list):
        fail("register must be an object with an 'items' list")
    for i, it in enumerate(items):
        if not isinstance(it, dict):
            fail(f"register item #{i} is not an object")
        rid = it.get("id") or f"#{i}"
        for field in REQUIRED_FIELDS:
            if not it.get(field):
                fail(f"{rid}: missing required field '{field}'")
        status = it.get("status")
        if status not in VALID_STATUS:
            fail(f"{rid}: invalid status {status!r} (one of {sorted(VALID_STATUS)})")
        if status == "open":
            fail(f"{rid}: still untriaged ('open') — triage and record a decision")
        decision = it.get("decision")
        if decision not in VALID_DECISION:
            fail(f"{rid}: '{status}' has decision {decision!r}; expected one of "
                 f"{sorted(VALID_DECISION)} — no silent drops")
        if status == "rejected" and not it.get("rationale"):
            fail(f"{rid}: rejected without a written rationale")
    print(f"register: {len(items)} report(s), all recorded + triaged + decided")
    return len(items)


def _spec(requirements_path: pathlib.Path):
    data = _load_json(requirements_path, "spec/requirements.json")
    try:
        ids = {r["id"] for r in data["requirements"]}
        version = str(data["spec_version"])
    except (KeyError, TypeError):
        fail(f"{requirements_path}: missing 'requirements' list or 'spec_version'")
    if not ids:
        fail(f"{requirements_path}: spec lists zero requirements")
    return ids, version


def check_consumers(
    conformance_dir: pathlib.Path = CONFORMANCE_DIR,
    requirements_path: pathlib.Path = REQUIREMENTS,
) -> None:
    """Every consumer must report EVERY current spec requirement as met."""
    spec_ids, spec_version = _spec(requirements_path)
    reports = sorted(conformance_dir.glob("*.yaml"))
    if not reports:
        fail(f"no conformance reports found in {conformance_dir}")
    for rep in reports:
        try:
            d = yaml.safe_load(rep.read_text())
        except yaml.YAMLError as e:
            fail(f"{rep.name}: not valid YAML ({e})")
        if not isinstance(d, dict):
            fail(f"{rep.name}: conformance report is empty or not a mapping")
        impl = d.get("implementation", rep.stem)
        ver = str(d.get("spec_version"))
        if ver != spec_version:
            fail(f"{impl}: conformance is for spec {ver}, current spec is "
                 f"{spec_version} — re-run the implementation's conformance")
        reqs = d.get("requirements")
        if not isinstance(reqs, dict) or not reqs:
            fail(f"{impl}: conformance report has no requirements table")
        missing = sorted(spec_ids - set(reqs))
        if missing:
            shown = ", ".join(missing[:5]) + ("…" if len(missing) > 5 else "")
            fail(f"{impl}: report is missing {len(missing)} spec requirement(s): {shown}")
        # A requirement entry must be a {status: ...} mapping that says "met";
        # anything else (missing, null, or a malformed non-mapping value) is
        # NOT met and surfaces through the clean fail() below — never a crash.
        unmet = sorted(r for r in spec_ids
                       if not (isinstance(reqs.get(r), dict)
                               and reqs[r].get("status") == "met"))
        if unmet:
            shown = ", ".join(unmet[:5]) + ("…" if len(unmet) > 5 else "")
            fail(f"{impl}: no longer conforms to spec {spec_version} — unmet: {shown}")
        print(f"consumer {impl}: conforms to spec {spec_version} (all {len(spec_ids)} met)")


def main(
    register: pathlib.Path = REGISTER,
    conformance_dir: pathlib.Path = CONFORMANCE_DIR,
    requirements: pathlib.Path = REQUIREMENTS,
) -> None:
    check_register(register)
    check_consumers(conformance_dir, requirements)
    print("feedback cycle: OK")


if __name__ == "__main__":
    main()
