import os
import pytest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SPEC_DIR = os.path.join(REPO_ROOT, "spec")
CONFORMANCE_DIR = os.path.join(REPO_ROOT, "conformance")
FIXTURES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fixtures")


@pytest.fixture
def spec_dir():
    return SPEC_DIR


@pytest.fixture
def conformance_dir():
    return CONFORMANCE_DIR


@pytest.fixture
def fixtures_dir():
    return FIXTURES_DIR
