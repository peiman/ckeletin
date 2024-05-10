# logging_config.py
import logging
from rich.logging import RichHandler

# logger.debug() for detailed diagnostic information.
# logger.info() for general informational messages.
# logger.warning() to log potential issues that are not necessarily errors.
# logger.error() and logger.critical() for serious problems.

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler(rich_tracebacks=True)]
    )
    return logging.getLogger("rich")

logger = setup_logging()  # This should create and configure your logger