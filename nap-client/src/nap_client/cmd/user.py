import click

from nap_client.cmd._utils import confirm_delete, print_item
from nap_client.v1.client import CLIENT

USER_FIELDS = ["uuid", "username", "email", "created_at"]


@click.group("user")
def root():
    "User account management"


@root.command("me")
def me():
    print_item(CLIENT.me(), fields=USER_FIELDS)


@root.command("create")
@click.option("--username", required=True)
@click.option("--password", prompt=True, hide_input=True, confirmation_prompt=True)
@click.option("--email")
def create_user(username: str, password: str, email: str | None):
    print_item(CLIENT.register(username, password, email=email), fields=USER_FIELDS)


@root.command("update")
@click.argument("uuid")
@click.option("--account")
@click.option("--email")
def update_user(uuid: str, account: str | None, email: str | None):
    print_item(
        CLIENT.update_user(uuid, account=account, email=email),
        fields=USER_FIELDS,
    )


@root.command("delete")
@click.argument("uuid")
@click.option("--yes", is_flag=True, help="Skip confirmation")
def delete_user(uuid: str, yes: bool):
    confirm_delete("user", uuid, yes)
    CLIENT.delete_user(uuid)
    click.echo(f"Deleted user {uuid}")
