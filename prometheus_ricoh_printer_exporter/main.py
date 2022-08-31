# This file is licensed under the ISC license.
# Oskar Druska 2022
# For further information look up LICENSE.txt

# Exporter entry point

import argparse
import time
import logging
import urllib.parse
from prometheus_client import start_http_server, REGISTRY
from .data import get_urls
from . import exporter_file


DEFAULT_HOSTNAME = '0.0.0.0'
DEFAULT_PORT = 9840


def main():
    logging.basicConfig(format='%(asctime)s %(message)s', level=logging.INFO)

    args = parse_args()
    printers = get_urls()

    listen_addr = urllib.parse.urlsplit(f'//{args.listen_address}')
    addr = listen_addr.hostname if listen_addr.hostname else DEFAULT_HOSTNAME
    port = listen_addr.port if listen_addr.port else DEFAULT_PORT

    REGISTRY.register(exporter_file.RicohPrinterExporter(printers, args.insecure))
    start_http_server(port, addr=addr)

    # keep the thing going indefinitely
    logging.info("Exporter started!")
    while True:
        time.sleep(1)


def parse_args():
    '''argparser; returns the args from command line'''

    parser = argparse.ArgumentParser(
        description='Set up the Prometheus exporter (connection ports)')
    group = parser.add_argument_group()
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

    return parser.parse_args()


if __name__ == '__main__':
    main()
