import asyncio

import click
from nap.db.models import Session
from pystonic.pretty.output import print_models

from nap.master.manager import MANAGER


@click.group(name="session")
def root():
    pass


@root.command("list")
def list_sessions():
    print_models(
        Session.query(), fields=["uuid", "user", "agent", "created_at", "title"]
    )


@root.command("messages")
@click.argument("session")
def list_messages(session: str):
    items = asyncio.run(MANAGER.list_messages(Session.get_by_uuid(session)))
    print_models(items)
