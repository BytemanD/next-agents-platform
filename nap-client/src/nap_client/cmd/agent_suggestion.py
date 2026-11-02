import click

from nap_client.cmd._utils import (
    confirm_delete,
    json_output,
    parse_json,
    print_item,
    print_items,
    read_text,
)
from nap_client.v1.client import CLIENT

AGENT_FIELDS = ["uuid", "name", "status", "llm", "description"]
DETAIL_FIELDS = [
    "uuid",
    "name",
    "status",
    "llm",
    "knowledge_bases",
    "tools",
    "mcps",
]


@click.group("agent")
def root():
    "Agent management"


def _instruction(instruction: str | None, instruction_file: str | None) -> str | None:
    if not instruction and not instruction_file:
        return None
    from_file = read_text(instruction_file)
    return from_file if from_file is not None else instruction


@root.command("list")
def list_agents():
    print_items(CLIENT.list_agents(), fields=AGENT_FIELDS)


@root.command("get")
@click.argument("uuid")
def get_agent(uuid: str):
    print_item(CLIENT.get_agent(uuid))


@root.command("detail")
@click.argument("uuid")
def get_agent_detail(uuid: str):
    print_item(CLIENT.get_agent_detail(uuid), fields=DETAIL_FIELDS)


@root.command("create")
@click.option("--name", required=True, help="Agent name")
@click.option("--description", default="")
@click.option("--instruction", default="")
@click.option(
    "--instruction-file",
    type=click.Path(exists=True, dir_okay=False),
    help="Read instruction from a file",
)
@click.option("--llm", default="", help="LLM uuid")
@click.option("--status", default="draft")
@click.option("--config", help='JSON object, e.g. {"temperature": 0.7}')
@click.option("--kb", "knowledge_bases", multiple=True, help="Knowledge base uuid")
@click.option("--mcp", "mcp_uuids", multiple=True, help="MCP uuid")
@click.option("--tools", help="JSON object of enabled tools")
def create_agent(
    name: str,
    description: str,
    instruction: str,
    instruction_file: str | None,
    llm: str,
    status: str,
    config: str | None,
    knowledge_bases: tuple[str, ...],
    mcp_uuids: tuple[str, ...],
    tools: str | None,
):
    agent = CLIENT.create_agent(
        name=name,
        description=description,
        instruction=_instruction(instruction, instruction_file) or "",
        llm=llm,
        status=status,
        config=parse_json(config, "--config"),
        knowledge_bases=list(knowledge_bases),
        tools=parse_json(tools, "--tools"),
        mcp_uuids=list(mcp_uuids),
    )
    print_item(agent, fields=AGENT_FIELDS)


@root.command("update")
@click.argument("uuid")
@click.option("--name")
@click.option("--description")
@click.option("--instruction")
@click.option(
    "--instruction-file",
    type=click.Path(exists=True, dir_okay=False),
    help="Read instruction from a file",
)
@click.option("--llm", help="LLM uuid")
@click.option("--status")
@click.option("--config", help='JSON object, e.g. {"temperature": 0.7}')
@click.option("--kb", "knowledge_bases", multiple=True)
@click.option("--mcp", "mcp_uuids", multiple=True)
@click.option("--tools", help="JSON object of enabled tools")
def update_agent(
    uuid: str,
    name: str | None,
    description: str | None,
    instruction: str | None,
    instruction_file: str | None,
    llm: str | None,
    status: str | None,
    config: str | None,
    knowledge_bases: tuple[str, ...],
    mcp_uuids: tuple[str, ...],
    tools: str | None,
):
    agent = CLIENT.update_agent(
        uuid,
        name=name,
        description=description,
        instruction=_instruction(instruction, instruction_file),
        llm=llm,
        status=status,
        config=parse_json(config, "--config"),
        knowledge_bases=list(knowledge_bases) or None,
        tools=parse_json(tools, "--tools"),
        mcp_uuids=list(mcp_uuids) or None,
    )
    print_item(agent, fields=AGENT_FIELDS)


@root.command("delete")
@click.argument("uuid")
@click.option("--yes", is_flag=True, help="Skip confirmation")
def delete_agent(uuid: str, yes: bool):
    confirm_delete("agent", uuid, yes)
    CLIENT.delete_agent(uuid)
    click.echo(f"Deleted agent {uuid}")


@root.command("chat")
@click.argument("uuid")
@click.argument("query")
@click.option("--session", default="", help="Session uuid")
@click.option("--model", default="", help="Override model")
@click.option("--tool", "tools", multiple=True)
@click.option("--kb", "knowledge_bases", multiple=True)
@click.option("--mcp", "mcp_uuids", multiple=True)
@click.option("--attachment", "attachments", multiple=True)
def chat_agent(
    uuid: str,
    query: str,
    session: str,
    model: str,
    tools: tuple[str, ...],
    knowledge_bases: tuple[str, ...],
    mcp_uuids: tuple[str, ...],
    attachments: tuple[str, ...],
):
    failed = False
    for event in CLIENT.chat_agent(
        uuid,
        query,
        session=session,
        model=model,
        tools=list(tools),
        knowledge_bases=list(knowledge_bases),
        mcp_uuids=list(mcp_uuids) or None,
        attachments=list(attachments),
    ):
        if json_output():
            click.echo(event.model_dump_json())
            continue
        if event.type == "error":
            click.echo(event.msg, err=True)
            failed = True
        elif event.type == "thinking":
            click.echo(click.style(event.msg, fg="bright_black"), err=True, nl=False)
        else:
            click.echo(event.msg, nl=False)
    if not json_output():
        click.echo()
    if failed:
        raise click.exceptions.Exit(1)


@root.command("suggestions")
@click.argument("uuid")
def get_agent_suggestions(uuid: str):
    items = CLIENT.get_agent_suggestions(uuid)
    print(items)
