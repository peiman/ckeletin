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

## Current State

Six domains, verified against the reference implementations:

| # | Domain | Requirements | Platform it creates |
|---|--------|-------------|---------------------|
| 01 | Architecture | CKSPEC-ARCH-001 to 007 | Code organization, layer boundaries |
| 02 | Enforcement | CKSPEC-ENF-001 to 010 | Every rule is automated |
| 03 | Testing | CKSPEC-TEST-001 to 004 | Correctness is verified |
| 04 | Output | CKSPEC-OUT-001 to 006 | Machines can parse responses |
| 05 | Agent Readiness | CKSPEC-AGENT-001 to 006 | Any agent can use the project |
| 06 | Changelog | CKSPEC-CL-001 to 007 | Changes are communicated |

Each domain is a platform for the ones after it. The order matters.

## Implementations

| Implementation | Language | Conformance report |
|---------------|----------|-------------|
| [ckeletin-go](https://github.com/peiman/ckeletin-go) | Go | [`conformance/ckeletin-go.yaml`](conformance/ckeletin-go.yaml) |
| [ckeletin-rust](https://github.com/peiman/ckeletin-rust) | Rust | [`conformance/ckeletin-rust.yaml`](conformance/ckeletin-rust.yaml) |

Which requirements each implementation meets is **not duplicated here** — it
lives in the auto-generated reports under [`conformance/`](conformance/), the
single source of truth (one report per implementation, regenerated from each
implementation's published conformance data). A hand-copied status drifts the
moment an implementation ships a change — this table once read
"ckeletin-rust: Planned" long after Rust had become the most advanced
implementation. So the README links to the live reports rather than restating
them — Single Source of Truth (a derived/linked fact can't drift; a hand-copied
one will).

## Validation

Requires [Task](https://taskfile.dev/installation/) and Python 3.

```bash
task check       # validate spec + conformance
task test        # run test suite
```

First run creates a virtual environment and installs dependencies
automatically.

Without Task:
```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python scripts/validate_spec.py
```

## Changelog Management

Uses [changie](https://github.com/peiman/changie) for changelog
enforcement (CKSPEC-CL requirements).

```bash
task changelog:added -- "New feature description"
task changelog:fixed -- "Bug fix description"
task release -- minor
```

Or directly: `changie changelog added "..."`, `changie bump minor`.

## Structure

```
spec/
  _schema.yaml             — Requirement format definition
  01-architecture.yaml     — 4-layer architecture
  02-enforcement.yaml      — Automated enforcement
  03-testing.yaml          — TDD, coverage, DI
  04-output.yaml           — 3-stream model, JSON, shadow logging
  05-agent-readiness.yaml  — AGENTS.md, provider guides, CLI interface
  06-changelog.yaml        — Keep a Changelog, SemVer
conformance/
  <implementation>.yaml    — one auto-generated report per implementation
                             (e.g. ckeletin-go.yaml, ckeletin-rust.yaml)
research/                  — Source research behind requirements
principles.md              — Derives from the Manifesto
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

Derives from the [Manifesto](https://github.com/peiman/manifesto).
See [principles.md](principles.md) for how the manifesto applies to
CLI scaffold specifications.
