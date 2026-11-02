import click

from nap_client.cmd._utils import json_output, print_items, print_rows
from nap_client.v1.client import CLIENT

TOOLKIT_FIELDS = ["name", "title", "type", "help"]


@click.group("toolkit")
def root():
    "Available toolkits"


@root.command("list")
def list_toolkits():
    toolkits = CLIENT.list_toolkits()
    if json_output():
        print_items(toolkits)
        return
    rows = [
        {
            "name": item.metadata.name,
            "title": item.metadata.title,
            "type": item.metadata.type,
            "help": item.metadata.help,
        }
        for item in toolkits
    ]
    print_rows(rows, fields=TOOLKIT_FIELDS)
