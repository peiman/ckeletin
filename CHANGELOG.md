# Changelog

All notable changes to the ckeletin specification.

Format: [Keep a Changelog](https://keepachangelog.com/)
Versioning: [Semantic Versioning](https://semver.org/)

## [Unreleased]

### Added

- changie integration for changelog management — enforces CKSPEC-CL requirements
- Taskfile changelog and release commands (task changelog:added, task release)

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
