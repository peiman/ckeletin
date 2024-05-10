# main.py
from mycliapp.commands import app
from mycliapp.logging_config import setup_logging
from mycliapp.config import settings

def main():
    logger = setup_logging()
    logger.info(f"Starting {settings.app_name}...")
    app()

if __name__ == "__main__":
    main()
