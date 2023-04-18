from pathlib import Path
import sys
import webbrowser

import click
import rocks

import classy.classify
from classy import core
from classy.log import logger
import classy.preprocessing
from classy import taxonomies
from classy import sources


@click.group()
@click.version_option(version=classy.__version__, message="%(version)s")
def cli_classy():
    """CLI for minor body classification."""
    pass


@cli_classy.command()
def docs():
    """Open the classy documentation in browser."""
    webbrowser.open("https://classy.readthedocs.io/en/latest/", new=2)


@cli_classy.command()
@click.argument("id_", type=str)
@click.option("-c", "--classify", is_flag=True, help="Classify the spectra.")
@click.option(
    "-t",
    "--taxonomy",
    default="mahlke",
    help="Specify the taxonomic system.",
    type=click.Choice(taxonomies.SYSTEMS),
)
@click.option(
    "-s",
    "--source",
    type=click.Choice(sources.SOURCES),
    multiple=True,
    help="Select one or more online repositories.",
)
@click.option(
    "--save",
    is_flag=True,
    help="Save plot to file in current working directory.",
)
@click.option("-v", is_flag=True, help="Set verbose output.")
def spectra(id_, classify, taxonomy, source, save, v):
    """Retrieve, plot, classify spectra of an individual asteroid."""

    if v:
        classy.set_log_level("DEBUG")

    name, number = rocks.id(id_)

    if name is None:
        logger.error("Cannot retrieve spectra for unidentified asteroid.")
        sys.exit()
    else:
        logger.debug(f"Looking for reflectance spectra of ({number}) {name}")

    if not source:
        source = classy.sources.SOURCES

    # Load spectra
    spectra = core.Spectra(id_, source=source)

    if not spectra:
        sys.exit()

    # Classify
    if classify:
        spectra.classify(taxonomy=taxonomy)

    # Plot
    if save:
        save = f"{number}_{name}_classy.png"

    spectra.plot(add_classes=classify, taxonomy=taxonomy, save=save if save else None)

    if save:
        logger.info(f"Figure stored under {Path().cwd() / save}")
