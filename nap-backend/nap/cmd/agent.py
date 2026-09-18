import asyncio

import click
from nap.db.models import Agents
from pystonic.pretty.output import print_models

from nap.master.manager import MANAGER
from nap.common.exceptions import LLMRateLimitError


@click.group(name="agent")
def root():
    pass


@root.command("list")
def list_agents():
    print_models(Agents.query(), fields=["uuid", "name", "llm", "status"])


async def _do_chat(agent: Agents, query: str):
    reasoning = True

    try:
        async for event in MANAGER.chat(agent, query):
            reasoning_content = event.additional_kwargs.get("reasoning_content")

            if reasoning_content:
                reasoning = True
                click.secho(reasoning_content, nl=False, fg="bright_black")
                continue
            if reasoning:
                click.echo("")
                reasoning = False

            click.secho(event.content, nl=False)
        click.echo("")

    except LLMRateLimitError as e:
        raise click.ClickException(str(e))


@root.command()
@click.argument("agent_uuid")
@click.argument("query")
def chat(agent_uuid: str, query: str):
    asyncio.run(_do_chat(Agents.get_by_uuid(agent_uuid), query))


@root.command()
@click.argument("agent_uuid")
def sessions(agent_uuid: str):
    items = asyncio.run(MANAGER.list_sessions(agent_uuid))
    print_models(items)


@root.command("messages")
@click.argument("session")
def list_messages(session: str):
    items = asyncio.run(MANAGER.list_messages(session))
    print_models(items)
