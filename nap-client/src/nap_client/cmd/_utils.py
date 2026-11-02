import json
from collections.abc import Sequence
from pathlib import Path
from typing import Any

import click
from pydantic import BaseModel
from pystonic.pretty import output
from rich import box
from rich.console import Console
from rich.table import Table

console = Console()


def json_output() -> bool:
    ctx = click.get_current_context(silent=True)
    return bool(ctx and ctx.obj and ctx.obj.get("json"))


def dump_json(data: Any) -> None:
    console.print_json(json.dumps(data, ensure_ascii=False, default=str))


def print_items(
    items: Sequence[BaseModel],
    fields: list[str] | None = None,
    title: str | None = None,
) -> None:
    if json_output():
        dump_json([item.model_dump(mode="json") for item in items])
        return
    output.print_models(items, fields=fields, title=title)


def print_item(item: BaseModel, fields: list[str] | None = None) -> None:
    if json_output():
        dump_json(item.model_dump(mode="json"))
        return
    output.print_model(item, fields=fields)


def print_rows(
    rows: Sequence[dict], fields: list[str], title: str | None = None
) -> None:
    if json_output():
        dump_json([{field: row.get(field) for field in fields} for row in rows])
        return
    if not rows:
        console.print("No items", style="yellow")
        return
    table = Table(*fields, title=title, box=box.HEAVY_HEAD)
    for row in rows:
        table.add_row(*[str(row.get(field, "")) for field in fields])
    console.print(table)


def parse_json(value: str | None, option: str = "--json") -> Any:
    if value is None:
        return None
    try:
        return json.loads(value)
    except json.JSONDecodeError as e:
        raise click.BadParameter(f"invalid JSON for {option}: {e}") from e


def read_text(path: str | None) -> str | None:
    if path is None:
        return None
    return Path(path).read_text(encoding="utf-8")


def read_bytes(path: str) -> bytes:
    return Path(path).read_bytes()


def write_bytes(data: bytes, output_path: str | None = None) -> None:
    if output_path:
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        click.echo(f"Saved to {path}")
        return
    click.get_binary_stream("stdout").write(data)


def confirm_delete(kind: str, uuid: str, yes: bool) -> None:
    if not yes:
        click.confirm(f"Delete {kind} {uuid}?", abort=True)
