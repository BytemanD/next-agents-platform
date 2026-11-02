import sys

import click
import httpx
from loguru import logger

from nap_client.cmd import (
    agent,
    attachment,
    auth,
    dashboard,
    knowledge,
    knowledge_base,
    llm,
    mcp,
    monitoring,
    session,
    tools,
    user,
)
from nap_client.common.conf import CONF

LOG_VERBOSES = ["WARNING", "INFO", "DEBUG", "TRACE"]


@click.group()
@click.option("-v", "--verbose", count=True)
@click.option("--json", "as_json", is_flag=True, help="Output raw JSON")
@click.pass_context
def root(ctx: click.Context, verbose: int, as_json: bool):
    """NAP Client"""

    import logging

    logging.basicConfig(level=logging.WARNING)
    logger.remove()
    logger.configure(
        extra={"context": CONF.auth.username},
        # patcher=_context_patcher,
    )
    logger.add(
        sys.stdout,
        level=LOG_VERBOSES[min(len(LOG_VERBOSES) - 1, verbose)],
    )

    ctx.ensure_object(dict)
    ctx.obj["json"] = as_json


for module in (
    agent,
    attachment,
    auth,
    dashboard,
    knowledge,
    knowledge_base,
    llm,
    mcp,
    monitoring,
    session,
    tools,
    user,
):
    root.add_command(module.root)


def main():
    try:
        root()
    except httpx.HTTPStatusError as e:
        resp = e.response
        try:
            detail = resp.json()
        except ValueError:
            detail = resp.text
        click.echo(
            f"Error: {resp.status_code} {e.request.method} {e.request.url} - {detail}",
            err=True,
        )
        raise SystemExit(1) from None
    except httpx.RequestError as e:
        click.echo(f"Error: request failed - {e}", err=True)
        raise SystemExit(1) from None
