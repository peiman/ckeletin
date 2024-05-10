# test_commands.py
import pytest
from typer.testing import CliRunner
from unittest.mock import patch
from mycliapp.commands import app
from mycliapp.config import settings

runner = CliRunner()

# Test for echo command
def test_echo(mocker):
    mock_info = mocker.patch('mycliapp.commands.logger.info')
    result = runner.invoke(app, ["echo", "Hello"])
    assert result.exit_code == 0
    assert "Hello" in result.stdout
    mock_info.assert_called_with("Echoing: Hello")

# Test for ping command
def test_ping(mocker):
    mock_info = mocker.patch('mycliapp.commands.logger.info')
    result = runner.invoke(app, ["ping"])
    assert result.exit_code == 0
    assert "pong" in result.stdout
    mock_info.assert_called_with("Received ping command")

# Test for config command
@pytest.fixture(autouse=True)
def reset_settings():
    original_app_name = settings.app_name
    original_admin_email = settings.admin_email
    yield
    settings.app_name = original_app_name
    settings.admin_email = original_admin_email

@pytest.mark.usefixtures("mock_settings")
def test_config_get(mock_settings):
    for key, expected_value in mock_settings.items():
        result = runner.invoke(app, ["config", "--key", key])
        assert result.exit_code == 0
        assert f"{key}: {expected_value}" in result.stdout

@pytest.mark.parametrize("key, value", [
    ("app_name", "NewTestApp"),
    ("admin_email", "new@example.com")
])
def test_config_set(key, value, mock_settings, mocker):
    result = runner.invoke(app, ["config", "--key", key, "--value", value])
    assert result.exit_code == 0
    assert f"Set {key} to {value}" in result.stdout
    # Update to use model_dump() instead of dict()
    updated_settings = settings.model_dump()  # Adjusted to use the new Pydantic method
    assert updated_settings[key] == value, f"Expected {key} to be set to {value}, but found {updated_settings[key]}"

@pytest.mark.usefixtures("mock_settings")
def test_config_display_all(mock_settings):
    result = runner.invoke(app, ["config"])
    assert result.exit_code == 0

    for key, expected_value in mock_settings.items():
        assert f"{key}: {expected_value}" in result.stdout