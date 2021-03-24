import click

import logging
from pathlib import Path
import sys


@click.group()
@click.option(
    "--log-level",
    type=click.Choice(
        ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"], case_sensitive=False
    ),
    default="WARNING",
)
def cli(log_level):
    # when calling a function through command line
    # the local directory doesn't seem to be added to
    # the path by default. Add it explicitly here.
    cwd = Path.cwd()
    sys.path.append(str(cwd.absolute()))

    logging.basicConfig(level=getattr(logging, log_level.upper()))


@cli.command()
def dashboard():
    from dashboard import create_app
    import socket

    app = create_app()

    url = socket.getfqdn()
    app.run(host=url, debug=True)


@cli.command()
def init_db():
    from dashboard import create_app
    from dashboard.db import init_db

    app = create_app()

    init_db(app)
    click.echo("Initialized the database.")