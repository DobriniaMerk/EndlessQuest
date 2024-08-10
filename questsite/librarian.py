import sqlite3

import click
from flask import current_app, g


def ask_for_index():
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row

    return g.db


def return_index(e=None):
    index = g.pop('db', None)
    if index is not None:
        index.close()


def employ():
    db = ask_for_index()

    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))


@click.command('init-db')
def employ_command():
    employ()
    click.echo('Librarian ready.')


def onstart(app):
    app.teardown_appcontext(return_index)
    app.cli.add_command(employ_command)
