# ckeletin

The ckeletin specification — a versioned, language-agnostic standard
for CLI application scaffolds.

## What This Is

ckeletin defines what a production-ready CLI scaffold must provide.
Implementations in specific languages document how they meet each
requirement.

This is not a top-down mandate. The specification and its
implementations learn from each other — conformance reports are
retrospectives, not audits.

## Current State (v0.1.0 — Lean Start)

Three core domains, verified against one implementation:

| Domain | Requirements | What it covers |
|--------|-------------|----------------|
| Architecture | CKSPEC-ARCH-001 to 007 | 4-layer architecture, dependency rules |
| Enforcement | CKSPEC-ENF-001 to 004 | Every decision must be enforced |
| Testing | CKSPEC-TEST-001 to 004 | TDD, coverage, dependency injection |

More domains will be added when ckeletin-rust needs them.

## Implementations

| Implementation | Language | Conformance |
|---------------|----------|-------------|
| [ckeletin-go](https://github.com/peiman/ckeletin-go) | Go | 15/15 met |
| ckeletin-rust | Rust | Planned |

## Validation

Requires [Task](https://taskfile.dev/installation/) and Python 3.

```bash
task check       # validate spec + conformance
task test        # run test suite (23 tests)
```

First run creates a virtual environment and installs dependencies
automatically.

Without Task:
```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python scripts/validate_spec.py
```

## Structure

```
spec/
  _schema.yaml             — Requirement format definition
  01-architecture.yaml     — 4-layer architecture
  02-enforcement.yaml      — Automated enforcement
  03-testing.yaml          — TDD, coverage, DI
conformance/
  ckeletin-go.yaml         — Go conformance report
principles.md              — The why behind everything
```

## Conformance Language

Uses [RFC 2119](https://datatracker.ietf.org/doc/html/rfc2119)
keywords: MUST, SHOULD, MAY. Normative only in ALL CAPS per
[RFC 8174](https://www.rfc-editor.org/rfc/rfc8174).

## Feedback Cycle

Implementations open issues tagged `feedback/go` or `feedback/rust`
to propose spec changes. The other implementation reviews before
merge. A requirement isn't proven until two implementations can
satisfy it.

## Principles

See [principles.md](principles.md).
