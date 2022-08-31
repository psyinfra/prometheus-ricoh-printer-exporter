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
from . import exporter


DEFAULT_HOSTNAME = '0.0.0.0'
DEFAULT_PORT = 9840


def main():
    logging.basicConfig(format='%(asctime)s %(message)s', level=logging.INFO)

    args = parse_args()

    config_file = args.config
    printers = get_urls(config_file)

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
    group.add_argument(
        "-c", "--config",
        help="Configuration JSON file containing "
             "UPS addresses and login info."
             "NOTE: make sure to provide an absolute path to ensure the file is found.",
        required=True
    )

    return parser.parse_args()


if __name__ == '__main__':
    main()
