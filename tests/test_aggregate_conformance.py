"""Tests for scripts/aggregate_conformance.py."""

import json
import os

import yaml

from scripts.aggregate_conformance import (
    aggregate,
    dump_conformance_yaml,
    fetch_report,
    report_to_conformance,
)
from scripts.validate_spec import (
    collect_all_ids,
    generate_requirements_data,
    validate_conformance_coverage,
    validate_conformance_entry,
    validate_conformance_header,
)


def _sample_report():
    """A minimal but representative published report."""
    return {
        "implementation": "ckeletin-go",
        "spec_version": "0.6.0",
        "summary": {"total": 2, "met": 2, "partial": 0, "deferred": 0, "passed": True},
        "requirements": {
            "CKSPEC-ARCH-001": {
                "status": "met",
                "enforcement_level": "linter",
                "evidence": "go-arch-lint enforces the four layers.\n",
                "checks": ["task validate:layering"],
                "violation_tests": ["test/conformance/violation_test.go::TestViolation_ARCH001"],
                "violation_evidence": None,
            },
            "CKSPEC-ENF-001": {
                "status": "met",
                "enforcement_level": "honor-system",
                "evidence": "Meta-requirement.\n",
                "checks": [],
                "violation_tests": [],
                "violation_evidence": "Assessed at review.\n",
            },
        },
    }


class TestReportToConformance:
    def test_header_fields(self):
        out = report_to_conformance(_sample_report(), "2026-06-04")
        assert out["implementation"] == "ckeletin-go"
        assert out["spec_version"] == "0.6.0"
        assert out["report_date"] == "2026-06-04"

    def test_every_entry_has_required_fields(self):
        out = report_to_conformance(_sample_report(), "2026-06-04")
        for req_id, entry in out["requirements"].items():
            assert "status" in entry, req_id
            assert "evidence" in entry, req_id

    def test_checks_become_tests(self):
        out = report_to_conformance(_sample_report(), "2026-06-04")
        assert out["requirements"]["CKSPEC-ARCH-001"]["tests"] == ["task validate:layering"]

    def test_optional_fields_present_when_set(self):
        out = report_to_conformance(_sample_report(), "2026-06-04")
        arch = out["requirements"]["CKSPEC-ARCH-001"]
        assert arch["enforcement_level"] == "linter"
        assert arch["violation_tests"] == [
            "test/conformance/violation_test.go::TestViolation_ARCH001"
        ]

    def test_empty_optional_fields_omitted(self):
        out = report_to_conformance(_sample_report(), "2026-06-04")
        enf = out["requirements"]["CKSPEC-ENF-001"]
        # ENF-001 has empty checks/violation_tests and null violation_evidence handling
        assert "tests" not in enf
        assert "violation_tests" not in enf
        # but it has a violation_evidence string, which IS carried
        assert enf["violation_evidence"] == "Assessed at review."

    def test_evidence_trailing_whitespace_stripped(self):
        out = report_to_conformance(_sample_report(), "2026-06-04")
        assert out["requirements"]["CKSPEC-ARCH-001"]["evidence"] == (
            "go-arch-lint enforces the four layers."
        )

    def test_requirements_sorted_by_id(self):
        report = _sample_report()
        # Insert in reverse order to prove the transform sorts.
        report["requirements"] = dict(reversed(list(report["requirements"].items())))
        out = report_to_conformance(report, "2026-06-04")
        assert list(out["requirements"].keys()) == ["CKSPEC-ARCH-001", "CKSPEC-ENF-001"]


class TestPassesSpecValidation:
    def test_transformed_entries_pass_validators(self):
        out = report_to_conformance(_sample_report(), "2026-06-04")
        assert validate_conformance_header(out, "ckeletin-go.yaml") == []
        for req_id, entry in out["requirements"].items():
            assert validate_conformance_entry(req_id, entry, "ckeletin-go.yaml") == []

    def test_full_coverage_against_real_spec(self, spec_dir):
        """A report covering every real spec ID aggregates to a complete file."""
        spec_ids = {rid for rid, _ in collect_all_ids(spec_dir)}
        data = generate_requirements_data(spec_dir)
        report = {
            "implementation": "ckeletin-go",
            "spec_version": data["spec_version"],
            "requirements": {
                rid: {"status": "met", "evidence": "covered", "checks": ["test -f x"]}
                for rid in spec_ids
            },
        }
        out = report_to_conformance(report, "2026-06-04")
        conformance_ids = set(out["requirements"])
        assert validate_conformance_coverage(spec_ids, conformance_ids, "f.yaml") == []

    def test_dumped_yaml_round_trips(self):
        out = report_to_conformance(_sample_report(), "2026-06-04")
        reparsed = yaml.safe_load(dump_conformance_yaml(out))
        assert reparsed["implementation"] == "ckeletin-go"
        assert set(reparsed["requirements"]) == {"CKSPEC-ARCH-001", "CKSPEC-ENF-001"}


class TestFetchAndAggregate:
    def test_fetch_report_from_local_file(self, tmp_path):
        report = _sample_report()
        p = tmp_path / "report.json"
        p.write_text(json.dumps(report))
        assert fetch_report(str(p))["implementation"] == "ckeletin-go"

    def test_aggregate_writes_file(self, tmp_path):
        report = _sample_report()
        src = tmp_path / "report.json"
        src.write_text(json.dumps(report))
        conf_dir = tmp_path / "conformance"
        conf_dir.mkdir()
        written, failed = aggregate(
            str(conf_dir), "2026-06-04",
            registry={"ckeletin-go": str(src)},
        )
        assert written == ["ckeletin-go"]
        assert failed == []
        produced = yaml.safe_load((conf_dir / "ckeletin-go.yaml").read_text())
        assert produced["report_date"] == "2026-06-04"
        assert len(produced["requirements"]) == 2

    def test_aggregate_graceful_on_fetch_failure(self, tmp_path):
        conf_dir = tmp_path / "conformance"
        conf_dir.mkdir()
        existing = conf_dir / "ckeletin-go.yaml"
        existing.write_text("implementation: ckeletin-go\n")  # pre-existing, must survive
        written, failed = aggregate(
            str(conf_dir), "2026-06-04",
            registry={"ckeletin-go": str(tmp_path / "does-not-exist.json")},
        )
        assert written == []
        assert failed == ["ckeletin-go"]
        # The existing file is untouched (graceful fallback).
        assert existing.read_text() == "implementation: ckeletin-go\n"

    def test_generated_header_marks_auto_generated(self, tmp_path):
        report = _sample_report()
        src = tmp_path / "report.json"
        src.write_text(json.dumps(report))
        conf_dir = tmp_path / "conformance"
        conf_dir.mkdir()
        aggregate(str(conf_dir), "2026-06-04", registry={"ckeletin-go": str(src)})
        text = (conf_dir / "ckeletin-go.yaml").read_text()
        assert "AUTO-GENERATED" in text
        assert "Do NOT edit by hand" in text

    def test_aggregate_graceful_on_malformed_report(self, tmp_path):
        # Valid JSON, but structurally malformed (a requirement entry has no 'status').
        bad = {
            "implementation": "ckeletin-go",
            "spec_version": "0.6.0",
            "requirements": {"CKSPEC-ARCH-001": {"evidence": "x"}},
        }
        src = tmp_path / "bad.json"
        src.write_text(json.dumps(bad))
        conf_dir = tmp_path / "conformance"
        conf_dir.mkdir()
        existing = conf_dir / "ckeletin-go.yaml"
        existing.write_text("implementation: ckeletin-go\n")
        written, failed = aggregate(
            str(conf_dir), "2026-06-04",
            registry={"ckeletin-go": str(src)},
        )
        assert written == []
        assert failed == ["ckeletin-go"]
        # The existing file is left untouched (graceful fallback, not truncated).
        assert existing.read_text() == "implementation: ckeletin-go\n"

    def test_one_malformed_report_does_not_block_others(self, tmp_path):
        good = _sample_report()
        good_src = tmp_path / "good.json"
        good_src.write_text(json.dumps(good))
        bad_src = tmp_path / "bad.json"
        bad_src.write_text(json.dumps({"implementation": "x"}))  # missing spec_version
        conf_dir = tmp_path / "conformance"
        conf_dir.mkdir()
        written, failed = aggregate(
            str(conf_dir), "2026-06-04",
            # Bad impl first; the good one must still be processed.
            registry={"ckeletin-bad": str(bad_src), "ckeletin-go": str(good_src)},
        )
        assert failed == ["ckeletin-bad"]
        assert written == ["ckeletin-go"]
        assert (conf_dir / "ckeletin-go.yaml").exists()
        assert not (conf_dir / "ckeletin-bad.yaml").exists()
