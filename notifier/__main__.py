import os

import click as click
import pkg_resources
from click_option_group import optgroup

from notifier.gpu_monitor import run_monitoring
from notifier.telegram import TelegramNotifier

__version__ = pkg_resources.require('gpu-overseer')[0].version
API_TOKEN_ENV = 'TELEGRAM_API_TOKEN'
API_URL_ENV = 'TELEGRAM_API_URL'


def get_telegram_notifier() -> TelegramNotifier:
    if API_URL_ENV not in os.environ:
        raise EnvironmentError(f'{API_URL_ENV} is not set!')
    if API_TOKEN_ENV not in os.environ:
        raise EnvironmentError(f'{API_TOKEN_ENV} is not set!')

    return TelegramNotifier(telegram_url=os.environ[API_URL_ENV], api_token=os.environ[API_TOKEN_ENV])


@click.group()
@click.option('--version')
def cli(version):
    pass


@cli.command()
@click.argument('message', type=click.STRING)
def notify(message: str):
    get_telegram_notifier().notify(message)


@cli.command()
@click.option('-i', '--check-interval', type=click.INT, default=1, help='Waiting interval in seconds between GPU availability checks.')
def monitor(check_interval: int):
    notifier = get_telegram_notifier()
    run_monitoring(notifier.notify, interval=check_interval)


main = cli


if __name__ == '__main__':
    main()
