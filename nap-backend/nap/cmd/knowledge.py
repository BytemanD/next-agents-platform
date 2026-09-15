import click
from nap.db.models import Knowledge
from nap.knowledge.enrich_drivers.agent import EnrichmentAgentDriver
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
    print_models(
        Knowledge.query(),
        fields=["uuid", "knowledge_base", "creator", "name", "size", "status"],
    )


@root.command()
@click.argument("knowledge_uuid")
@click.option("--force", "-f", is_flag=True, help="force")
def enrich(knowledge_uuid, force: bool=False):
    driver = EnrichmentAgentDriver()
    item = Knowledge.get_by_uuid(knowledge_uuid)
    driver.enrich(item, replace=force)


# @root.command("sync", help="sync from db")
# def sync():
#     MANAGER.handle_saved()
