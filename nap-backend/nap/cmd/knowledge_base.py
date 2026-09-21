import click
from nap.common.knowledge_client import KnowledgeClient
from nap.db.models import KnowledgeBase
from pystonic.pretty.output import print_models


KNOWLEDGE_CLIENT = KnowledgeClient()


@click.group(name="knowledge-base")
def root():
    pass


@root.command("list")
def list_knowledge_base():
    print_models(KnowledgeBase.query())
