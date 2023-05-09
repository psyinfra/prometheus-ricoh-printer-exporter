from dataclasses import dataclass, field
from ssl import SSLCertVerificationError
from typing import Union
from urllib.parse import urljoin
import logging

from aiohttp import (
    ClientSession, ClientTimeout, TCPConnector, ServerTimeoutError)
from aiohttp.web import HTTPException
from bs4 import BeautifulSoup

from . import ENDPOINT_TONER


async def read_target(url: str, ssl: bool) -> BeautifulSoup:
    async with ClientSession(
            timeout=ClientTimeout(total=10),
            connector=TCPConnector(ssl=None if ssl else False)) as session:
        async with session.get(url) as response:
            text = await response.read()
    return BeautifulSoup(text.decode('utf-8'), 'html.parser')


def toner_level(tag: dict) -> Union[float, None]:
    """Convert width value to toner level (percentage)"""
    width = tag.get('width', None)

    try:
        level = float(width) * (100 / 160)
    except ValueError:
        return None

    return level


@dataclass
class Printer:
    address: str
    insecure: bool = field(default=False)
    toner: dict = field(init=False)

    async def scrape(self) -> None:
        toner_address = urljoin(self.address, ENDPOINT_TONER)
        self.toner = await self.scrape_toner(toner_address, self.insecure)

    @staticmethod
    async def scrape_toner(
            target: str, insecure: bool = False) -> dict[str, float]:
        try:
            data = await read_target(target, not insecure)
        except (
                SSLCertVerificationError, HTTPException,
                ServerTimeoutError) as exc:
            logging.error(f'({target}) {exc}')
            return {}

        tags = data.find_all(
            'img', class_='ver-algn-m mgn-R5p bdr-1px-666', attrs='width')

        if not tags:
            logging.error(
                f'Failed to scrape {target}: missing required HTML tags')
            return {}

        colors = ['black', 'cyan', 'magenta', 'yellow']
        return dict(zip(colors, [toner_level(tag) for tag in tags[:4]]))
