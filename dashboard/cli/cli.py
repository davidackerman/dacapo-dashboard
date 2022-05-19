import click

import logging
from pathlib import Path
import sys
from flask_socketio import SocketIO


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
@click.option(
    "--host",
    type=str,
    help="The (optional) host name for providing your server",
    default=None,
)
@click.option(
    "--port",
    type=int,
    help="The port to provide your server on. By Default 5000",
    default=5000,
)
def dashboard(host, port):
    from dashboard import create_app, socketio
    import socket

    app = create_app()

    url = socket.getfqdn()
    url = host if host is not None else url
    socketio.run(app=app, host=url, debug=True, port=port)


@cli.command()
def init_db():
    # TODO: Remove deprecated create_app?
    from dashboard import create_app
    from dashboard.stores import init_db

    app = create_app()

    init_db(app)
    click.echo("Initialized the database.")
