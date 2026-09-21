import click

from nap.cmd import agent, session, knowledge, knowledge_base, tools


@click.group()
def root():
    pass


def main():
    root.add_command(knowledge_base.root)
    root.add_command(knowledge.root)
    root.add_command(agent.root)
    root.add_command(session.root)
    root.add_command(tools.root)
    root()


if __name__ == "__main__":
    main()
