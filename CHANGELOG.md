# Changelog

All notable changes to the ckeletin specification.

Format: [Keep a Changelog](https://keepachangelog.com/)
Versioning: [Semantic Versioning](https://semver.org/)

## [Unreleased]

### Added

- Conformance cycle requirements (CKSPEC-ENF-005 to 007) — mapping completeness, violation tests, automatic feedback signals
- enforcement_level field on conformance_entry schema — makes enforcement ladder visible in conformance data
- violation_test field on conformance_entry schema — links enforcement claims to proof
- violation_evidence field on conformance_entry schema — alternative proof for structural and tooling-enforced enforcement where violation tests are not feasible (must include file path)
- Output domain (CKSPEC-OUT-001 to 005) — 3-stream model, JSON mode, shadow logging, output isolation
- Agent Readiness domain (CKSPEC-AGENT-001 to 005) — AGENTS.md, provider guides, CLI as agent interface
- changie integration for changelog management — enforces CKSPEC-CL requirements
- Taskfile changelog and release commands (task changelog:added, task release)
- Research document: violation-evidence-proposal.md — joint proposal from ckeletin-go and ckeletin-rust with revision history

### Changed

- CKSPEC-ENF-006: accepts violation_evidence as alternative to violation_test for structural and tooling-enforced enforcement; narrowed from four categories to two after ckeletin-go proved self-referential case was testable
- CKSPEC-ARCH-004: added notes clarifying serialization annotations are permitted on business logic types
- CKSPEC-ENF-002: added notes on language-varying enforcement levels
- Clarified checkable field in schema — captures whether a requirement CAN be checked, not how strongly
- Principles restructured — derives from [Manifesto](https://github.com/peiman/manifesto)
- Added Curiosity Over Certainty, Good Will, Partnership to principles
- Folded Framework Independence into Separation of Concerns
- Folded Two-Implementation Rule into Feedback Cycle
- Principles organized into tiers: Foundation → Method → Design → Process
- Changelog domain reordered from 04 to 06 (nothing depends on it)
- Spec domains now follow platform dependency chain

## [0.1.2] - 2026-04-13

### Added
- Changelog domain (CKSPEC-CL-001 to 007) — Keep a Changelog, SemVer,
  ISO 8601, Unreleased section, human curation, comparison links
- Research directory with changelog best practices source material
- ckeletin-go conformance for changelog requirements (7/7 met)

## [0.1.1] - 2026-04-13

### Added
- Principle 9: Single Source of Truth (SSOT)
- Spec validation script (scripts/validate_spec.py) — TDD, 23 tests
- 7 failure fixture files for validation testing
- Taskfile with venv-based task check / task test / task setup
- Numbered spec files to encode reading order (01-, 02-, 03-)

### Changed
- Removed Go-specific implementation details from spec YAML notes
  (implementation details belong in conformance reports, not the spec)

## [0.1.0] - 2026-04-12

### Added
- Requirement format schema (spec/_schema.yaml)
- Principles document (8 principles)
- Architecture domain (CKSPEC-ARCH-001 to 007)
- Enforcement domain (CKSPEC-ENF-001 to 004)
- Testing domain (CKSPEC-TEST-001 to 004)
- ckeletin-go conformance report (15 requirements verified)

### Notes
- Lean start: 3 core domains. More added when ckeletin-rust needs them.
- No gate zero yet — deferred until second implementation exists.

[Unreleased]: https://github.com/peiman/ckeletin/compare/v0.1.2...HEAD
[0.1.2]: https://github.com/peiman/ckeletin/compare/v0.1.1...v0.1.2
[0.1.1]: https://github.com/peiman/ckeletin/compare/v0.1.0...v0.1.1
[0.1.0]: https://github.com/peiman/ckeletin/releases/tag/v0.1.0
