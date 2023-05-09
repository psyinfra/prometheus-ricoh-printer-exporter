from setuptools import setup, find_packages

setup(
    name='prometheus_ricoh_printer_exporter',
    version='1.4.0',
    description=(
        'Python-based Prometheus exporter to retrieve data from Ricoh '
        'printers'),
    author='Oskar Druska',
    author_email='o.druska@fz-juelich.de',
    packages=find_packages(),
    license='ISC',
    install_requires=[
        'aiohttp',
        'BeautifulSoup4',
        'prometheus_client'
    ],
    python_requires=">=3.7",
    entry_points={
        'console_scripts': [
            'prometheus_ricoh_printer_exporter=prometheus_ricoh_printer_exporter.main:main'  # noqa: E501
        ],
    },
)
