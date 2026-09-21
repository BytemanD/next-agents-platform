import click
from nap.common.knowledge_client import KnowledgeClient
from nap.db.models import Knowledge, KnowledgeBase
from nap.services.enrich import ENRICH_SERVICE
from pystonic.pretty.output import print_models

from nap.knowledge.manager import MANAGER

KNOWLEDGE_CLIENT = KnowledgeClient()
@click.group(name="knowledge")
def root():
    pass


@root.command("list")
@click.argument(
    "knowwledge_base", help="knowledge base uuid"
)
@click.option(
    "--vectorstore", "-v", is_flag=True, help="list knowledge from vectorstore"
)
def list_knowledge(knowwledge_base: str, vectorstore: bool = False):
    if vectorstore:
        print_models(KNOWLEDGE_CLIENT.list_documents(knowwledge_base))
        return
    print_models(
        Knowledge.query(Knowledge.knowledge_base == knowwledge_base),
        fields=["uuid", "creator", "name", "size", "status"],
    )


@root.command()
@click.argument("knowledge_uuid")
@click.option("--force", "-f", is_flag=True, help="force")
def enrich(knowledge_uuid, force: bool = False):
    item = Knowledge.get_by_uuid(knowledge_uuid)
    ENRICH_SERVICE.enrich(item, replace=force)


# @root.command("sync", help="sync from db")
# def sync():
#     MANAGER.handle_saved()
