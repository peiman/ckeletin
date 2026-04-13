import os
import pytest
from scripts.validate_spec import (
    load_spec_file,
    validate_domain_fields,
    validate_requirement_fields,
    validate_id_format,
    collect_all_ids,
    validate_id_uniqueness,
    validate_level,
    REQUIRED_DOMAIN_FIELDS,
    REQUIRED_REQUIREMENT_FIELDS,
    VALID_LEVELS,
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


class TestIdValidation:
    def test_valid_id_format(self):
        """Valid CKSPEC IDs pass format check."""
        assert validate_id_format("CKSPEC-ARCH-001") == []
        assert validate_id_format("CKSPEC-TEST-042") == []
        assert validate_id_format("CKSPEC-ENF-100") == []

    def test_invalid_id_format_missing_prefix(self):
        """IDs without CKSPEC- prefix are rejected."""
        errors = validate_id_format("SPEC-ARCH-001")
        assert len(errors) > 0

    def test_invalid_id_format_bad_number(self):
        """IDs with non-3-digit numbers are rejected."""
        errors = validate_id_format("CKSPEC-ARCH-01")
        assert len(errors) > 0

    def test_invalid_id_format_lowercase(self):
        """IDs with lowercase domain are rejected."""
        errors = validate_id_format("CKSPEC-arch-001")
        assert len(errors) > 0

    def test_real_spec_ids_valid_format(self, spec_dir):
        """All IDs in real spec files pass format check."""
        for fname in os.listdir(spec_dir):
            if fname.endswith(".yaml") and not fname.startswith("_"):
                path = os.path.join(spec_dir, fname)
                data = load_spec_file(path)
                for req in data.get("requirements", []):
                    errors = validate_id_format(req["id"])
                    assert errors == [], f"{req['id']}: {errors}"

    def test_real_spec_no_duplicate_ids(self, spec_dir):
        """No duplicate IDs across all real spec files."""
        all_ids = collect_all_ids(spec_dir)
        errors = validate_id_uniqueness(all_ids)
        assert errors == [], f"Duplicate IDs: {errors}"

    def test_duplicate_ids_detected(self, fixtures_dir):
        """Fixture with duplicate IDs must produce errors."""
        all_ids = collect_all_ids(fixtures_dir, pattern="bad_spec_duplicate_ids.yaml")
        errors = validate_id_uniqueness(all_ids)
        assert len(errors) > 0, "Should detect duplicate CKSPEC-DUP-001"

    def test_invalid_id_fixture_detected(self, fixtures_dir):
        """Fixture with bad ID format must produce errors."""
        path = os.path.join(fixtures_dir, "bad_spec_invalid_id.yaml")
        data = load_spec_file(path)
        for req in data.get("requirements", []):
            errors = validate_id_format(req["id"])
            assert len(errors) > 0, f"Should reject {req['id']}"


class TestEnumValidation:
    def test_valid_levels(self):
        """MUST, SHOULD, MAY are valid levels."""
        for level in ["MUST", "SHOULD", "MAY"]:
            assert validate_level(level) == []

    def test_invalid_level(self):
        """Non-standard levels are rejected."""
        errors = validate_level("REQUIRED")
        assert len(errors) > 0

    def test_lowercase_level_rejected(self):
        """Lowercase levels are rejected (RFC 2119 requires ALL CAPS)."""
        errors = validate_level("must")
        assert len(errors) > 0

    def test_real_spec_levels_valid(self, spec_dir):
        """All levels in real spec files are valid."""
        for fname in os.listdir(spec_dir):
            if fname.endswith(".yaml") and not fname.startswith("_"):
                path = os.path.join(spec_dir, fname)
                data = load_spec_file(path)
                for req in data.get("requirements", []):
                    errors = validate_level(req["level"])
                    assert errors == [], f"{req['id']}: {errors}"

    def test_invalid_level_fixture(self, fixtures_dir):
        """Fixture with bad level must produce errors."""
        path = os.path.join(fixtures_dir, "bad_spec_invalid_level.yaml")
        data = load_spec_file(path)
        for req in data.get("requirements", []):
            errors = validate_level(req["level"])
            assert len(errors) > 0
