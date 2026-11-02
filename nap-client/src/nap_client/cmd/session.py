import click

from nap_client.cmd._utils import confirm_delete, print_items
from nap_client.v1.client import CLIENT

SESSION_FIELDS = ["uuid", "user", "agent", "title", "created_at", "updated_at"]
MESSAGE_FIELDS = ["id", "type", "content", "thinking"]


@click.group("session")
def root():
    "Session management"


@root.command("list")
@click.option("--agent", required=True, help="Agent uuid")
def list_sessions(agent: str):
    print_items(CLIENT.list_sessions(agent), fields=SESSION_FIELDS)


@root.command("messages")
@click.argument("session_id")
def list_messages(session_id: str):
    print_items(CLIENT.list_messages(session_id), fields=MESSAGE_FIELDS)


@root.command("delete")
@click.argument("session_id")
@click.option("--yes", is_flag=True, help="Skip confirmation")
def delete_session(session_id: str, yes: bool):
    confirm_delete("session", session_id, yes)
    CLIENT.delete_session(session_id)
    click.echo(f"Deleted session {session_id}")
