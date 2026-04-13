"""Ckeletin spec validation — enforces the spec's own rules."""

import os
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
