from prometheus_client import Summary
from prometheus_client.core import GaugeMetricFamily

from . import Printer

REQUEST_TIME = Summary(
    "ricoh_printer_exporter_collect_",
    "Time spent to collect metrics from ricoh_data_crawler.py")


class RicohPrinterExporter:
    def __init__(self, targets: list[str], insecure: bool) -> None:
        self.printers = [
            Printer(address=target, insecure=insecure) for target in targets]

    @REQUEST_TIME.time()
    def collect(self):
        for printer in self.printers:
            printer.scrape()

            g = GaugeMetricFamily(
                name='ricoh_printer_tonerlevel_percent',
                labels=['address', 'color'],
                documentation='toner level in percent')
            g.add_metric([printer.address, 'black'], printer.toner.black)
            g.add_metric([printer.address, 'cyan'], printer.toner.cyan)
            g.add_metric([printer.address, 'magenta'], printer.toner.magenta)
            g.add_metric([printer.address, 'yellow'], printer.toner.yellow)
            yield g
