import typer
from rich.console import Console
from settings import Settings

settings = Settings()
app = typer.Typer()
console = Console()

@app.command()
def echo(text: str):
    """Echoes the text back to the user."""
    console.print(f"[bold magenta]{text}[/bold magenta]")

@app.command()
def ping():
    """Responds with 'pong'."""
    console.print("[bold green]pong[/bold green]")


@app.command()
def config(key: str = typer.Option(None, help="Config key to view or set"),
           value: str = typer.Option(None, help="Value to set for the key")):
    """View or set a configuration setting."""
    if key and value:
        setattr(settings, key, value)
        console.print(f"[bold green]Set {key} to {value}.[/bold green]")
    elif key:
        val = getattr(settings, key, None)
        console.print(f"[bold yellow]{key}: {val}[/bold yellow]")
    else:
        # Only print the actual settings
        config_items = {name: getattr(settings, name) for name in settings.model_fields.keys()}
        for k, v in config_items.items():
            console.print(f"[bold yellow]{k}: {v}[/bold yellow]")

if __name__ == "__main__":
    console.print(f"Starting {settings.app_name}...")
    app()
