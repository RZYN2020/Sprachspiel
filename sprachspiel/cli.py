"""Command-line interface for Sprachspiel."""

import sys
from pathlib import Path
from typing import Optional

import click

from sprachspiel import __version__
from sprachspiel.config import Config, CONFIG_DIR, DEFAULT_CONFIG_PATH


@click.group()
@click.version_option(version=__version__)
@click.option("--config", "-c", type=click.Path(exists=True), help="Path to config file")
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose output")
@click.option("--debug", is_flag=True, help="Enable debug output")
@click.pass_context
def cli(ctx: click.Context, config: Optional[str], verbose: bool, debug: bool) -> None:
    """Sprachspiel - Anki Card Card Generation Assistant.

    A cross-platform tool for language learners to efficiently create Anki vocabulary cards
    from videos, text, and web content.
    """
    # Store options in context
    ctx.ensure_object(dict)
    ctx.obj = {
        "config_path": Path(config) if config else None,
        "verbose": verbose,
        "debug": debug,
    }


@cli.command()
@click.pass_context
def start(ctx: click.Context) -> None:
    """Start the HTTP server."""
    from sprachspiel.server.app import create_app

    options = ctx.obj
    config = Config(options["config_path"])
    config.ensure_directories()

    host = config.get("server.host", "localhost")
    port = config.get("server.port", 8000)

    click.echo(f"Starting Sprachspiel server on {host}:{port}")
    click.echo(f"Config file: {config.config_path}")

    app = create_app(config)

    import uvicorn

    uvicorn.run(app, host=host, port=port)


@cli.command()
@click.pass_context
def process_queue(ctx: click.Context) -> None:
    """Process all cards in the queue and push to Anki."""
    options = ctx.obj
    config = Config(options["config_path"])

    from sprachspiel.core.queue import CardQueue
    from sprachspiel.core.engine import CardEngine

    queue = CardQueue(config)
    engine = CardEngine(config)

    if queue.is_empty():
        click.echo("Queue is empty. Nothing to process.")
        return

    pending = queue.get_all()
    click.echo(f"Processing {len(pending)} cards...")

    success_count = 0
    for card_data in pending:
        try:
            engine.generate_card(card_data)
            queue.remove(card_data["id"])
            success_count += 1
        except Exception as e:
            click.echo(f"Error processing card {card_data.get('word', 'unknown')}: {e}", err=True)

    click.echo(f"Processed {success_count}/{len(pending)} cards successfully.")


@cli.command()
@click.option("--output", "-o", type=click.Path(), help="Output directory for .apkg file")
@click.pass_context
def export(ctx: click.Context, output: Optional[str]) -> None:
    """Export all queued cards to an .apkg file."""
    options = ctx.obj
    config = Config(options["config_path"])

    from sprachspiel.core.queue import CardQueue
    from sprachspiel.anki.file_export import FileExporter

    queue = CardQueue(config)

    if queue.is_empty():
        click.echo("Queue is empty. Nothing to export.")
        return

    cards = queue.get_all()
    output_dir = Path(output) if output else Path(config.get("anki.file.output_dir", "./output"))
    output_dir.mkdir(parents=True, exist_ok=True)

    click.echo(f"Exporting {len(cards)} cards to {output_dir}")

    exporter = FileExporter(config)
    apkg_path = exporter.export_cards(cards, output_dir)

    click.echo(f"Exported to {apkg_path}")


@cli.command()
@click.pass_context
def status(ctx: click.Context) -> None:
    """Show connection and queue status."""
    options = ctx.obj
    config = Config(options["config_path"])

    from sprachspiel.core.queue import CardQueue

    queue = CardQueue(config)

    click.echo("Sprachspiel Status")
    click.echo(f"Config file: {config.config_path}")
    click.echo(f"Anki mode: {config.get('anki.mode')}")
    click.echo(f"Card generation mode: {config.get('card_generation.mode')}")
    click.echo(f"Queue size: {queue.size()}")

    # Check AnkiConnect connection
    if config.get("anki.mode") in ["connect", "both"]:
        from sprachspiel.anki.connect import AnkiConnect

        anki = AnkiConnect(config)
        if anki.check_connection():
            click.echo("AnkiConnect: Connected ✓")
        else:
            click.echo("AnkiConnect: Not connected ✗")


@cli.command()
@click.argument("key")
@click.argument("value", required=False)
@click.pass_context
def config_cmd(ctx: click.Context, key: str, value: Optional[str]) -> None:
    """Get or set configuration values.

    Usage:
        sprachspiel config <key>              # Get value
        sprachspiel config <key> <value>       # Set value
    """
    options = ctx.obj
    config = Config(options["config_path"])

    if value is None:
        # Get value
        result = config.get(key)
        click.echo(f"{key}: {result}")
    else:
        # Set value
        config.set(key, value)
        config.save()
        click.echo(f"Set {key} = {value}")


@cli.command()
@click.pass_context
def reload(ctx: click.Context) -> None:
    """Reload configuration from file."""
    options = ctx.obj
    config = Config(options["config_path"])

    config.reload()
    click.echo("Configuration reloaded.")


def main() -> int:
    """Main entry point for the CLI."""
    try:
        cli()
        return 0
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
