# Ckeletin Principles

These principles ground every requirement in the specification.
When a requirement seems arbitrary, trace it back here.

## Conformance Language

This specification uses RFC 2119 keywords: MUST, MUST NOT, SHOULD,
SHOULD NOT, MAY. These words carry normative weight only when
written in ALL CAPS, per RFC 8174.

## Principles

### 1. Truth-Seeking

Observe, trace, verify. Every conclusion rests on evidence.
When something breaks, read the source, trace the signal path,
extract the real cause. Assumptions compound into architectural
drift — evidence prevents it.

### 2. Automated Enforcement

Rules that aren't enforced erode. Every architectural decision
that CAN be checked by a tool MUST be. The enforcement ladder
provides a hierarchy: compile-time, linter, SAST, validator
script, CI, honor system. Prefer higher levels — they catch
violations earlier and cost less to maintain.

### 3. Lean Iteration

Don't design the perfect system on paper. Build the smallest
thing that produces real data. Run it. Observe what actually
happens. Learn. Iterate. Reality is the specification.

### 4. Platforms, Not Features

Each piece of architecture is a platform for the next. Build
heavy enough to support what comes after, and clean enough that
nothing rots underneath. Skip a step and the structure is hollow.

### 5. Separation of Concerns

Structure (WHAT) and decisions (WHY) live in different places.
Universal project knowledge and LLM-specific rules live in
different files. Framework code and project code live in
different directories. Each separation prevents a specific
kind of drift.

### 6. Framework Independence

Business logic MUST NOT depend on CLI frameworks, configuration
libraries, or other infrastructure. This ensures testability,
portability, and the ability to swap infrastructure without
rewriting business logic.

### 7. Feedback Cycle

The specification and its implementations learn from each other.
Implementations that discover better approaches feed back to
the spec. Conformance reports are retrospectives, not audits.
The spec evolves through evidence from real projects, not
top-down mandates.

### 8. Two-Implementation Rule

A requirement isn't proven until at least two implementations
can satisfy it. If only one can meet it, the requirement may
be too language-specific. If both struggle, it needs revision.

### 9. Single Source of Truth

Every piece of information has ONE authoritative location.
Duplication drifts — when the same fact lives in two places,
they inevitably diverge, and neither can be trusted. When
you need information in a second place, reference the source
rather than copying it. Configuration keys come from a
registry, not hardcoded strings. Architecture descriptions
link to decisions, not restate them. The spec defines
requirements; conformance reports describe implementation
details. Never both.
