import asyncio

from prometheus_client import Summary
from prometheus_client.core import GaugeMetricFamily, CounterMetricFamily

from .printer import Printer

REQUEST_TIME = Summary(
    "ricoh_printer_exporter_collect_",
    "Time spent to collect metrics from ricoh_data_crawler.py")


class RicohPrinterExporter:
    def __init__(self, targets: list[str], insecure: bool) -> None:
        self.printers = [
            Printer(address=target, insecure=insecure) for target in targets]

    async def _scrape(self):
        return await asyncio.gather(
            *[printer.scrape() for printer in self.printers])

    @REQUEST_TIME.time()
    def collect(self):
        asyncio.run(self._scrape())

        g = GaugeMetricFamily(
            name='ricoh_printer_tonerlevel_percent',
            labels=['address', 'color'],
            documentation='toner level in percent')

        for printer in self.printers:
            for color, value in printer.toner.items():
                if value is not None:
                    g.add_metric([printer.address, color], value)

        yield g

        g = CounterMetricFamily(
            name='ricoh_printer_printed_total',
            labels=['address', 'color'],
            documentation='total pages printed')

        for printer in self.printers:
            for color, value in printer.pages.get('printed', {}).items():
                if value is not None:
                    g.add_metric([printer.address, color], value)

        yield g

        g = CounterMetricFamily(
            name='ricoh_printer_copied_total',
            labels=['address', 'color'],
            documentation='total pages copied')

        for printer in self.printers:
            for color, value in printer.pages.get('copied', {}).items():
                if value is not None:
                    g.add_metric([printer.address, color], value)

        yield g

        g = CounterMetricFamily(
            name='ricoh_printer_faxed_total',
            labels=['address', 'type'],
            documentation='total pages faxed')

        for printer in self.printers:
            for typ, value in printer.pages.get('faxed', {}).items():
                if value is not None:
                    g.add_metric([printer.address, typ], value)

        yield g

        g = CounterMetricFamily(
            name='ricoh_printer_scanned_total',
            labels=['address', 'color'],
            documentation='total pages scanned')

        for printer in self.printers:
            for color, value in printer.pages.get('scanned', {}).items():
                if value is not None:
                    g.add_metric([printer.address, color], value)

        yield g
