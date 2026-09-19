import asyncio

import click
from nap.db.models import Session
from nap.master.api.v1.tools import ToolModel
from nap.master.manager import MANAGER
from pystonic.pretty.output import print_models

from nap.llm.tools import vector


@click.group(name="tools")
def root():
    pass


@root.command("list")
def list_tools():
    print_models(MANAGER.list_tools())
