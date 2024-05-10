import typer
from rich.console import Console
from settings import Settings
import logging
from rich.logging import RichHandler

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=True)]
)
logger = logging.getLogger("rich")

# logger.debug() for detailed diagnostic information.
# logger.info() for general informational messages.
# logger.warning() to log potential issues that are not necessarily errors.
# logger.error() and logger.critical() for serious problems.

settings = Settings()
app = typer.Typer()
console = Console()

@app.command()
def echo(text: str):
    """Echoes the text back to the user."""
    logger.info(f"Echoing: {text}")
    console.print(f"[bold magenta]{text}[/bold magenta]")

@app.command()
def ping():
    """Responds with 'pong'."""
    logger.info("Received ping command")
    console.print("[bold green]pong[/bold green]")


@app.command()
def config(key: str = typer.Option(None, help="Config key to view or set"),
           value: str = typer.Option(None, help="Value to set for the key")):
    """View or set a configuration setting."""
    if key and value:
        setattr(settings, key, value)
        logger.info(f"Set {key} to {value}")
        console.print(f"[bold green]Set {key} to {value}.[/bold green]")
    elif key:
        val = getattr(settings, key, None)
        logger.info(f"Retrieved {key}: {val}")
        console.print(f"[bold yellow]{key}: {val}[/bold yellow]")
    else:
        logger.info("Displaying all settings")
        # Only print the actual settings
        config_items = {name: getattr(settings, name) for name in settings.model_fields.keys()}
        for k, v in config_items.items():
            console.print(f"[bold yellow]{k}: {v}[/bold yellow]")

if __name__ == "__main__":
    logger.info(f"Starting {settings.app_name}...")
    app()
