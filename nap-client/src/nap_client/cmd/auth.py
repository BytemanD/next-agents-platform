import click

from nap_client.cmd._utils import dump_json, json_output
from nap_client.v1.client import CLIENT


@click.group("auth")
def root():
    "Authentication"


@root.command("token")
def token():
    value = CLIENT.login()
    if json_output():
        dump_json({"token": value})
        return
    click.echo(value)


@root.command("refresh")
def refresh():
    value = CLIENT.refresh_token()
    if json_output():
        dump_json({"token": value})
        return
    click.echo(value)
