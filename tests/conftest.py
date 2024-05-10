import pytest
from mycliapp.config import settings

@pytest.fixture
def mock_settings(monkeypatch):
    monkeypatch.setattr(settings, 'app_name', 'TestApp')
    return settings
