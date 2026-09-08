"""给已有 SQLite 表补充新增列（开发期轻量迁移）。"""

from sqlalchemy import inspect, text
from loguru import logger

from pystonic.orm.database import get_session
from pystonic.orm.database import _engine

# table -> [(新增列, SQLite 列定义)]
_ALTERS: dict[str, list[tuple[str, str]]] = {
    "agents": [
        ("status", "TEXT NOT NULL DEFAULT 'draft'"),
        ("tools", "TEXT NOT NULL DEFAULT '[]'"),
    ],
    "llms": [
        ("name", "TEXT NOT NULL DEFAULT ''"),
    ],
}


def ensure_columns() -> None:
    inspector = inspect(_engine)
    tables = set(inspector.get_table_names())
    for table, columns in _ALTERS.items():
        if table not in tables:
            continue
        existing = {c["name"] for c in inspector.get_columns(table)}
        for column, ddl in columns:
            if column in existing:
                continue
            with get_session() as session:
                session.exec(text(f"ALTER TABLE {table} ADD COLUMN {column} {ddl}"))
                session.commit()
            logger.info("added column {} to table {}", column, table)
