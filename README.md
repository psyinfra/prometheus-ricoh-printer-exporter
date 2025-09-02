# prometheus-ricoh-printer-exporter
A Python-based Prometheus exporter for retrieving data from Ricoh printers.
Currently the exporter retrieves toner levels, component status, and a page
count for printed, copied, scanned, and faxed pages.

## Install
You can install the exporter from this repository using the following command:
`pip install git+https://github.com/psyinfra/prometheus-ricoh-printer-exporter`

## Configuration
The exporter can be configured using either a configuration file providing a
json array of targeted printers (see `config_example.json`) or by providing
the `--targets` argument with a list of printer addresses.

Example configuration file:
```json
[
  "https://printer1.url",
  "https://printer2.url"
]
```

## Example
The exporter can be run with a configuration file using:

```commandline
prometheus_ricoh_printer_exporter -c config_example.json
```

or by using the `--targets` flag
```commandline
prometheus_ricoh_printer_exporter -t https://printer1.url https://printer2.url
```

To read the output in Prometheus format, use `curl 0.0.0.0:9188`. This
address and port can differ if a custom `--web.listen-address` was used.

## Usage
```
usage: prometheus_ricoh_printer_exporter [-h] [-w LISTEN_ADDRESS] [-c config] [-t targets [targets ...]] [-i]

Python-based Ricoh Printer exporter for prometheus.io

optional arguments:
  -h, --help            show this help message and exit
  -w LISTEN_ADDRESS, --web.listen-address LISTEN_ADDRESS
                        Address and port to listen on (default = :9188)
  -c config, --config config
                        configuration json file containing printer web-ui addresses
  -t targets [targets ...], --targets targets [targets ...]
  -i, --insecure        Skip SSL validation of the printer web-ui
```

Note that either `-c` or `-t` is required, but they cannot be used together.
