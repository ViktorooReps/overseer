import os

import click as click
import pkg_resources


__version__ = pkg_resources.require('overseer')[0].version


@click.group()
def cli():
    pass


@cli.command()
@click.argument('message', type=click.STRING)
def notify(message: str):
    print('notify')


@cli.command()
def monitor():
    print(os.environ['API'])


main = cli


if __name__ == '__main__':
    main()
