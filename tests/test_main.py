# test_main.py
import pytest
from unittest.mock import patch
from mycliapp.main import main
from mycliapp.config import settings

@patch('mycliapp.main.setup_logging')
@patch('mycliapp.main.app')
def test_main(mock_app, mock_setup_logging):
    logger_mock = mock_setup_logging.return_value
    main()
    # Make sure to use settings after importing it
    logger_mock.info.assert_called_once_with(f"Starting {settings.app_name}...")
    mock_app.assert_called_once()

