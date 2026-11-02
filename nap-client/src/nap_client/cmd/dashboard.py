import click

from nap_client.cmd._utils import json_output, print_item, print_items
from nap_client.v1.client import CLIENT


@click.group("dashboard")
def root():
    "Dashboard overview"


@root.command("show")
def show_dashboard():
    data = CLIENT.dashboard()
    if json_output():
        print_item(data)
        return

    print_items(
        data.stats,
        fields=["key", "label", "value", "change"],
        title="Stats",
    )
    print_items(
        data.recent_agents,
        fields=["uuid", "name", "model", "status"],
        title="Recent agents",
    )
    print_items(
        data.activities,
        fields=["type", "text", "time"],
        title="Activities",
    )
