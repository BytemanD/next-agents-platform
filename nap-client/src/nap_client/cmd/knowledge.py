import click

from nap_client.cmd._utils import (
    confirm_delete,
    print_item,
    print_items,
    write_bytes,
)
from nap_client.v1.client import CLIENT

KNOWLEDGE_FIELDS = [
    "uuid",
    "knowledge_base",
    "name",
    "size",
    "status",
    "created_at",
]
TODO_FIELDS = ["uuid", "name", "status", "detail"]


@click.group("knowledge")
def root():
    "Knowledge (document) management"


@root.command("list")
def list_knowledges():
    print_items(CLIENT.list_knowledges(), fields=KNOWLEDGE_FIELDS)


@root.command("get")
@click.argument("uuid")
def get_knowledge(uuid: str):
    print_item(CLIENT.get_knowledge(uuid))


@root.command("todos")
@click.argument("uuid")
def get_knowledge_todos(uuid: str):
    print_items(CLIENT.get_knowledge_todos(uuid), fields=TODO_FIELDS)


@root.command("content")
@click.argument("uuid")
@click.option("-o", "--output", help="Write content to a file")
def get_knowledge_content(uuid: str, output: str | None):
    write_bytes(CLIENT.get_knowledge_content(uuid), output)


@root.command("update")
@click.argument("uuid")
@click.option("--name")
@click.option("--size", type=int)
@click.option("--path")
@click.option("--status", type=int)
def update_knowledge(
    uuid: str,
    name: str | None,
    size: int | None,
    path: str | None,
    status: int | None,
):
    print_item(
        CLIENT.update_knowledge(uuid, name=name, size=size, path=path, status=status),
        fields=KNOWLEDGE_FIELDS,
    )


@root.command("delete")
@click.argument("uuid")
@click.option("--yes", is_flag=True, help="Skip confirmation")
def delete_knowledge(uuid: str, yes: bool):
    confirm_delete("knowledge", uuid, yes)
    CLIENT.delete_knowledge(uuid)
    click.echo(f"Deleted knowledge {uuid}")
