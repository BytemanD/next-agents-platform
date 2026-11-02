import click

from nap_client.cmd._utils import (
    dump_json,
    json_output,
    print_item,
    print_rows,
)
from nap_client.v1.client import CLIENT


@click.group("monitoring")
def root():
    "Monitoring data"


@root.command("token-usage")
@click.option("--days", default=7, type=int, show_default=True)
@click.option("--agent", "agent_uuid", help="Agent uuid")
@click.option("--model", help="Model name")
def token_usage(days: int, agent_uuid: str | None, model: str | None):
    usage = CLIENT.token_usage(days=days, agent_uuid=agent_uuid, model=model)
    if json_output():
        print_item(usage)
        return

    click.echo(
        f"calls={usage.total_calls} "
        f"prompt={usage.total_prompt} "
        f"completion={usage.total_completion} "
        f"total={usage.total_tokens}"
    )
    rows = [
        {"day": day, "prompt": prompt, "completion": completion}
        for day, prompt, completion in zip(
            usage.days, usage.prompt, usage.completion, strict=True
        )
    ]
    print_rows(rows, fields=["day", "prompt", "completion"])


@root.command("models")
def models():
    models = CLIENT.monitoring_models()
    if json_output():
        dump_json(models)
        return
    for model in models:
        click.echo(model)


@root.command("latency")
@click.option("--days", default=7, type=int, show_default=True)
@click.option("--agent", "agent_uuid", help="Agent uuid")
@click.option("--model", help="Model name")
def latency(days: int, agent_uuid: str | None, model: str | None):
    data = CLIENT.latency(days=days, agent_uuid=agent_uuid, model=model)
    if json_output():
        print_item(data)
        return

    rows = [
        {"day": day, "p50": p50, "p95": p95, "p99": p99}
        for day, p50, p95, p99 in zip(
            data.days, data.p50, data.p95, data.p99, strict=True
        )
    ]
    print_rows(rows, fields=["day", "p50", "p95", "p99"])
