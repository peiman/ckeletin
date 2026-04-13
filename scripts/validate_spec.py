"""Ckeletin spec validation — enforces the spec's own rules."""

import json
import os
import re
import sys
import yaml

REQUIRED_DOMAIN_FIELDS = {"name", "description"}

REQUIRED_REQUIREMENT_FIELDS = {
    "id", "title", "level", "since", "checkable", "description", "rationale"
}


def load_spec_file(path):
    """Load and parse a YAML spec file."""
    with open(path, "r") as f:
        return yaml.safe_load(f)


def validate_domain_fields(data, filename):
    """Check that domain has all required fields."""
    errors = []
    domain = data.get("domain")
    if domain is None:
        errors.append(f"{filename}: missing 'domain' key")
        return errors
    for field in sorted(REQUIRED_DOMAIN_FIELDS):
        if field not in domain:
            errors.append(f"{filename}: domain missing '{field}'")
    return errors


def validate_requirement_fields(req, filename):
    """Check that a requirement has all required fields."""
    errors = []
    req_id = req.get("id", "unknown")
    for field in sorted(REQUIRED_REQUIREMENT_FIELDS):
        if field not in req:
            errors.append(f"{filename} {req_id}: missing '{field}'")
    return errors


ID_PATTERN = re.compile(r"^CKSPEC-[A-Z]+-\d{3}$")

VALID_LEVELS = {"MUST", "SHOULD", "MAY"}

VALID_STATUSES = {"met", "partial", "not-met", "not-applicable", "deferred"}


def validate_id_format(req_id):
    """Check that an ID matches CKSPEC-<DOMAIN>-<NNN> format."""
    errors = []
    if not ID_PATTERN.match(req_id):
        errors.append(f"'{req_id}' does not match CKSPEC-<DOMAIN>-<NNN> format")
    return errors


def collect_all_ids(directory, pattern=None):
    """Collect all requirement IDs from spec files in a directory.

    Returns list of (id, filename) tuples.
    """
    all_ids = []
    for fname in sorted(os.listdir(directory)):
        if pattern and fname != pattern:
            continue
        if not fname.endswith(".yaml") or fname.startswith("_"):
            continue
        path = os.path.join(directory, fname)
        data = load_spec_file(path)
        if data and "requirements" in data:
            for req in data["requirements"]:
                if "id" in req:
                    all_ids.append((req["id"], fname))
    return all_ids


def validate_id_uniqueness(id_list):
    """Check for duplicate IDs. Input is list of (id, filename) tuples."""
    errors = []
    seen = {}
    for req_id, fname in id_list:
        if req_id in seen:
            errors.append(
                f"Duplicate ID '{req_id}' in {fname} (first seen in {seen[req_id]})"
            )
        else:
            seen[req_id] = fname
    return errors


def collect_all_requirements(directory):
    """Collect full requirement metadata from spec files.

    Returns list of dicts sorted by ID with fields: id, title, level,
    checkable, domain, since, and optionally modified.
    """
    requirements = []
    for fname in sorted(os.listdir(directory)):
        if not fname.endswith(".yaml") or fname.startswith("_"):
            continue
        path = os.path.join(directory, fname)
        data = load_spec_file(path)
        if data is None:
            continue
        domain_name = data.get("domain", {}).get("name", "")
        for req in data.get("requirements", []):
            if "id" not in req:
                continue
            entry = {
                "id": req["id"],
                "title": req.get("title", ""),
                "level": req.get("level", ""),
                "checkable": req.get("checkable", False),
                "domain": domain_name,
                "since": req.get("since", ""),
            }
            if "modified" in req:
                entry["modified"] = req["modified"]
            requirements.append(entry)
    requirements.sort(key=lambda r: r["id"])
    return requirements


def _parse_version(version_str):
    """Parse 'vX.Y.Z' to tuple for comparison."""
    return tuple(int(x) for x in version_str.lstrip("v").split("."))


def _derive_spec_version(requirements):
    """Derive spec version from highest since/modified across all requirements."""
    versions = set()
    for req in requirements:
        if req.get("since"):
            versions.add(req["since"])
        if req.get("modified"):
            versions.add(req["modified"])
    if not versions:
        return "0.0.0"
    highest = max(versions, key=_parse_version)
    return highest.lstrip("v")


def generate_requirements_data(spec_dir):
    """Generate the requirements.json data structure from spec YAML files.

    Returns a dict with spec_version and sorted requirements list.
    """
    requirements = collect_all_requirements(spec_dir)
    spec_version = _derive_spec_version(requirements)

    return {
        "spec_version": spec_version,
        "requirements": requirements,
    }


def validate_requirements_json_sync(spec_dir):
    """Check that spec/requirements.json matches the spec YAML files.

    Returns list of errors.
    """
    errors = []
    json_path = os.path.join(spec_dir, "requirements.json")

    if not os.path.exists(json_path):
        errors.append(
            "spec/requirements.json does not exist"
            " — run 'task generate:requirements'"
        )
        return errors

    expected = generate_requirements_data(spec_dir)
    expected_json = json.dumps(expected, indent=2) + "\n"

    with open(json_path, "r") as f:
        actual_json = f.read()

    if actual_json != expected_json:
        errors.append(
            "spec/requirements.json is out of sync with spec YAML files"
            " — run 'task generate:requirements'"
        )

    return errors


def validate_level(level):
    """Check that a requirement level is a valid RFC 2119 keyword."""
    errors = []
    if level not in VALID_LEVELS:
        errors.append(f"'{level}' is not a valid level (must be MUST, SHOULD, or MAY)")
    return errors


REQUIRED_CONFORMANCE_HEADER_FIELDS = {"implementation", "spec_version", "report_date"}

REQUIRED_CONFORMANCE_ENTRY_FIELDS = {"status", "evidence"}


def validate_conformance_header(data, filename):
    """Check that a conformance report has required header fields."""
    errors = []
    for field in sorted(REQUIRED_CONFORMANCE_HEADER_FIELDS):
        if field not in data:
            errors.append(f"{filename}: missing header field '{field}'")
    return errors


def validate_conformance_entry(req_id, entry, filename):
    """Check that a conformance entry has required fields and valid values."""
    errors = []
    for field in sorted(REQUIRED_CONFORMANCE_ENTRY_FIELDS):
        if field not in entry:
            errors.append(f"{filename} {req_id}: missing '{field}'")
    if "status" in entry and entry["status"] not in VALID_STATUSES:
        errors.append(
            f"{filename} {req_id}: invalid status '{entry['status']}'"
            f" (must be one of: {', '.join(sorted(VALID_STATUSES))})"
        )
    return errors


def validate_conformance_coverage(spec_ids, conformance_ids, filename):
    """Check that spec and conformance IDs match exactly."""
    errors = []
    missing_from_conformance = spec_ids - conformance_ids
    orphaned_in_conformance = conformance_ids - spec_ids
    for mid in sorted(missing_from_conformance):
        errors.append(f"{filename}: spec ID '{mid}' has no conformance entry")
    for oid in sorted(orphaned_in_conformance):
        errors.append(f"{filename}: conformance ID '{oid}' has no matching spec requirement")
    return errors


def collect_conformance_warnings(conformance_dir):
    """Collect warnings for deferred, not-met, and partial conformance entries.

    These are not errors — the report is valid — but they must be visible
    so incomplete work doesn't hide behind a green check.
    """
    warnings = []
    conformance_files = sorted(
        f for f in os.listdir(conformance_dir)
        if f.endswith(".yaml")
    )
    for fname in conformance_files:
        path = os.path.join(conformance_dir, fname)
        data = load_spec_file(path)
        if data is None:
            continue
        impl_name = data.get("implementation", fname)
        reqs = data.get("requirements", {})
        if not isinstance(reqs, dict):
            continue
        for req_id, entry in reqs.items():
            status = entry.get("status", "")
            if status == "deferred":
                warnings.append(f"{impl_name}: {req_id} is deferred")
            elif status == "not-met":
                warnings.append(f"{impl_name}: {req_id} is not met")
            elif status == "partial":
                warnings.append(f"{impl_name}: {req_id} is partial")
    return warnings


def validate_all(spec_dir, conformance_dir):
    """Run all validation checks. Returns (errors, warnings)."""
    all_errors = []

    spec_files = sorted(
        f for f in os.listdir(spec_dir)
        if f.endswith(".yaml") and not f.startswith("_")
    )
    all_ids = []

    for fname in spec_files:
        path = os.path.join(spec_dir, fname)
        data = load_spec_file(path)
        if data is None:
            all_errors.append(f"{fname}: failed to parse YAML")
            continue

        all_errors.extend(validate_domain_fields(data, fname))

        for req in data.get("requirements", []):
            all_errors.extend(validate_requirement_fields(req, fname))
            if "id" in req:
                all_errors.extend(validate_id_format(req["id"]))
                all_ids.append((req["id"], fname))
            if "level" in req:
                all_errors.extend(validate_level(req["level"]))

    all_errors.extend(validate_id_uniqueness(all_ids))

    all_errors.extend(validate_requirements_json_sync(spec_dir))

    spec_id_set = {sid for sid, _ in all_ids}

    conformance_files = sorted(
        f for f in os.listdir(conformance_dir)
        if f.endswith(".yaml")
    )

    for fname in conformance_files:
        path = os.path.join(conformance_dir, fname)
        data = load_spec_file(path)
        if data is None:
            all_errors.append(f"{fname}: failed to parse YAML")
            continue

        all_errors.extend(validate_conformance_header(data, fname))

        conformance_ids = set()
        for req_id, entry in data.get("requirements", {}).items():
            conformance_ids.add(req_id)
            all_errors.extend(validate_conformance_entry(req_id, entry, fname))

        all_errors.extend(
            validate_conformance_coverage(spec_id_set, conformance_ids, fname)
        )

    all_warnings = collect_conformance_warnings(conformance_dir)

    return all_errors, all_warnings


def main():
    """CLI entry point — run all validation, print results, exit 0/1."""
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    spec_dir = os.path.join(repo_root, "spec")
    conformance_dir = os.path.join(repo_root, "conformance")

    print("Validating ckeletin spec...")
    print()

    errors, warnings = validate_all(spec_dir, conformance_dir)

    if errors:
        print(f"FAILED — {len(errors)} error(s):\n")
        for err in errors:
            print(f"  - {err}")
        sys.exit(1)
    else:
        spec_count = len([
            f for f in os.listdir(spec_dir)
            if f.endswith(".yaml") and not f.startswith("_")
        ])
        id_count = len(collect_all_ids(spec_dir))
        conformance_count = len([
            f for f in os.listdir(conformance_dir)
            if f.endswith(".yaml")
        ])
        print(f"PASSED — {spec_count} spec files, {id_count} requirements, "
              f"{conformance_count} conformance report(s)")

        if warnings:
            print(f"\n⚠ {len(warnings)} conformance warning(s):\n")
            for warn in warnings:
                print(f"  - {warn}")

        sys.exit(0)


if __name__ == "__main__":
    main()
