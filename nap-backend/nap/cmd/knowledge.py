import click
from nap.db.models import Knowledge
from pystonic.pretty.output import print_models

from nap.knowledge.manager import MANAGER


@click.group(name="knowledge")
def root():
    pass


@root.command("list")
@click.option(
    "--vectorstore", "-v", is_flag=True, help="list knowledge from vectorstore"
)
def list_knowledge(vectorstore: bool = False):
    if vectorstore:
        print_models(MANAGER.list_documents())

        return
    print_models(Knowledge.query())


@root.command("ingest")
@click.argument("knowledge_base")
def ingest(knowledge_base):
    pass


# @root.command("sync", help="sync from db")
# def sync():
#     MANAGER.handle_saved()
