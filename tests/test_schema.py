"""Tests for the schema SSOT reader (scripts/schema.py).

Loader *logic* is pinned with synthetic schemas so these tests never restate
the real enum values (that would just be another hand-copied source). The real
values are exercised end-to-end by the validator tests.
"""

import pytest

from scripts.schema import enum_values, load_schema, required_fields


def test_enum_values_reads_named_location():
    schema = {"requirement": {"fields": {"level": {"values": ["MUST", "SHOULD"]}}}}
    assert enum_values("level", schema) == {"MUST", "SHOULD"}


def test_enum_values_enforcement_level_maps_to_conformance_entry():
    schema = {"conformance_entry": {"fields": {"enforcement_level": {"values": ["x", "y"]}}}}
    assert enum_values("enforcement_level", schema) == {"x", "y"}


def test_enum_values_returns_a_set_not_a_list():
    schema = {"requirement": {"fields": {"level": {"values": ["A", "A", "B"]}}}}
    assert enum_values("level", schema) == {"A", "B"}


def test_required_fields_keeps_only_required_true():
    schema = {
        "requirement": {
            "fields": {
                "id": {"required": True},
                "title": {"required": True},
                "notes": {"required": False},
                "modified": {},  # absent treated as not required
            }
        }
    }
    assert required_fields("requirement", schema) == {"id", "title"}


def test_unknown_enum_name_raises():
    with pytest.raises(KeyError):
        enum_values("not-an-enum", {"x": {}})


def test_real_schema_loads_and_exposes_the_three_enums():
    """The real schema must load and define all three named enums (non-empty),
    without asserting their contents — that stays in the schema, the SSOT."""
    schema = load_schema()
    for name in ("level", "status", "enforcement_level"):
        assert enum_values(name, schema), f"{name} enum is empty or missing"
