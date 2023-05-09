import argparse
import json
import logging
import time
import urllib.parse

from prometheus_client import start_http_server, REGISTRY

from . import (
    RicohPrinterExporter, DEFAULT_LISTEN_INTERFACE, DEFAULT_PORT)


def parse_args() -> argparse.Namespace:
    """Parse arguments when executed as a script"""
    parser = argparse.ArgumentParser(
        description='Python-based Ricoh Printer exporter for prometheus.io')
    parser.add_argument(
        '-w', '--web.listen-address', type=str, required=False,
        dest='listen_address', default=f':{DEFAULT_PORT}',
        help=f'Address and port to listen on (default = :{DEFAULT_PORT})')
    parser.add_argument(
        '-c', '--config', metavar='config', dest='config', required=False,
        help='configuration json file containing printer web-ui addresses')
    parser.add_argument(
        '-t', '--targets', metavar='targets', dest='targets', nargs='+',
        required=False)
    parser.add_argument(
        '-i', '--insecure', dest='insecure', action='store_true',
        default=False, help='Skip SSL validation of the printer web-ui')

    args = parser.parse_args()

    if args.targets and args.config:
        parser.error('Cannot use --targets and --config together')
    elif not args.targets and not args.config:
        parser.error('Either --targets or --config is required')

    return args


def get_targets(config: str = None) -> list[str]:
    """Get printer target URIs from a config json file"""
    with open(config, 'r') as file:
        data = json.load(file)

    if not isinstance(data, list) or not all(isinstance(x, str) for x in data):
        raise TypeError('Config must contain only a list of strings')

    return data


def main():
    logging.basicConfig(format='%(asctime)s %(message)s', level=logging.INFO)

    args = parse_args()
    targets = get_targets(args.config) if args.config else args.targets
    addr = urllib.parse.urlsplit(f'//{args.listen_address}')
    hostname = addr.hostname if addr.hostname else DEFAULT_LISTEN_INTERFACE
    port = addr.port if addr.port else DEFAULT_PORT

    start_http_server(port, addr=hostname)
    REGISTRY.register(RicohPrinterExporter(targets, args.insecure))
    logging.info('listening on %s' % addr.netloc)

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logging.info('Interrupted by user')
        exit(0)


if __name__ == '__main__':
    main()
