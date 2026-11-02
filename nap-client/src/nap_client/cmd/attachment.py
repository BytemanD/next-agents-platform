from pathlib import Path

import click

from nap_client.cmd._utils import (
    confirm_delete,
    print_item,
    print_items,
    read_bytes,
    write_bytes,
)
from nap_client.v1.client import CLIENT

ATTACHMENT_FIELDS = ["uuid", "name", "size", "created_at"]


@click.group("attachment")
def root():
    "Attachment management"


@root.command("list")
def list_attachments():
    print_items(CLIENT.list_attachments(), fields=ATTACHMENT_FIELDS)


@root.command("get")
@click.argument("uuid")
def get_attachment(uuid: str):
    print_item(CLIENT.get_attachment(uuid))


@root.command("upload")
@click.argument("path", type=click.Path(exists=True, dir_okay=False))
def upload_attachment(path: str):
    file_path = Path(path)
    print_item(
        CLIENT.upload_attachment(file_path.name, read_bytes(path)),
        fields=ATTACHMENT_FIELDS,
    )


@root.command("download")
@click.argument("uuid")
@click.option("-o", "--output", help="Output path (default: attachment name)")
@click.option("--force", is_flag=True, help="Overwrite existing file")
def download_attachment(uuid: str, output: str | None, force: bool):
    attachment = CLIENT.get_attachment(uuid)
    if output:
        path = Path(output)
    else:
        path = Path(attachment.name or uuid)
    if path.exists() and not force:
        raise click.ClickException(f"{path} already exists, use --force to overwrite")
    path.write_bytes(CLIENT.get_attachment_content(uuid))
    click.echo(f"Saved to {path}")


@root.command("content")
@click.argument("uuid")
@click.option("-o", "--output", help="Write content to a file")
def get_attachment_content(uuid: str, output: str | None):
    write_bytes(CLIENT.get_attachment_content(uuid), output)


@root.command("delete")
@click.argument("uuid")
@click.option("--yes", is_flag=True, help="Skip confirmation")
def delete_attachment(uuid: str, yes: bool):
    confirm_delete("attachment", uuid, yes)
    CLIENT.delete_attachment(uuid)
    click.echo(f"Deleted attachment {uuid}")
