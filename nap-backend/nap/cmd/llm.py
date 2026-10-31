import click
from pystonic.pretty.output import print_models

from nap.master.manager import MANAGER


@click.group(name="llm")
def root():
    pass


@root.command("list")
def list_tools():
    print_models(MANAGER.list_llm())
