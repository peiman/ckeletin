# Changelog

All notable changes to the ckeletin specification.

Format: [Keep a Changelog](https://keepachangelog.com/)
Versioning: [Semantic Versioning](https://semver.org/)

## [Unreleased]

## [0.12.0] - 2026-10-16

### Added

- CKSPEC-UPD-001: a derived project, during its ordinary quality gate, is told when the upstream framework version is a newer semantic version than its own. The notice does not fail the build, does not run in continuous integration, can be turned off, and does not fail offline or without an upstream remote. The upstream repository is exempt. The comparison is the framework version, not a commit count and not the application version.
- CKSPEC-UPD-002: one command replaces only the framework tree. It accepts an explicit upstream ref, defaults to the upstream default branch, has a dry run and a compatibility check that discards its result, and reports the framework version before and after. A git tag is only a pin.
- CKSPEC-UPD-003: the check and the update result are machine-readable, so an agent can poll and apply an update without scraping prose.

## [0.11.0] - 2026-06-27

### Changed

- CKSPEC-ENF-008: an anchor on a met claim must resolve. The file must exist and the symbol must be present. A generator must fail on a dangling anchor.
- CKSPEC-AGENT-002: the reference check is a provider-name grep with cross-references excluded. The residual gap is why this stays `verification: partial`.
- CKSPEC-OUT-002: completion scripts, man pages, and dev-only commands may skip JSON mode only when the exemption is declared.
- CKSPEC-OUT-003: the error field should be a structured object with `code` and `message`. The total schema still applies.
- CKSPEC-OUT-004: an audit-stream init failure is a returned error, not a panic. The writer stays alive through error rendering, and a shadow event is not recorded before the write. Generated artifacts may log metadata (type, destination, size, hash) instead of full content when the bytes are reproducible from versioned inputs.

## [0.10.0] - 2026-06-26

### Added

- CKSPEC-ENF-011: a tool that walks the tree must stay inside the project's own sources. It must not descend into a nested checkout, and it must not pass or fail because of one.

### Changed

- The boolean `checkable` field is replaced by `verification`: `automated`, `partial`, or `manual`. Manual covers a human judgment or an analytical argument.
- CKSPEC-ENF-002: the enforcement ladder adds `structural` and retires the overloaded `design` level. The ladder and the schema enum are the same list.
- CKSPEC-OUT-002: flag over config is the blessed precedence.
- CKSPEC-ARCH-004: a module boundary the compiler cannot see is not compile-time enforcement. The conformance report must say so.

## [0.9.0] - 2026-06-25

### Added

- CKSPEC-AGENT-007: a scaffold must not present the reference implementation's files as the derived project's own. Ownership is framework-owned, consumer-owned, generated evidence, or upstream-only.

### Changed

- CKSPEC-ENF-009: a conformance gate must name its subject. A no-op must not count as a pass.
- CKSPEC-OUT-003: the JSON envelope is a total schema. Absent values are null, not omitted keys.
- CKSPEC-OUT-002: argument-parser errors emitted before the command is resolved may follow the CLI framework's own convention. The envelope is required from configuration load onward. The same requirement recommends `--output text|json`.
- CKSPEC-ARCH-001: a layer may be empty or absent. The conformance report says which layers are populated.
- The word "audit" in the README means the CKSPEC-ENF-004 table. Conformance reports are evidence retrospectives.
- Spec validation is derived from the schema. `enforcement_level` is enforced, and principle citations are checked.

## [0.8.0] - 2026-06-05

### Added

- CKSPEC-AGENT-006: a machine-readable command catalog, so an agent can discover commands without parsing help text.
- Scheduled conformance refresh. A daily job compares each implementation's published `conformance-report.json` with the committed snapshot, ignoring `report_date`, and opens a pull request when the content has drifted. The spec repository polls. Implementations do not need a cross-repo token.

## [0.7.0] - 2026-06-04

### Added

- CKSPEC-ENF-010: a published machine-readable conformance report. The spec aggregates those reports instead of hand-authoring the snapshots.

## [0.6.0] - 2026-06-04

### Added

- CKSPEC-ENF-008: every met claim must be anchored to an automated check or to an analysis entry that names its evidence.
- CKSPEC-ENF-009: conformance is verified continuously, and a release is gated on that verification.

## [0.5.0] - 2026-06-03

### Added

- CKSPEC-OUT-006: version output must surface version, commit, date, and dirty state. A field that is unavailable degrades to `unknown`.

## [0.4.0] - 2026-04-14

### Added

- `spec/requirements.json`, generated from the spec YAML. `task check` regenerates it in memory and fails if the committed file has drifted.
- `violation_evidence` on a conformance entry, for structural and tooling-enforced claims where a violation test is not feasible. The entry must name a file.

### Changed

- CKSPEC-ENF-006: `violation_evidence` is an alternative to `violation_test` for structural and tooling-enforced enforcement only. The wider set of categories was narrowed after ckeletin-go showed the self-referential case could be tested.

## [0.3.0] - 2026-04-13

### Added

- CKSPEC-ENF-005 to CKSPEC-ENF-007: mapping completeness, violation tests for enforcement claims, and automatic feedback when a checkable requirement has no signal.
- `enforcement_level` and `violation_test` on a conformance entry, so the enforcement ladder and its proof are visible in the report.

### Changed

- CKSPEC-ARCH-004: serialization annotations from the language's usual framework are allowed on business-logic types. They describe data. They are not an import of the infrastructure layer.

## [0.2.0] - 2026-04-13

### Added

- Output domain (CKSPEC-OUT-001 to CKSPEC-OUT-005): three streams, JSON mode, shadow logging, and output kept out of business logic.
- Agent Readiness domain (CKSPEC-AGENT-001 to CKSPEC-AGENT-005): a universal agent guide, provider guides, and the CLI as the agent interface.

### Changed

- Principles now derive from the [Manifesto](https://github.com/peiman/manifesto). Curiosity Over Certainty, Good Will, and Partnership are included. Framework Independence is folded into Separation of Concerns. The Two-Implementation Rule is folded into the Feedback Cycle. The tiers are Foundation, Method, Design, and Process.
- The changelog domain moved from `04` to `06`. Spec domains follow the platform dependency chain.

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

[Unreleased]: https://github.com/peiman/ckeletin/compare/8d06a2384850322906e03b5cc9d4bf81797bc499...HEAD
[0.12.0]: https://github.com/peiman/ckeletin/compare/b063c5fc65db5d18172c91881a9642bc349a3317...8d06a2384850322906e03b5cc9d4bf81797bc499
[0.11.0]: https://github.com/peiman/ckeletin/compare/940a335f40005972b1120a5f144a35ab1926887d...b063c5fc65db5d18172c91881a9642bc349a3317
[0.10.0]: https://github.com/peiman/ckeletin/compare/cf645df4f75e3f7778dcc23f982b9a0e64b55630...940a335f40005972b1120a5f144a35ab1926887d
[0.9.0]: https://github.com/peiman/ckeletin/compare/33078a6754f0ad8bc3ac13b65204420601f11e58...cf645df4f75e3f7778dcc23f982b9a0e64b55630
[0.8.0]: https://github.com/peiman/ckeletin/compare/c1a25674af3cb4d389b65581c946b156fc25eb2a...33078a6754f0ad8bc3ac13b65204420601f11e58
[0.7.0]: https://github.com/peiman/ckeletin/compare/d8188e39f86aa4ccd134c22d5df4de30076afe4f...c1a25674af3cb4d389b65581c946b156fc25eb2a
[0.6.0]: https://github.com/peiman/ckeletin/compare/b3184b4a6a2107b37e30b31de3046615080dd9f9...d8188e39f86aa4ccd134c22d5df4de30076afe4f
[0.5.0]: https://github.com/peiman/ckeletin/compare/b0e1cc39fbd7edadf177e4451ae37ae1550c222f...b3184b4a6a2107b37e30b31de3046615080dd9f9
[0.4.0]: https://github.com/peiman/ckeletin/compare/74ddb050250010797806b12e333da55ecbe4257e...b0e1cc39fbd7edadf177e4451ae37ae1550c222f
[0.3.0]: https://github.com/peiman/ckeletin/compare/v0.2.0...74ddb050250010797806b12e333da55ecbe4257e
[0.2.0]: https://github.com/peiman/ckeletin/compare/v0.1.2...v0.2.0
[0.1.2]: https://github.com/peiman/ckeletin/compare/v0.1.1...v0.1.2
[0.1.1]: https://github.com/peiman/ckeletin/compare/v0.1.0...v0.1.1
[0.1.0]: https://github.com/peiman/ckeletin/releases/tag/v0.1.0
