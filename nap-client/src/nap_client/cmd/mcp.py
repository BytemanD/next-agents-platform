import click

from nap_client.cmd._utils import confirm_delete, print_item, print_items
from nap_client.v1.client import CLIENT

MCP_FIELDS = ["uuid", "name", "url", "transport"]


@click.group("mcp")
def root():
    "MCP server management"


@root.command("list")
def list_mcps():
    print_items(CLIENT.list_mcps(), fields=MCP_FIELDS)


@root.command("get")
@click.argument("uuid")
def get_mcp(uuid: str):
    print_item(CLIENT.get_mcp(uuid))


@root.command("create")
@click.option("--url", required=True, help="MCP server URL")
@click.option("--name", help="MCP server name (fetched when omitted)")
@click.option("--transport", default="streamable_http")
@click.option("--api-key")
def create_mcp(url: str, name: str | None, transport: str, api_key: str | None):
    print_item(
        CLIENT.create_mcp(url=url, name=name, transport=transport, api_key=api_key),
        fields=MCP_FIELDS,
    )


@root.command("update")
@click.argument("uuid")
@click.option("--name")
@click.option("--url")
@click.option("--transport")
@click.option("--api-key")
def update_mcp(
    uuid: str,
    name: str | None,
    url: str | None,
    transport: str | None,
    api_key: str | None,
):
    print_item(
        CLIENT.update_mcp(
            uuid, name=name, url=url, transport=transport, api_key=api_key
        ),
        fields=MCP_FIELDS,
    )


@root.command("delete")
@click.argument("uuid")
@click.option("--yes", is_flag=True, help="Skip confirmation")
def delete_mcp(uuid: str, yes: bool):
    confirm_delete("mcp", uuid, yes)
    CLIENT.delete_mcp(uuid)
    click.echo(f"Deleted mcp {uuid}")
