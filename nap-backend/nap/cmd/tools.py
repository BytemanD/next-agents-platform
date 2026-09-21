import click
from nap.master.manager import MANAGER
from pystonic.pretty.output import print_models


@click.group(name="tools")
def root():
    pass


@root.command("list")
def list_tools():
    print_models(MANAGER.list_tools())
