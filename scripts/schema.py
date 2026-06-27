"""Single source of truth for the spec's enums and required-field sets.

`spec/_schema.yaml` is the authoritative definition of the spec's shape.
Every validator derives its enums and required-field sets from here rather
than carrying its own copy, so these facts live in exactly one place
(Principle 7 — SSOT). A derived fact can't drift; a hand-copied one will.
"""

import os

import yaml

_SCHEMA_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "spec",
    "_schema.yaml",
)

# Logical enum name -> (schema kind, field) where its values are defined.
_ENUM_LOCATIONS = {
    "level": ("requirement", "level"),
    "verification": ("requirement", "verification"),
    "status": ("conformance_entry", "status"),
    "enforcement_level": ("conformance_entry", "enforcement_level"),
}


def load_schema(path=None):
    """Load and parse spec/_schema.yaml."""
    with open(path or _SCHEMA_PATH, "r") as f:
        return yaml.safe_load(f)


def enum_values(name, schema=None):
    """Allowed values for a named enum, as a set, sourced from the schema."""
    schema = load_schema() if schema is None else schema
    kind, field = _ENUM_LOCATIONS[name]
    return set(schema[kind]["fields"][field]["values"])


def required_fields(kind, schema=None):
    """Field names marked `required: true` for a schema kind, as a set."""
    schema = load_schema() if schema is None else schema
    fields = schema[kind]["fields"]
    return {name for name, spec in fields.items() if spec.get("required")}
