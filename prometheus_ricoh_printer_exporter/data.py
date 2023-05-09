from dataclasses import dataclass, field
from typing import Union
import logging
import requests

from bs4 import BeautifulSoup


def toner_level(tag: dict) -> Union[float, None]:
    """Convert width value to toner level (percentage)"""
    width = tag.get('width', None)

    if width is None or not isinstance(width, (int, float)):
        return None

    return float(width) * (100 / 160)


@dataclass
class Toner:
    """Toner levels for a printer"""
    black: Union[float, None] = field(default=None)
    cyan: Union[float, None] = field(default=None)
    magenta: Union[float, None] = field(default=None)
    yellow: Union[float, None] = field(default=None)


@dataclass
class Printer:
    address: str = field(repr=False)
    insecure: bool = field(repr=False, default=False)
    toner: Toner = field(default=Toner())

    def scrape(self) -> None:
        self.toner = self.scrape_toner(self.address, self.insecure)

    @staticmethod
    def scrape_toner(target: str, insecure: bool = False) -> Toner:
        try:
            data = requests.get(target, verify=not insecure)
        except requests.exceptions.ConnectTimeout as exc:
            logging.error(exc)
            return Toner()

        if data.status_code != 200:
            logging.error(
                f'Failed to scrape {target}: status code '
                f'{data.status_code}]')
            return Toner()

        data = BeautifulSoup(data.text, 'html.parser')
        tags = data.find_all(
            'img', class_='ver-algn-m mgn-R5p bdr-1px-666', attrs='width')

        if not tags:
            logging.error(
                f'Failed to scrape {target}: missing required HTML '
                f'tags')
            return Toner()

        colors = ['black', 'cyan', 'magenta', 'yellow']
        tags = dict(zip(colors, [toner_level(tag) for tag in tags[::3]]))
        return Toner(**tags)
