import os
import pytest
from scripts.validate_spec import (
    load_spec_file,
    validate_domain_fields,
    validate_requirement_fields,
    REQUIRED_DOMAIN_FIELDS,
    REQUIRED_REQUIREMENT_FIELDS,
)


class TestSpecFileStructure:
    def test_real_spec_files_parse(self, spec_dir):
        """Every spec YAML file in the repo must parse without error."""
        for fname in os.listdir(spec_dir):
            if fname.endswith(".yaml") and not fname.startswith("_"):
                path = os.path.join(spec_dir, fname)
                data = load_spec_file(path)
                assert data is not None, f"{fname} failed to parse"

    def test_real_spec_files_have_domain(self, spec_dir):
        """Every spec file must have domain.name and domain.description."""
        for fname in os.listdir(spec_dir):
            if fname.endswith(".yaml") and not fname.startswith("_"):
                path = os.path.join(spec_dir, fname)
                data = load_spec_file(path)
                errors = validate_domain_fields(data, fname)
                assert errors == [], f"{fname}: {errors}"

    def test_real_spec_requirements_have_required_fields(self, spec_dir):
        """Every requirement must have all required fields from schema."""
        for fname in os.listdir(spec_dir):
            if fname.endswith(".yaml") and not fname.startswith("_"):
                path = os.path.join(spec_dir, fname)
                data = load_spec_file(path)
                for req in data.get("requirements", []):
                    errors = validate_requirement_fields(req, fname)
                    assert errors == [], f"{fname} {req.get('id', '?')}: {errors}"

    def test_missing_fields_detected(self, fixtures_dir):
        """Fixture with missing fields must produce errors."""
        path = os.path.join(fixtures_dir, "bad_spec_missing_fields.yaml")
        data = load_spec_file(path)
        for req in data.get("requirements", []):
            errors = validate_requirement_fields(req, "bad_spec_missing_fields.yaml")
            assert len(errors) > 0, "Should detect missing rationale and checkable"
