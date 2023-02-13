import sys
import webbrowser

import click
import numpy as np
import pandas as pd
import rich
import rocks

import classy.classify
from classy import core
from classy.logging import logger
import classy.preprocessing
from classy import cache
from classy import plotting


def _logging_option(func):
    func = click.option(
        "-l",
        "--log",
        type=int,
        default=2,
        help="Set level of logging. Everything [0] to nothing [5]. Default is 2.",
    )(func)
    return func


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
@click.option("-s", "--source", help="Select a online repository.")
def spectra(id_, classify, source):
    """Retrieve, plot, classify spectra of an individual asteroid."""

    name, number = rocks.id(id_)

    if name is None:
        logger.error("Cannot retrieve spectra for unidentified asteroid.")
        sys.exit()
    else:
        logger.info(f"Looking for reflectance spectra of ({number}) {name}")

    if source is not None:
        source = source.split(",")

    # Load spectra
    spectra = core.Spectra(id_, source=source)

    if not spectra:
        sys.exit()

    # Classify
    if classify:
        spectra.classify()

    # Plot
    spectra.plot(add_classes=classify)
