# Contributing — the spec feedback cycle

> "This is not a top-down mandate. The specification and its implementations
> learn from each other — conformance reports are retrospectives, not audits."
> — the README

This file makes that promise concrete: a defined, followable process for how a
report against the spec is handled — by a human **or** an agent — so nothing is
silently dropped and the spec and its implementations keep reshaping each other.

## How feedback flows

Anyone — an implementation (`ckeletin-rust`, `ckeletin-go`), a downstream
consumer (e.g. [muster](https://github.com/peiman/muster)), an agent, or a
person — who hits friction with the spec reports it. Each report runs:

```
intake -> triage -> DECIDE -> implement -> verify
                      |
                      +-- UPDATE   the spec   (bump the version, regenerate, note it in CHANGELOG)
                      +-- DISCUSS  with the reporter (clarify / push back, then re-triage)
                      +-- REJECT   with a written reason (out of scope != silently ignored)
```

1. **Intake** — record the report in a feedback register: one entry of
   `{id, reporter, spec_rule, summary, status, decision, rationale}`.
2. **Triage** — real gap, misunderstanding, or out of scope?
3. **Decide** — `update` / `discuss` / `reject` (the branch above).
4. **Implement** (if `update`) — edit the spec YAML under `spec/`, bump
   `spec_version`, regenerate `spec/requirements.json` (`task generate:requirements`), and record the change in `CHANGELOG.md`.
5. **Verify** — every implementation re-runs conformance against the new spec.
   The loop only closes when the consumers stay green.

The verify step is the teeth: a spec change that **breaks an implementation**
must show up — it is the implementation pushing back on the spec. That is the
whole point ("not master-slave, a learning system").

## Enforcement (shipped here)

This repo ships the register (`feedback/register.json`) and a zero-dependency CI
gate (`scripts/check_feedback.py`, run by `task feedback:check` and on every PR
via the spec-check workflow). It fails if any report is untriaged or undecided,
or if any implementation no longer conforms to the **current** spec version —
read from the real `conformance/*.yaml` aggregates. The source of truth is the
register plus those conformance reports; no external tools are required.
The consumer-conformance gate is intentionally strict — the spec's CI stays red until every implementation re-conforms, so the spec never quietly advances past its implementations.

A portable, language-agnostic reference of the same cycle (a shell `ci-check.sh`
plus a `muster` setup) lives in the muster example:

> https://github.com/peiman/muster/tree/main/examples/ckeletin-feedback

For a living process-map and an honest, agent-drivable readiness view on top,
install muster (the same example doubles as its definition):

```sh
# OPTIONAL — muster is the live view, never a prerequisite for contributing.
cargo install --git https://github.com/peiman/muster muster   # or: muster README -> Install
muster readiness                          # text
muster readiness --output json | jq .     # an agent reads the gaps and acts
```

An agent and a human follow the identical flow: the agent/human does the
triage + decision + implementation; the register (and muster, if used) is the
honest scoreboard that can't drift, because it reads the real sources on every
read instead of trusting a stored copy.

## Writing a check

When you add a gate or validator (like `scripts/check_feedback.py`), its tests
must cover the **adversarial-input matrix**, not just the happy path:

- malformed input (bad JSON/YAML, truncated), missing input (absent file/key),
  wrong-type input (a scalar where a mapping is expected), and empty/null;
- **the false-pass** — does it stay green when it should go red? For a gate this
  is the load-bearing test: a gate that can't go red is worthless (an empty
  conformance report must NOT read "all met");
- **clean failure** — every bad input emits the check's own diagnostic and a
  non-zero exit, never a raw traceback.

`scripts/check_feedback.py` + `tests/test_check_feedback.py` are the worked
example: every failure mode is tested, and the gate is self-sufficient — it
cross-checks the spec's own requirement IDs rather than trusting an upstream step.
