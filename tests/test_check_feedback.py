"""Tests for the spec-feedback-cycle CI gate (scripts/check_feedback.py).

Covers the happy path AND every failure/malformed-input mode — a per-PR CI gate
must catch real breaks and fail cleanly, never crash or false-pass.
"""
import importlib.util
import json
import pathlib

import pytest

_spec = importlib.util.spec_from_file_location(
    "check_feedback",
    pathlib.Path(__file__).resolve().parent.parent / "scripts" / "check_feedback.py",
)
cf = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(cf)

SPEC_IDS = ["CKSPEC-A", "CKSPEC-B"]


def _item(**over):
    base = dict(id="FB-1", reporter="r", spec_rule="CKSPEC-A",
               summary="s", status="accepted", decision="update", rationale=None)
    base.update(over)
    return base


def _register(tmp_path, items, raw=None):
    p = tmp_path / "register.json"
    p.write_text(raw if raw is not None else json.dumps({"items": items}))
    return p


def _requirements(tmp_path, version="0.8.0", ids=SPEC_IDS):
    p = tmp_path / "requirements.json"
    p.write_text(json.dumps({"spec_version": version,
                             "requirements": [{"id": i} for i in ids]}))
    return p


def _conformance(tmp_path, name="impl-a", spec_version="0.8.0",
                 statuses=None, raw=None):
    d = tmp_path / "conformance"
    d.mkdir(exist_ok=True)
    if raw is not None:
        (d / f"{name}.yaml").write_text(raw)
        return d
    statuses = statuses or {i: "met" for i in SPEC_IDS}
    body = "".join(f"  {r}: {{status: {s}}}\n" for r, s in statuses.items())
    (d / f"{name}.yaml").write_text(
        f"implementation: {name}\nspec_version: {spec_version}\nrequirements:\n{body}")
    return d


# ---- register: happy + every failure mode ----
def test_empty_register_passes(tmp_path):
    assert cf.check_register(_register(tmp_path, [])) == 0


def test_full_report_passes(tmp_path):
    assert cf.check_register(_register(tmp_path, [_item()])) == 1


def test_open_report_fails(tmp_path):
    with pytest.raises(SystemExit):
        cf.check_register(_register(tmp_path, [_item(status="open", decision=None)]))


def test_undecided_report_fails(tmp_path):
    with pytest.raises(SystemExit):
        cf.check_register(_register(tmp_path, [_item(status="accepted", decision=None)]))


def test_invalid_decision_token_fails(tmp_path):
    # the review's "banana" hole
    with pytest.raises(SystemExit):
        cf.check_register(_register(tmp_path, [_item(decision="banana")]))


def test_rejected_status_without_rationale_fails(tmp_path):
    # the review's "decision: rejected matching the status name" hole — rationale
    # is keyed on the STATE, and `rejected` is not a valid decision token either
    with pytest.raises(SystemExit):
        cf.check_register(_register(tmp_path, [_item(status="rejected", decision="reject")]))


def test_rejected_with_rationale_passes(tmp_path):
    assert cf.check_register(_register(
        tmp_path, [_item(status="rejected", decision="reject", rationale="out of scope")])) == 1


def test_missing_required_field_fails(tmp_path):
    with pytest.raises(SystemExit):
        cf.check_register(_register(tmp_path, [_item(reporter="")]))


def test_non_dict_item_fails(tmp_path):
    with pytest.raises(SystemExit):
        cf.check_register(_register(tmp_path, ["not-an-object"]))


def test_invalid_status_fails(tmp_path):
    with pytest.raises(SystemExit):
        cf.check_register(_register(tmp_path, [_item(status="wibble")]))


def test_malformed_register_json_fails_cleanly(tmp_path):
    with pytest.raises(SystemExit):
        cf.check_register(_register(tmp_path, None, raw="{not json"))


def test_missing_register_file_fails_cleanly(tmp_path):
    with pytest.raises(SystemExit):
        cf.check_register(tmp_path / "does-not-exist.json")


# ---- consumers: happy + the false-pass blocker + drift + malformed ----
def test_consumers_all_met_passes(tmp_path):
    cf.check_consumers(_conformance(tmp_path), _requirements(tmp_path))


def test_unmet_consumer_fails(tmp_path):
    conf = _conformance(tmp_path, statuses={"CKSPEC-A": "met", "CKSPEC-B": "unmet"})
    with pytest.raises(SystemExit):
        cf.check_consumers(conf, _requirements(tmp_path))


def test_version_drift_fails(tmp_path):
    conf = _conformance(tmp_path, spec_version="0.7.0")
    with pytest.raises(SystemExit):
        cf.check_consumers(conf, _requirements(tmp_path))


def test_missing_requirements_key_false_pass_is_caught(tmp_path):
    # THE blocker: a report with no requirements table must FAIL, not read green
    conf = _conformance(tmp_path, raw="implementation: x\nspec_version: 0.8.0\n")
    with pytest.raises(SystemExit):
        cf.check_consumers(conf, _requirements(tmp_path))


def test_report_missing_a_spec_requirement_fails(tmp_path):
    # report covers only CKSPEC-A; spec needs A + B -> missing B
    conf = _conformance(tmp_path, statuses={"CKSPEC-A": "met"})
    with pytest.raises(SystemExit):
        cf.check_consumers(conf, _requirements(tmp_path))


def test_scalar_requirement_value_fails_cleanly(tmp_path):
    # a malformed report whose requirement is a bare scalar (not a {status:...}
    # mapping) must FAIL cleanly, not crash with a traceback
    conf = _conformance(
        tmp_path,
        raw="implementation: x\nspec_version: 0.8.0\nrequirements:\n  CKSPEC-A: met\n  CKSPEC-B: met\n",
    )
    with pytest.raises(SystemExit):
        cf.check_consumers(conf, _requirements(tmp_path))


def test_empty_yaml_report_fails(tmp_path):
    conf = _conformance(tmp_path, raw="")
    with pytest.raises(SystemExit):
        cf.check_consumers(conf, _requirements(tmp_path))


def test_no_reports_fails(tmp_path):
    (tmp_path / "conformance").mkdir()
    with pytest.raises(SystemExit):
        cf.check_consumers(tmp_path / "conformance", _requirements(tmp_path))


def test_requirements_without_spec_version_fails_cleanly(tmp_path):
    p = tmp_path / "requirements.json"
    p.write_text(json.dumps({"requirements": [{"id": "CKSPEC-A"}]}))
    with pytest.raises(SystemExit):
        cf.check_consumers(_conformance(tmp_path), p)


# ---- main() end-to-end ----
def test_main_passes_on_clean_state(tmp_path):
    cf.main(_register(tmp_path, []), _conformance(tmp_path), _requirements(tmp_path))


def test_main_fails_on_broken_consumer(tmp_path):
    conf = _conformance(tmp_path, statuses={"CKSPEC-A": "unmet", "CKSPEC-B": "met"})
    with pytest.raises(SystemExit):
        cf.main(_register(tmp_path, []), conf, _requirements(tmp_path))
