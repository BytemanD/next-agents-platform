import os

import click
import dotenv
from pystonic.common import context

from nap.cmd import agent, db, knowledge, knowledge_base, llm, session, tools


@click.group()
def root():
    dotenv.load_dotenv()
    context.setvars(account=os.getenv("NAP_USERNAME"))


def main():
    root.add_command(knowledge_base.root)
    root.add_command(knowledge.root)
    root.add_command(agent.root)
    root.add_command(session.root)
    root.add_command(tools.root)
    root.add_command(llm.root)
    root.add_command(db.root)
    root()


if __name__ == "__main__":
    main()
