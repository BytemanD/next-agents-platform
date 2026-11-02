import click

from nap.cmd import db


@click.group()
def root():
    """Nap Backend Tools"""


def main():
    root.add_command(db.root)
    root()


if __name__ == "__main__":
    main()
