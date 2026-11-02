from pathlib import Path

import click

from nap_client.cmd._utils import (
    confirm_delete,
    print_item,
    print_items,
    read_bytes,
)
from nap_client.v1.client import CLIENT

KB_FIELDS = ["uuid", "name", "active", "description"]
KNOWLEDGE_FIELDS = ["uuid", "name", "size", "status", "created_at"]


@click.group("kb")
def root():
    "Knowledge base management"


@root.command("list")
@click.option("--shared", is_flag=True, help="List shared knowledge bases")
def list_knowledge_bases(shared: bool):
    print_items(CLIENT.list_knowledge_bases(shared=shared), fields=KB_FIELDS)


@root.command("get")
@click.argument("uuid")
def get_knowledge_base(uuid: str):
    print_item(CLIENT.get_knowledge_base(uuid))


@root.command("create")
@click.option("--name", required=True)
@click.option("--description", default="")
def create_knowledge_base(name: str, description: str):
    print_item(
        CLIENT.create_knowledge_base(name, description=description),
        fields=KB_FIELDS,
    )


@root.command("update")
@click.argument("uuid")
@click.option("--name")
@click.option("--description")
@click.option("--active/--inactive", default=None, help="Enable or disable")
def update_knowledge_base(
    uuid: str,
    name: str | None,
    description: str | None,
    active: bool | None,
):
    print_item(
        CLIENT.update_knowledge_base(
            uuid, name=name, description=description, active=active
        ),
        fields=KB_FIELDS,
    )


@root.command("delete")
@click.argument("uuid")
@click.option("--yes", is_flag=True, help="Skip confirmation")
def delete_knowledge_base(uuid: str, yes: bool):
    confirm_delete("knowledge base", uuid, yes)
    CLIENT.delete_knowledge_base(uuid)
    click.echo(f"Deleted knowledge base {uuid}")


@root.command("stats")
@click.argument("uuid")
def knowledge_base_stats(uuid: str):
    print_item(CLIENT.knowledge_base_stats(uuid))


@root.command("knowledges")
@click.argument("uuid")
def list_kb_knowledges(uuid: str):
    print_items(CLIENT.list_knowledge_base_knowledges(uuid), fields=KNOWLEDGE_FIELDS)


@root.command("add-file")
@click.argument("uuid")
@click.argument("path", type=click.Path(exists=True, dir_okay=False))
def add_knowledge_file(uuid: str, path: str):
    item = CLIENT.add_knowledge_file(uuid, Path(path).name, read_bytes(path))
    print_item(item, fields=KNOWLEDGE_FIELDS)


@root.command("add-url")
@click.argument("uuid")
@click.argument("urls", nargs=-1, required=True)
@click.option("--name", help="Override file name")
def add_knowledge_from_urls(uuid: str, urls: tuple[str, ...], name: str | None):
    web_files = [{"url": url, "name": name} for url in urls]
    print_items(
        CLIENT.add_knowledge(uuid, web_files=web_files),
        fields=KNOWLEDGE_FIELDS,
    )


@root.command("add-attachment")
@click.argument("uuid")
@click.argument("attachments", nargs=-1, required=True)
def add_knowledge_from_attachments(uuid: str, attachments: tuple[str, ...]):
    print_items(
        CLIENT.add_knowledge(uuid, attachments=list(attachments)),
        fields=KNOWLEDGE_FIELDS,
    )
