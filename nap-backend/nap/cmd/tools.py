import asyncio

import click
from nap.master.manager import MANAGER
from pystonic.pretty.output import print_models


@click.group(name="tool")
def root():
    pass


async def _list_tools():
    return MANAGER.list_tools()


@root.command("list")
def list_tools():
    print_models([x.metadata() for x in asyncio.run(_list_tools())])
