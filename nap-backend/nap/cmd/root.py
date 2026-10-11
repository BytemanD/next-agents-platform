import os

import click

import dotenv
from nap.cmd import agent, session, knowledge, llm, knowledge_base, tools
from pystonic.common import context


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
    root()


if __name__ == "__main__":
    main()
