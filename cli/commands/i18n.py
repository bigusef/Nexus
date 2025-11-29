"""Translation management commands."""

import subprocess
from pathlib import Path
from typing import Annotated

import typer

from src.shared.enums import Language


app = typer.Typer(no_args_is_help=True)

LOCALES_DIR = Path(__file__).parent.parent.parent / "locales"
DOMAIN = "messages"
SOURCE_DIRS = ["src/", "workers/"]


@app.command()
def extract() -> None:
    """Extract translatable strings to messages.pot."""
    pot_file = LOCALES_DIR / f"{DOMAIN}.pot"
    cmd = ["pybabel", "extract", "-o", str(pot_file), *SOURCE_DIRS]
    subprocess.run(cmd, check=True)
    typer.echo(f"Extracted strings to {pot_file}")


@app.command()
def init(
    lang: Annotated[str | None, typer.Option(help="Language code (e.g., ar)")] = None,
    all_langs: Annotated[bool, typer.Option("--all", help="Initialize all languages")] = False,
) -> None:
    """Initialize translation catalog for a language."""
    if not lang and not all_langs:
        raise typer.BadParameter("Specify --lang or --all")

    pot_file = LOCALES_DIR / f"{DOMAIN}.pot"
    if not pot_file.exists():
        typer.echo("Run 'nexus i18n extract' first", err=True)
        raise typer.Exit(1)

    languages = [ln.value for ln in Language] if all_langs else [lang]

    for code in languages:
        cmd = ["pybabel", "init", "-i", str(pot_file), "-d", str(LOCALES_DIR), "-l", code]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            typer.echo(f"Initialized {code}")
        else:
            typer.echo(f"Skipped {code} (may already exist)")


@app.command()
def update() -> None:
    """Update existing catalogs with new strings."""
    pot_file = LOCALES_DIR / f"{DOMAIN}.pot"
    if not pot_file.exists():
        typer.echo("Run 'nexus i18n extract' first", err=True)
        raise typer.Exit(1)

    cmd = ["pybabel", "update", "-i", str(pot_file), "-d", str(LOCALES_DIR)]
    subprocess.run(cmd, check=True)
    typer.echo("Updated all catalogs")


@app.command(name="compile")
def compile_catalogs() -> None:
    """Compile .po files to .mo for runtime use."""
    cmd = ["pybabel", "compile", "-d", str(LOCALES_DIR)]
    subprocess.run(cmd, check=True)
    typer.echo("Compiled all catalogs")
