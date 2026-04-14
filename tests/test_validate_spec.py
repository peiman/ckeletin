import json
import os
import tempfile
import pytest
from scripts.validate_spec import (
    load_spec_file,
    validate_domain_fields,
    validate_requirement_fields,
    validate_id_format,
    collect_all_ids,
    validate_id_uniqueness,
    validate_level,
    validate_conformance_header,
    validate_conformance_entry,
    validate_conformance_coverage,
    collect_conformance_warnings,
    collect_all_requirements,
    generate_requirements_data,
    validate_requirements_json_sync,
    _parse_version,
    _derive_spec_version,
    REQUIRED_DOMAIN_FIELDS,
    REQUIRED_REQUIREMENT_FIELDS,
    REQUIRED_CONFORMANCE_HEADER_FIELDS,
    VALID_LEVELS,
    VALID_STATUSES,
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


class TestConformanceValidation:
    def test_real_conformance_has_header(self, conformance_dir):
        """Real conformance report must have required header fields."""
        for fname in os.listdir(conformance_dir):
            if fname.endswith(".yaml"):
                path = os.path.join(conformance_dir, fname)
                data = load_spec_file(path)
                errors = validate_conformance_header(data, fname)
                assert errors == [], f"{fname}: {errors}"

    def test_real_conformance_entries_valid(self, conformance_dir):
        """Real conformance entries must have status + evidence."""
        for fname in os.listdir(conformance_dir):
            if fname.endswith(".yaml"):
                path = os.path.join(conformance_dir, fname)
                data = load_spec_file(path)
                for req_id, entry in data.get("requirements", {}).items():
                    errors = validate_conformance_entry(req_id, entry, fname)
                    assert errors == [], f"{fname} {req_id}: {errors}"

    def test_real_conformance_coverage_complete(self, spec_dir, conformance_dir):
        """Every spec ID must have a conformance entry and vice versa."""
        spec_ids = collect_all_ids(spec_dir)
        for fname in os.listdir(conformance_dir):
            if fname.endswith(".yaml"):
                path = os.path.join(conformance_dir, fname)
                data = load_spec_file(path)
                conformance_ids = set(data.get("requirements", {}).keys())
                errors = validate_conformance_coverage(
                    {sid for sid, _ in spec_ids}, conformance_ids, fname
                )
                assert errors == [], f"{fname}: {errors}"

    def test_missing_evidence_detected(self, fixtures_dir):
        """Conformance entry without evidence must be rejected."""
        path = os.path.join(fixtures_dir, "bad_conformance_missing.yaml")
        data = load_spec_file(path)
        for req_id, entry in data.get("requirements", {}).items():
            errors = validate_conformance_entry(req_id, entry, "bad_conformance_missing.yaml")
            assert len(errors) > 0, f"Should detect missing evidence for {req_id}"

    def test_invalid_status_detected(self, fixtures_dir):
        """Conformance entry with invalid status must be rejected."""
        path = os.path.join(fixtures_dir, "bad_conformance_status.yaml")
        data = load_spec_file(path)
        for req_id, entry in data.get("requirements", {}).items():
            errors = validate_conformance_entry(req_id, entry, "bad_conformance_status.yaml")
            assert len(errors) > 0, f"Should reject status 'complete' for {req_id}"

    def test_orphan_conformance_detected(self, fixtures_dir, spec_dir):
        """Conformance entry referencing nonexistent spec ID must be caught."""
        spec_ids = {sid for sid, _ in collect_all_ids(spec_dir)}
        path = os.path.join(fixtures_dir, "bad_conformance_orphan.yaml")
        data = load_spec_file(path)
        conformance_ids = set(data.get("requirements", {}).keys())
        errors = validate_conformance_coverage(
            spec_ids, conformance_ids, "bad_conformance_orphan.yaml"
        )
        assert len(errors) > 0, "Should detect orphan CKSPEC-GHOST-001"


class TestConformanceWarnings:
    def test_deferred_entries_produce_warnings(self, fixtures_dir):
        """Deferred, not-met, and partial entries must produce warnings."""
        warnings = collect_conformance_warnings(fixtures_dir)
        # Filter to our specific fixture (fixtures_dir has many files)
        deferred = [w for w in warnings if "deferred" in w]
        not_met = [w for w in warnings if "not met" in w]
        partial = [w for w in warnings if "partial" in w]
        assert len(deferred) > 0, "Should warn about deferred entries"
        assert len(not_met) > 0, "Should warn about not-met entries"
        assert len(partial) > 0, "Should warn about partial entries"

    def test_met_entries_produce_no_warnings(self):
        """A conformance dir with only 'met' entries produces no warnings."""
        import tempfile
        import yaml

        with tempfile.TemporaryDirectory() as tmpdir:
            report = {
                "implementation": "perfect-impl",
                "spec_version": "0.1.0",
                "report_date": "2026-04-13",
                "requirements": {
                    "CKSPEC-TEST-001": {
                        "status": "met",
                        "evidence": "Everything works",
                    },
                },
            }
            path = os.path.join(tmpdir, "perfect.yaml")
            with open(path, "w") as f:
                yaml.dump(report, f)
            warnings = collect_conformance_warnings(tmpdir)
            assert warnings == [], f"Should have no warnings, got: {warnings}"

    def test_real_conformance_warnings_visible(self, conformance_dir):
        """Real conformance reports' non-met entries produce warnings."""
        warnings = collect_conformance_warnings(conformance_dir)
        # ckeletin-rust has partial entries; ckeletin-go is 35/35 met
        non_met = [w for w in warnings if "partial" in w or "deferred" in w or "not met" in w]
        assert len(non_met) >= 1, (
            f"Expected at least 1 non-met warning (from any conformance report), "
            f"got {len(non_met)}: {non_met}"
        )


class TestRequirementsGeneration:
    def test_collect_all_requirements_count(self, spec_dir):
        """Must collect all 35 requirements from spec files."""
        reqs = collect_all_requirements(spec_dir)
        assert len(reqs) == 35, f"Expected 35 requirements, got {len(reqs)}"

    def test_collect_all_requirements_has_required_fields(self, spec_dir):
        """Every collected requirement must have id, title, level, checkable, domain, since."""
        reqs = collect_all_requirements(spec_dir)
        required_keys = {"id", "title", "level", "checkable", "domain", "since"}
        for req in reqs:
            missing = required_keys - set(req.keys())
            assert missing == set(), f"{req['id']}: missing keys {missing}"

    def test_collect_all_requirements_sorted_by_id(self, spec_dir):
        """Requirements must be sorted alphabetically by ID."""
        reqs = collect_all_requirements(spec_dir)
        ids = [r["id"] for r in reqs]
        assert ids == sorted(ids), "Requirements must be sorted by ID"

    def test_collect_all_requirements_domains_populated(self, spec_dir):
        """Every requirement must have a non-empty domain name."""
        reqs = collect_all_requirements(spec_dir)
        for req in reqs:
            assert req["domain"] != "", f"{req['id']}: domain must not be empty"

    def test_parse_version(self):
        """Version strings parse to comparable tuples."""
        assert _parse_version("v0.1.0") == (0, 1, 0)
        assert _parse_version("v1.2.3") == (1, 2, 3)
        assert _parse_version("v0.1.0") < _parse_version("v0.2.0")
        assert _parse_version("v0.4.0") > _parse_version("v0.3.0")

    def test_derive_spec_version(self):
        """Spec version is the highest since/modified across requirements."""
        reqs = [
            {"since": "v0.1.0"},
            {"since": "v0.2.0", "modified": "v0.4.0"},
            {"since": "v0.3.0"},
        ]
        assert _derive_spec_version(reqs) == "0.4.0"

    def test_derive_spec_version_empty(self):
        """Empty requirements list produces version 0.0.0."""
        assert _derive_spec_version([]) == "0.0.0"

    def test_generate_requirements_data_structure(self, spec_dir):
        """Generated data must have spec_version and requirements list."""
        data = generate_requirements_data(spec_dir)
        assert "spec_version" in data
        assert "requirements" in data
        assert isinstance(data["requirements"], list)
        assert len(data["requirements"]) == 35

    def test_generate_requirements_data_spec_version(self, spec_dir):
        """Spec version must match highest version in requirements."""
        data = generate_requirements_data(spec_dir)
        # v0.4.0 is the highest (CKSPEC-ENF-006 modified: v0.4.0)
        assert data["spec_version"] == "0.4.0"

    def test_generate_requirements_data_deterministic(self, spec_dir):
        """Two calls must produce identical output."""
        data1 = generate_requirements_data(spec_dir)
        data2 = generate_requirements_data(spec_dir)
        assert json.dumps(data1) == json.dumps(data2)

    def test_requirements_json_in_sync(self, spec_dir):
        """spec/requirements.json must match generated output."""
        errors = validate_requirements_json_sync(spec_dir)
        assert errors == [], (
            f"requirements.json out of sync: {errors}. "
            "Run 'task generate:requirements' to fix."
        )

    def test_requirements_json_missing_detected(self):
        """Missing requirements.json must produce an error."""
        with tempfile.TemporaryDirectory() as tmpdir:
            errors = validate_requirements_json_sync(tmpdir)
            assert len(errors) == 1
            assert "does not exist" in errors[0]

    def test_requirements_json_stale_detected(self, spec_dir):
        """Stale requirements.json must produce an error."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Copy a spec file into tmpdir
            import shutil
            import yaml

            src = os.path.join(spec_dir, "01-architecture.yaml")
            shutil.copy2(src, os.path.join(tmpdir, "01-architecture.yaml"))

            # Write a requirements.json with wrong content
            stale = {"spec_version": "0.0.0", "requirements": []}
            json_path = os.path.join(tmpdir, "requirements.json")
            with open(json_path, "w") as f:
                json.dump(stale, f, indent=2)
                f.write("\n")

            errors = validate_requirements_json_sync(tmpdir)
            assert len(errors) == 1
            assert "out of sync" in errors[0]
