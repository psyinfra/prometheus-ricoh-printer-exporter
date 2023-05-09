from dataclasses import dataclass, field
from ssl import SSLCertVerificationError
from typing import Union
from urllib.parse import urljoin
import logging

from aiohttp import (
    ClientSession, ClientTimeout, TCPConnector, ServerTimeoutError)
from aiohttp.web import HTTPException
from bs4 import BeautifulSoup

from . import ENDPOINT_TONER, ENDPOINT_PAGES


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
    pages: dict = field(init=False)

    async def scrape(self) -> None:
        toner_address = urljoin(self.address, ENDPOINT_TONER)
        pages_address = urljoin(self.address, ENDPOINT_PAGES)

        self.toner = await self.scrape_toner(target=toner_address)
        self.pages = await self.scrape_pages(target=pages_address)

    async def scrape_toner(self, target: str) -> dict[str, float]:
        try:
            soup = await read_target(target, not self.insecure)
        except (
                SSLCertVerificationError, HTTPException,
                ServerTimeoutError) as exc:
            logging.error(f'({target}) {exc}')
            return {}

        tags = soup.find_all(
            'img', class_='ver-algn-m mgn-R5p bdr-1px-666', attrs='width')

        if not tags:
            logging.error(
                f'Failed to scrape {target}: missing required HTML tags')
            return {}

        colors = ['black', 'cyan', 'magenta', 'yellow']
        return dict(zip(colors, [toner_level(tag) for tag in tags[:4]]))

    async def scrape_pages(self, target: str) -> dict[str, dict[str, str]]:
        try:
            soup = await read_target(target, not self.insecure)
        except (
                SSLCertVerificationError, HTTPException,
                ServerTimeoutError) as exc:
            logging.error(f'({target}) {exc}')
            return {}

        tags = soup.find_all('td')
        mapping_default = [
            126, 132, 138, 144, 88, 94, 100, 106, 163, 169, 211, 216]
        mapping_a3dlt = [
            206, 222, 238, 254, 128, 144, 160, 176, 283, 323, 335, 340]

        if soup.body.findAll(text='A3/DLT'):
            logging.debug('Found A3/DLT; changing mapping')
            mapping = mapping_a3dlt
        elif soup.body.findAll(text='Printer'):
            mapping = mapping_default
        else:
            return {}

        return {
            'printed': {
                'fullcolor': tags[mapping[0]].string,
                'blackwhite': tags[mapping[1]].string,
                'singlecolor': tags[mapping[2]].string,
                'twocolor': tags[mapping[3]].string},
            'copied': {
                'fullcolor': tags[mapping[4]].string,
                'blackwhite': tags[mapping[5]].string,
                'singlecolor': tags[mapping[6]].string,
                'twocolor': tags[mapping[7]].string},
            'faxed': {
                'received': tags[mapping[8]].string,
                'transmitted': tags[mapping[9]].string},
            'scanned': {
                'fullcolor': tags[mapping[10]].string,
                'blackwhite': tags[mapping[11]].string}}
