"""Ckeletin spec validation — enforces the spec's own rules."""

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


def validate_level(level):
    """Check that a requirement level is a valid RFC 2119 keyword."""
    errors = []
    if level not in VALID_LEVELS:
        errors.append(f"'{level}' is not a valid level (must be MUST, SHOULD, or MAY)")
    return errors
