import click

from nap_client.cmd._utils import confirm_delete, print_item, print_items
from nap_client.v1.client import CLIENT

LLM_FIELDS = ["uuid", "name", "base_url", "models"]


@click.group("llm")
def root():
    "LLM provider management"


@root.command("list")
def list_llms():
    print_items(CLIENT.list_llms(), fields=LLM_FIELDS)


@root.command("get")
@click.argument("uuid")
def get_llm(uuid: str):
    print_item(CLIENT.get_llm(uuid))


@root.command("create")
@click.option("--base-url", required=True, help="OpenAI-compatible base URL")
@click.option("--api-key", prompt=True, hide_input=True)
@click.option("--name", default="")
@click.option("--model", "models", multiple=True, help="Supported model name")
def create_llm(base_url: str, api_key: str, name: str, models: tuple[str, ...]):
    print_item(
        CLIENT.create_llm(
            base_url=base_url, api_key=api_key, name=name, models=list(models)
        ),
        fields=LLM_FIELDS,
    )


@root.command("update")
@click.argument("uuid")
@click.option("--name")
@click.option("--base-url")
@click.option("--api-key")
@click.option("--model", "models", multiple=True, help="Supported model name")
def update_llm(
    uuid: str,
    name: str | None,
    base_url: str | None,
    api_key: str | None,
    models: tuple[str, ...],
):
    print_item(
        CLIENT.update_llm(
            uuid,
            name=name,
            base_url=base_url,
            api_key=api_key,
            models=list(models) or None,
        ),
        fields=LLM_FIELDS,
    )


@root.command("delete")
@click.argument("uuid")
@click.option("--yes", is_flag=True, help="Skip confirmation")
def delete_llm(uuid: str, yes: bool):
    confirm_delete("llm", uuid, yes)
    CLIENT.delete_llm(uuid)
    click.echo(f"Deleted llm {uuid}")
