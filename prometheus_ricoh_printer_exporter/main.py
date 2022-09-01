# This file is licensed under the ISC license.
# Oskar Druska 2022
# For further information look up LICENSE.txt

# Exporter entry point

import argparse
import sys
import time
import logging
import urllib.parse
from prometheus_client import start_http_server, REGISTRY
from .data import get_urls
from . import exporter

DEFAULT_HOSTNAME = '0.0.0.0'
DEFAULT_PORT = 9840


def main():
    logging.basicConfig(format='%(asctime)s %(message)s', level=logging.INFO)

    args = parse_args()
    printers = get_urls()

    if args.add_printer:
        add_printer()
        sys.exit(0)

    if args.remove_printer:
        remove_printer()
        sys.exit(0)

    # if listen_address is None, urlsplit would parse '//None' which would result in 'none' (String) as hostname
    # annotation: solution not ideal
    listen_addr = urllib.parse.urlsplit(f'//{args.listen_address}') if args.listen_address is not None else urllib.parse.urlsplit(None)

    addr = listen_addr.hostname if listen_addr.hostname else DEFAULT_HOSTNAME
    port = listen_addr.port if listen_addr.port else DEFAULT_PORT

    REGISTRY.register(exporter.RicohPrinterExporter(printers, args.insecure))
    start_http_server(port, addr=addr)

    # keep the thing going indefinitely
    while True:
        time.sleep(1)


def add_printer():
    print("would add printer WIP")


def remove_printer():
    print("would remove printer WIP")


def parse_args():
    '''argparser; returns the args from command line'''

    parser = argparse.ArgumentParser(
        description='Set up the Prometheus exporter (connection ports)')

    group = parser.add_argument_group()
    config = parser.add_mutually_exclusive_group()

    group.add_argument(
        '-w', '--web.listen-address',
        type=str,
        dest='listen_address',
        help=f'Address and port to expose metrics and web interface. Default: ":{DEFAULT_PORT}"\n'
        'To listen on all interfaces, omit the IP. ":<port>"`\n'
        'To listen on a specific IP: <address>:<port>')
    group.add_argument(
        '-i', '--insecure',
        dest='insecure',
        action='store_true',
        default=False,
        help='Skip SSL validation of the printer website.')

    config.add_argument(
        '-a', '--add',
        dest='add_printer',
        default=None,
        help='Provide printer URL to parse: -a <URL> <name>\n'
        'If given URL is not already registered, it will be added to the config file.\n'
        'If URL is already registered, message will be shown and nothing gets changed.'
    )
    config.add_argument(
        '-r', '--remove',
        dest='remove_printer',
        default=None,
        help='Provide name of the Printer that shall be removed: -r <name>\n'
        'If name exists, the corresponding printer will be removed from the config file.\n'
        'If name is not registered, message will be shown and nothign gets changed.'
    )

    return parser.parse_args()


if __name__ == '__main__':
    main()
