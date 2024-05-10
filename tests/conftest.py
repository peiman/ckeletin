# conftest.py
import pytest
from mycliapp.config import settings
from copy import deepcopy, copy
import logging

@pytest.fixture(autouse=True)
def mock_settings(monkeypatch):
    original_settings = {}
    mock_values = {
        'app_name': 'TestApp',
        'admin_email': 'test@example.com'
    }

    # Backup and monkeypatch settings
    for key, value in mock_values.items():
        original_value = getattr(settings, key, None)
        original_settings[key] = original_value
        monkeypatch.setattr(settings, key, value)

    # Yield a dictionary for testing
    yield mock_values

    # Restore original settings after the test
    for key, original_value in original_settings.items():
        if original_value is not None:
            try:
                setattr(settings, key, original_value)
            except Exception as e:
                logging.error(f"Could not restore {key}: {e}")
