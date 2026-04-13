# Ckeletin Principles

These principles ground every requirement in the specification.
When a requirement seems arbitrary, trace it back here.

They derive from the [Manifesto](https://github.com/peiman/manifesto)
— shared philosophical foundations for all projects. This document
applies the manifesto to the domain of CLI scaffold specifications.

## Conformance Language

This specification uses RFC 2119 keywords: MUST, MUST NOT, SHOULD,
SHOULD NOT, MAY. These words carry normative weight only when
written in ALL CAPS, per RFC 8174.

## Philosophical Foundation

These come directly from the manifesto. They are why we build.

### 1. Truth-Seeking

Observe, trace, verify. Every conclusion rests on evidence.
Assumptions compound into architectural drift — evidence prevents
it. When something breaks, find the actual mechanism, not the
probable cause.

### 2. Curiosity Over Certainty

When something fails, it's not a problem to fix — it's a signal
to understand. An approach that fails repeatedly isn't wasted
work — it's learning that the approach is fundamentally wrong.
Don't rush to fix. Rush to understand.

### 3. Good Will

Capabilities are accelerating but infrastructure is fragile.
Every specification, every test, every enforcement mechanism
makes the foundation more trustworthy. The bad must not outgrow
the good. Build anchors.

## Method

These are how we approach the work.

### 4. Lean Iteration

Don't design the perfect system on paper. Build the smallest
thing that produces real data. Run it. Observe what actually
happens. Learn. Iterate. Reality is the specification.

### 5. Platforms, Not Features

Each step is a platform for the next. Build heavy enough to
support what comes after, and clean enough that nothing rots
underneath. The order matters — skip a step and the structure
is hollow.

### 6. Partnership

Built by a team of different minds — each with their own nature.
Partnership means holding each other to a high standard because
the standard is reachable and the work deserves it. The
specification and its implementations are partners — conformance
reports are retrospectives, not audits.

## Design

These are how we organize.

### 7. Single Source of Truth

Every piece of information has one authoritative location.
Duplication drifts. Reference the source rather than copying it.
The spec defines requirements; conformance reports describe
implementation details. Never both.

### 8. Separation of Concerns

Different responsibilities live in different places. Structure
and decisions. Knowledge and behavior. Framework and application.
Business logic and CLI framework. Each separation prevents a
specific kind of drift.

## Process

These are how we enforce and evolve.

### 9. Automated Enforcement

Rules that aren't enforced erode. Every decision that can be
checked by a tool must be. Prefer mechanisms that catch
violations early: compile-time over linting, linting over
scripts, scripts over CI, CI over honor system.

### 10. Feedback Cycle

The specification and its implementations learn from each other.
A specification is a hypothesis — implementations test it. When
they discover better approaches, the specification evolves. A
requirement isn't proven until at least two implementations can
satisfy it.
