# This file is licensed under the ISC license.
# Oskar Druska 2022
# For further information look up LICENSE.txt

# Exporter file; produces Prometheus metrics using the crawled printer values from ricoh_data_cralwer.py

from prometheus_client import Summary
from prometheus_client.core import GaugeMetricFamily

from . import scrape_printers

REQUEST_TIME = Summary("ricoh_printer_exporter_collect_",
                       "Time spent to collect metrics from ricoh_data_crawler.py")


class RicohPrinterExporter:
    def __init__(self, printers, insec: bool) -> None:
        self.printers = printers
        self.insecure = insec

    @REQUEST_TIME.time()
    def collect(self):
        # returns a Printer_Values object in each generator call
        printers = scrape_printers(printers=self.printers, insecure=self.insecure)

        for printer in printers:
            g = GaugeMetricFamily(
                name='ricoh_printer_level_percent',
                labels=['name', 'color'],
                documentation='toner level in percent')
            g.add_metric([printer.name, 'black'], printer.level_black)
            g.add_metric([printer.name, 'cyan'], printer.level_cyan)
            g.add_metric([printer.name, 'magenta'], printer.level_magenta)
            g.add_metric([printer.name, 'yellow'], printer.level_yellow)
            yield g
