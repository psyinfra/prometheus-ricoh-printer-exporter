# This file is licensed under the ISC license.
# Oskar Druska 2022
# For further information look up LICENSE.txt

# This will be the script that yields the needed information and "talks" to the printers

from dataclasses import dataclass
from typing import Dict
from typing import Iterator
from typing import Union
from bs4 import BeautifulSoup
import csv
import logging
import requests
import os


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


def get_urls() -> Dict[str, str]:
    # gets current working directory and constructs path to config file
    here = os.path.dirname(os.path.abspath(__file__))
    filename = os.path.join(here, 'printers.csv')

    # parses config file, containing the names and URLs of the printers
    urls = []
    with open(filename, 'r') as printers_csv:
        filereader = csv.DictReader(printers_csv)
        for row in filereader:
            urls.append((row['printer_name'], row['printer_url']))
            print(row['printer_name'] + " " + row['printer_url'])

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