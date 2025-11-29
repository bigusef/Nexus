"""Nexus Cortex CLI."""

import typer

from .commands.i18n import app as i18n_app


app = typer.Typer(
    name="nexus",
    help="Nexus Cortex CLI utilities",
    no_args_is_help=True,
)

app.add_typer(i18n_app, name="i18n", help="Translation management commands")
