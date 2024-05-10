# test.commands.py
import pytest
from typer.testing import CliRunner
from mycliapp.commands import app

runner = CliRunner()

def test_echo():
    result = runner.invoke(app, ["echo", "Hello"])
    assert result.exit_code == 0
    assert "Hello" in result.stdout

def test_ping():
    result = runner.invoke(app, ["ping"])
    assert result.exit_code == 0
    assert "pong" in result.stdout

def test_config_set():
    result = runner.invoke(app, ["config", "--key", "app_name", "--value", "TestApp"])
    assert result.exit_code == 0
    assert "Set app_name to TestApp" in result.stdout
