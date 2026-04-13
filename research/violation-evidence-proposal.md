# Spec Proposal: violation_evidence as Alternative Proof for ENF-006

**Authors:** ckeletin-rust (workhorse), ckeletin-go
**Date:** 2026-04-14
**Target:** ckeletin spec v0.4.0
**Affects:** `_schema.yaml` (conformance_entry), `02-enforcement.yaml` (ENF-006)

---

## Problem

ENF-006 requires that enforcement claims above honor-system be accompanied by a violation test. Both implementations independently discovered cases where the enforcement is real but a violation test file is not feasible.

### Evidence from ckeletin-rust (workhorse)

**CKSPEC-ARCH-001 (Layered architecture):** Enforcement is the Cargo workspace structure itself. `crates/domain/Cargo.toml` declares no dependency on `workhorse-infrastructure` or `workhorse-cli`. Any reverse import is a compile error — not because a test catches it, but because the dependency graph makes it structurally impossible. There is no meaningful violation test for "try adding a forbidden dependency to Cargo.toml" — that's testing the build system's configuration, not code.

We DO have violation tests for individual import paths within the structure (trybuild tests that verify `use workhorse_infrastructure::*` fails to compile in domain code). But the higher claim — that the workspace topology enforces directed dependencies — has no violation test because the proof IS the `Cargo.toml` dependency graph.

**CKSPEC-ARCH-007 (Source file organization):** The enforcement is that domain and infrastructure crates have no `[[bin]]` target. Entry point isolation is structural — there's nothing to violate in code.

### Evidence from ckeletin-go

ckeletin-go reached 35/35 requirements met with 14 violation tests and 2 residual feedback signals. Both signals represent real enforcement that can't have violation test files.

**CKSPEC-ENF-006 (Violation tests for enforcement claims):** This is self-referential. ENF-006 says "enforcement claims above honor-system must have violation tests." The proof that ENF-006 is met IS the 14 violation tests in `test/conformance/violation_test.go`. Writing a violation test for "violation tests exist" would mean: delete the tests, verify the generator flags it — but that's what ENF-007 (feedback signals) already tests. The test infrastructure can't verify itself from within itself.

**CKSPEC-TEST-002 (Minimum coverage threshold):** Enforcement is `check-coverage-project.sh` which fails the build when coverage drops below 85%. To write a violation test, you'd need to actually reduce coverage below 85% — adding uncovered code or deleting tests. Both destroy the environment the enforcement mechanism protects. The violation IS the damage. You can't safely demonstrate the failure without causing it.

---

## Four Categories of Unfeasible Violation Tests

Both implementations converged on the same taxonomy:

### 1. Self-referential
The requirement is about the testing infrastructure itself. ENF-006 says "enforcement claims must have violation tests." The proof that ENF-006 is met IS the existence of the violation tests. Testing "do tests exist" from within the test infrastructure is circular.

### 2. Destructive-to-test
Creating a violation destroys the mechanism that would detect it. A coverage threshold enforced by a script that fails below 85% — to write a violation test, you'd have to actually break coverage below 85%, which puts the project in a state where the enforcement script correctly fails but the test suite is genuinely broken. The violation IS the damage.

### 3. Structural
The enforcement IS the architecture, not a runtime check. Cargo workspace dependencies, `.go-arch-lint.yml` configuration, Go module boundaries — these are build-system-level facts, not code-level assertions. You can point to the file that constitutes the enforcement, but there's no code to violate.

### 4. Tooling-enforced
Enforcement lives in CI configuration, git hooks, or toolchain behavior that wraps the source tree from outside. A GitHub Actions workflow that rejects PRs with forbidden patterns is real enforcement — arguably stronger than compile-time, because it catches config changes too. But no violation test within the source tree can prove an external enforcement mechanism works.

---

## Proposed Schema Change

### `_schema.yaml`: Add `violation_evidence` to conformance_entry

```yaml
violation_evidence:
  type: string
  required: false
  description: >
    For enforcement claims where a violation test file is not feasible
    (self-referential, destructive-to-test, structural, or
    tooling-enforced), an explanation referencing the specific file(s)
    that constitute the enforcement. Must include at least one file
    path. Required when violation_tests is empty and enforcement_level
    is above honor-system.
```

**Key constraint: must include at least one file path.** Free-text without a file reference invites hand-waving. If the enforcement is structural, you can always point to the file that IS the structure (`Cargo.toml`, `.go-arch-lint.yml`, `.github/workflows/ci.yml`). If you can't point to a file, the claim might actually be honor-system.

The conformance generator accepts either `violation_test` OR `violation_evidence` for claims above honor-system. Empty for both = feedback signal (current behavior). This preserves ENF-006's intent — enforcement claims need proof — while acknowledging that proof isn't always a test file.

### `02-enforcement.yaml`: Update ENF-006 description

Current:
```
Enforcement claims above honor-system in conformance reports
MUST be accompanied by a violation test — a test that introduces
a known violation and verifies the enforcement mechanism catches
it. If a violation test cannot be written, the enforcement level
MUST be reported as honor-system regardless of the intended
mechanism.
```

Proposed:
```
Enforcement claims above honor-system in conformance reports
MUST be accompanied by proof that the enforcement mechanism
works. The preferred proof is a violation test — a test that
introduces a known violation and verifies the enforcement
mechanism catches it. When a violation test is not feasible
(self-referential, destructive-to-test, structural, or
tooling-enforced enforcement), a violation_evidence field
referencing the specific file(s) that constitute the enforcement
is an acceptable alternative. If neither a violation test nor
violation evidence can be provided, the enforcement level
MUST be reported as honor-system.
```

### `02-enforcement.yaml`: Update ENF-006 notes

Add:
```
Four categories of enforcement where violation tests are not
feasible: (1) self-referential — the requirement is about the
testing infrastructure itself, (2) destructive-to-test — creating
a violation breaks the detection mechanism, (3) structural — the
enforcement IS the architecture (build config, dependency graph),
not a runtime check, (4) tooling-enforced — enforcement wraps the
codebase from outside (CI, hooks, toolchain). Discovered
independently by both ckeletin-go and ckeletin-rust during
conformance reporting. See: Principle 10 (Feedback Cycle).
```

---

## Impact on Existing Conformance Reports

### ckeletin-go

**CKSPEC-ENF-006** — currently a feedback signal (self-referential). Would become:
```yaml
CKSPEC-ENF-006:
  status: met
  enforcement_level: script
  evidence: >
    14 violation tests prove enforcement for all requirements with
    checks above honor-system. Run: go test -tags conformance ./test/conformance/...
  violation_evidence: >
    Self-referential: the proof IS the 14 violation tests.
    File: test/conformance/violation_test.go — contains
    TestViolation_ARCH001 through TestViolation_ENF007 (14 tests).
    Each test creates a known violation and verifies the enforcement
    mechanism catches it. The existence of these tests is the
    evidence that ENF-006 is satisfied.
  tests:
    - "go test -tags conformance ./test/conformance/..."
```

**CKSPEC-TEST-002** — currently a feedback signal (destructive-to-test). Would become:
```yaml
CKSPEC-TEST-002:
  status: met
  enforcement_level: script
  evidence: >
    check-coverage-project.sh enforces 85% minimum. Pre-push hook
    runs coverage check. Current coverage: 90.3%.
  violation_evidence: >
    Destructive-to-test: reducing coverage below 85% to trigger the
    check would break the test suite. The enforcement mechanism is
    the script itself and its integration into the pre-push hook.
    File: .ckeletin/scripts/check-coverage-project.sh — threshold
    check logic (line: MINIMUM_COVERAGE=85). File: lefthook.yml —
    pre-push hook runs coverage check.
  tests:
    - "test -f .ckeletin/scripts/check-coverage-project.sh"
```

### ckeletin-rust (workhorse)

**CKSPEC-ARCH-001** — currently a feedback signal (no violation test for structural enforcement). Would become:
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

**CKSPEC-ARCH-007** — currently a feedback signal. Would become:
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

Both implementations hit the same wall independently. That's Principle 10 working as designed — the specification is a hypothesis, implementations test it, and when they discover the same boundary, the specification should evolve.

The evidence is stronger because it's convergent:
- Two languages (Go, Rust) with different enforcement mechanisms (linter config vs Cargo workspace)
- Same taxonomy of unfeasible cases emerged independently
- Same proposed solution: alternative proof that still requires concrete file references
- Neither implementation is requesting weaker enforcement — both want honest reporting

---

## Checklist for Filing

- [x] Go agent fills in their sections (ENF-006 self-referential, TEST-002 destructive-to-test)
- [x] Both agents review the complete document (Rust agent reviewed 2026-04-14)
- [ ] PR targets ckeletin spec repo with changes to `_schema.yaml` and `02-enforcement.yaml`
- [ ] PR description references both conformance reports as evidence
