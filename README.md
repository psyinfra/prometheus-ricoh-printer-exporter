# prometheus-ricoh-printer-exporter
Building a prometheus exporter for ricoh-printer related information like toner level

## Install
You can install the exporter from this repository using the following command:
`pip install git+https://github.com/psyinfra/prometheus-ricoh-printer-exporter`

## Configuration
To run the exporter, you need to provide a configuration file using the .json format.
A template file "config_example.json" can be found at top-level in this repository.
This is the template:

```
{
    "printer1_name": {
        "url": "https://address.to.printer"
    },

    "printer2_name": {
        "url": "https://address.to.printer"
    }
}
```

## Test
You'll need a configuration file containing the names and URLs of the printers you want to scrape.
A template can be found in the repository under the name of config_example.json

To test the exporter, you can host the script on your own machine:
  1. `prometheus_ricoh_printer_exporter -c <abspath to config file>` (make sure you installed via pip)
  2. (from another terminal) `curl 0.0.0.0:9188` (default IP-address)

Running `curl 0.0.0.0:9188` should give you an output of similar structure
like this:
```
# HELP ricoh_printer_level_percent black toner level in percent
# TYPE ricoh_printer_level_percent gauge
ricoh_printer_level_percent{color="black",printer_name="oak"} 50.0
```
(The output should be similar for other data points, i.e. cyan)

## Usage
```
usage: prometheus_ricoh_printer_exporter [-h] [-w LISTEN_ADDRESS] [-i] -c CONFIG

Set up the Prometheus exporter (connection ports)

options:
  -h, --help            show this help message and exit

  -w LISTEN_ADDRESS, --web.listen-address LISTEN_ADDRESS
                        Address and port to expose metrics and web interface. Default: ":9188" To listen on all interfaces, omit the IP. ":<port>"` To listen on a specific IP: <address>:<port>
  -i, --insecure        Skip SSL validation of the printer website.
  -c CONFIG, --config CONFIG
                        Configuration JSON file containing UPS addresses and login info.NOTE: make sure to provide an absolute path to ensure the file is found.
```
