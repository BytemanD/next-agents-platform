from pathlib import Path

import click
from alembic import command
from alembic.config import Config
from loguru import logger
from nap.common.conf import CONF


@click.group(name="db")
def root():
    """DB tools"""


def run_migrations():
    migrations_dir = Path(__file__).parent.parent.joinpath("migrations")

    logger.info("migrations")

    alembic_cfg = Config()
    alembic_cfg.set_main_option("script_location", str(migrations_dir))
    alembic_cfg.set_main_option("sqlalchemy.url", CONF.db.url)

    # 直接执行 upgrade head
    command.upgrade(alembic_cfg, "head")


alembic_cfg = Config()
migrations_dir = Path(__file__).parent.parent.joinpath("migrations")
alembic_cfg.set_main_option("script_location", str(migrations_dir))
alembic_cfg.set_main_option("sqlalchemy.url", CONF.db.url)


@root.command
def version():
    command.current(alembic_cfg)


@root.command
@click.option(
    "-g",
    "--autogenerate",
    is_flag=True,
    help="whether or not to autogenerate the script from the database",
)
@click.option(
    "-m",
    "--message",
    help="whether or not to autogenerate the script from the database",
)
def revision(autogenerate: bool = False, message: str | None = None):
    command.revision(alembic_cfg, autogenerate=autogenerate, message=message)


@root.command
def migrate():
    logger.info("migrations")

    command.upgrade(alembic_cfg, "head")
    run_migrations()
