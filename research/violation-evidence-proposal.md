# Spec Proposal: violation_evidence as Alternative Proof for ENF-006

**Authors:** ckeletin-rust (workhorse), ckeletin-go
**Date:** 2026-04-14
**Updated:** 2026-04-14 — narrowed scope after ckeletin-go proved ENF-006 is testable
**Target:** ckeletin spec v0.4.0
**Affects:** `_schema.yaml` (conformance_entry), `02-enforcement.yaml` (ENF-006)

---

## Problem

ENF-006 requires that enforcement claims above honor-system be accompanied by a violation test. Both implementations independently discovered cases where the enforcement is real but a violation test file is not feasible.

### What survived scrutiny

**Structural enforcement (ckeletin-rust):** ARCH-001 and ARCH-007 enforcement is the Cargo workspace structure itself. `crates/domain/Cargo.toml` declares no dependency on `workhorse-infrastructure` — any reverse import is a compile error. Individual import violations ARE tested (trybuild), but the higher claim — that the dependency graph topology prevents violations — is structural. There is no test that "tries adding a dependency to Cargo.toml and watches it get rejected" because the build system WOULD accept it. The enforcement is the configuration being correct, not a tool catching incorrect configuration.

**Destructive-to-test (ckeletin-go):** TEST-002 coverage threshold enforcement. The script fails the build below 85%. Creating a violation test requires actually breaking coverage, destroying the environment the enforcement protects. Remains as a feedback signal — honestly untestable without a controlled fixture approach.

### What did NOT survive scrutiny

**Self-referential was wrong.** The ckeletin-go agent initially classified ENF-006 as self-referential ("the proof IS the 14 violation tests"). After being pushed to try harder, they wrote `TestViolation_ENF006_MissingViolationTestFlagged` — a test that verifies every requirement claiming linter/SAST enforcement has a corresponding violation test reference. On first run, it caught a real bug: ARCH-002's violation test reference was accidentally deleted during a mapping rewrite. The test doesn't test itself — it tests the mapping's consistency. ENF-006 was testable all along.

**Lesson:** "Self-referential" and "destructive-to-test" should default to "try harder first." The Go agent tried harder on ENF-006 and found a real test. Only after genuine effort fails should violation_evidence be considered.

---

## Revised Taxonomy: Two Categories, Not Four

### Accepted for violation_evidence

**1. Structural** — The enforcement IS the architecture, not a runtime check. Cargo workspace dependencies, Go module boundaries, build configuration. The absence of a declaration makes violations impossible. You can point to the file that constitutes the enforcement, but there's no code to violate and no tool that "catches" violations — the violations simply can't exist.

**2. Tooling-enforced** — Enforcement lives in CI configuration, git hooks, or toolchain behavior that wraps the source tree from outside. No violation test within the source tree can prove an external enforcement mechanism works.

### NOT accepted — try harder first

**Self-referential** — The ckeletin-go experience proved this category is usually a premature conclusion. If you think a requirement "tests itself," look for what the enforcement mechanism CHECKS, not what it IS. There's usually a consistency check hiding behind the apparent circularity.

**Destructive-to-test** — Some cases are genuine (TEST-002). But before claiming destruction, explore fixture-based approaches, isolated environments, or configuration-level tests that don't actually break the system. If genuinely infeasible after real effort, use a feedback signal rather than violation_evidence — this keeps the pressure to find a solution.

---

## Proposed Schema Change

### `_schema.yaml`: Add `violation_evidence` to conformance_entry

```yaml
violation_evidence:
  type: string
  required: false
  description: >
    For enforcement claims where a violation test file is not
    feasible (structural or tooling-enforced enforcement), an
    explanation referencing the specific file(s) that constitute
    the enforcement. Must include at least one file path. Accepted
    as alternative proof when violation_test is empty and
    enforcement_level is above honor-system. Not a substitute for
    trying harder — self-referential and destructive-to-test claims
    should attempt a violation test first.
```

**Key constraint: must include at least one file path.** If the enforcement is structural, you can always point to the file that IS the structure. If you can't point to a file, the claim is probably honor-system.

The conformance generator accepts either `violation_test` OR `violation_evidence` for claims above honor-system. Empty for both = feedback signal (current behavior).

### `02-enforcement.yaml`: Update ENF-006 description

Proposed:
```
Enforcement claims above honor-system in conformance reports
MUST be accompanied by proof that the enforcement mechanism
works. The preferred proof is a violation test — a test that
introduces a known violation and verifies the enforcement
mechanism catches it. When a violation test is not feasible
(structural or tooling-enforced enforcement), a
violation_evidence field referencing the specific file(s) that
constitute the enforcement is an acceptable alternative.
If neither a violation test nor violation evidence can be
provided, the enforcement level MUST be reported as
honor-system.
```

### `02-enforcement.yaml`: Update ENF-006 notes

Add:
```
Two categories of enforcement where violation tests are not
feasible: (1) structural — the enforcement IS the architecture
(build config, dependency graph), not a runtime check,
(2) tooling-enforced — enforcement wraps the codebase from
outside (CI, hooks, toolchain). Originally proposed with four
categories; self-referential and destructive-to-test were
narrowed after ckeletin-go proved ENF-006 (initially classified
as self-referential) was testable. The lesson: try harder before
reaching for violation_evidence. Discovered and refined through
cross-implementation feedback between ckeletin-go and
ckeletin-rust. See: Principle 10 (Feedback Cycle).
```

---

## Impact on Existing Conformance Reports

### ckeletin-go

**Score after revision:** 15 violation tests, 35/35 met, 1 feedback signal.

**CKSPEC-ENF-006** — NOW HAS A VIOLATION TEST. `TestViolation_ENF006_MissingViolationTestFlagged` verifies mapping consistency. No longer needs violation_evidence.

**CKSPEC-TEST-002** — remains a feedback signal. Genuinely destructive-to-test, but per the revised proposal, this stays as a feedback signal rather than using violation_evidence. Keeps the pressure to find a fixture-based solution.

### ckeletin-rust (workhorse)

**CKSPEC-ARCH-001** — structural enforcement. Would use violation_evidence:
```yaml
CKSPEC-ARCH-001:
  status: met
  enforcement_level: compile-time
  evidence: >
    Cargo workspace with separate crates. crates/domain/Cargo.toml
    declares no dependency on workhorse-infrastructure or workhorse-cli.
    Any reverse import is a compile error.
  violation_evidence: >
    Structural enforcement via Cargo workspace dependency graph.
    File: crates/domain/Cargo.toml (lines 8-14) — dependency list
    contains only serde. File: crates/infrastructure/Cargo.toml
    (lines 7-10) — no dependency on workhorse-domain or workhorse-cli.
    Additionally, individual import violations are tested via trybuild:
    crates/domain/tests/violations/domain_imports_infrastructure.rs.
  tests:
    - "cargo test -p workhorse-domain architecture_violations"
```

**CKSPEC-ARCH-007** — structural enforcement. Would use violation_evidence:
```yaml
CKSPEC-ARCH-007:
  status: met
  enforcement_level: compile-time
  evidence: >
    Only crates/cli/Cargo.toml has a [[bin]] target. Domain and
    infrastructure crates are library-only. Entry point isolation
    is structural.
  violation_evidence: >
    Structural enforcement via Cargo crate configuration.
    File: crates/cli/Cargo.toml (lines 7-9) — only [[bin]] target.
    File: crates/domain/Cargo.toml — no [[bin]] section.
    File: crates/infrastructure/Cargo.toml — no [[bin]] section.
```

---

## Why This Should Be a Joint PR

Both implementations hit the same wall independently. Then cross-implementation feedback made the proposal better — the Go agent tried harder on ENF-006 after the Rust agent's skepticism, and found it was testable. The proposal shrank from four categories to two. That's Principle 10 (Feedback Cycle) and Principle 6 (Partnership) working together.

---

## Checklist for Filing

- [x] Go agent fills in their sections
- [x] Both agents review the complete document
- [x] Revised after Go agent proved ENF-006 testable — narrowed from 4 to 2 categories
- [ ] PR updated with narrowed scope
- [ ] PR description references both conformance reports as evidence
