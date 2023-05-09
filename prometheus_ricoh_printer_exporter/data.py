from dataclasses import dataclass
from typing import Dict, Iterator, Union
import json
import logging
import requests
import os

from bs4 import BeautifulSoup


@dataclass
class Printer:
    name: str
    level_black = None
    level_cyan = None
    level_magenta = None
    level_yellow = None

    def __init__(self, name: str, black: float, cyan: float, magenta: float, yellow: float) -> None:
        self.name = name
        self.level_black = black
        self.level_cyan = cyan
        self.level_magenta = magenta
        self.level_yellow = yellow


def get_urls(config: str) -> Dict[str, str]:
    # creates absolut path for config file
    filename = os.path.abspath(config)
    print(filename)

    # parses config file, containing the names and URLs of the printers
    urls = []
    with open(filename, 'r') as printers_json:
        data = json.load(printers_json)

        for key, value in data.items():
            try:
                name = key
                url = value['url']
            except KeyError as exc:
                raise KeyError(
                    f'Error in configuration file: {exc} not found for {key}')
            urls.append((name, url))

    return urls


def width_to_percent(width: int) -> float:
    """Convert graphical units to percent, where 160 units is 100%"""
    return float(width) * (100 / 160)


def get_toner_level(tag: dict) -> Union[int, None]:
    """Return toner percentage if the tag has it"""
    return width_to_percent(tag['width']) if tag.get('width', False) else None


def scrape_printers(printers: Dict[str, str], insecure: bool = False) -> Iterator[Printer]:
    """Scrape printer URLs for toner level"""
    for name, url in printers:
        logging.info(f'Scraping {name} at {url}')
        try:
            data = requests.get(url, verify=not insecure)
        except requests.exceptions.ConnectTimeout as t:
            logging.error(f'ConectTimeout error from {name} with error message: {t}')
            continue
        if data.status_code != 200:
            logging.error(f'Scrape error from {name} with status code: {data.status_code}')
            continue

        data = BeautifulSoup(data.text, 'html.parser')
        tags = data.find_all('img', class_='ver-algn-m mgn-R5p bdr-1px-666', attrs='width')
        if not tags:
            logging.error(f'Scrape error from {name}: missing relevant tags')
            continue

        yield Printer(
            name=name,
            black=get_toner_level(tags[0]),
            cyan=get_toner_level(tags[1]),
            magenta=get_toner_level(tags[2]),
            yellow=get_toner_level(tags[3]))
