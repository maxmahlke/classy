from pathlib import Path
import sys
import webbrowser

import click
import rich
import rocks

import classy.classify
from classy import cache
from classy import core
from classy import config
from classy import index
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
    "--templates",
    default=None,
    help="Add class templates of the specified complex.",
    type=click.Choice(taxonomies.COMPLEXES.keys()),
)
@click.option(
    "-s",
    "--source",
    type=click.Choice(sources.SOURCES),
    multiple=True,
    help="Select one or more online repositories.",
)
@click.option(
    "-e",
    "--exclude",
    type=click.Choice(sources.SOURCES),
    multiple=True,
    help="Exclude one or more online repositories.",
)
@click.option(
    "--save",
    is_flag=True,
    help="Save plot to file in current working directory.",
)
@click.option("-v", is_flag=True, help="Set verbose output.")
def spectra(id_, classify, taxonomy, templates, source, exclude, save, v):
    """Retrieve, plot, classify spectra of an individual asteroid."""

    if v:
        classy.set_log_level("DEBUG")
        rocks.set_log_level("DEBUG")
    else:
        rocks.set_log_level("ERROR")

    name, number = rocks.id(id_)

    if name is None:
        logger.error("Cannot retrieve spectra for unidentified asteroid.")
        sys.exit()
    else:
        logger.debug(f"Looking for reflectance spectra of ({number}) {name}")

    if not source:
        source = None

    if exclude:
        # If exclude but no sources defined (default case), load sources
        if source is None:
            source = index.load().source.unique()

        source = [s for s in source if s not in exclude]

    # Load spectra
    spectra = core.Spectra(id_, source=source)

    if not spectra:
        sys.exit()

    # Classify
    if classify:
        spectra.classify(taxonomy=taxonomy)
    else:
        taxonomy = None  # required for the plotting function

    # Plot
    if save:
        save = f"{number}_{name}_classy.png"

    spectra.plot(taxonomy=taxonomy, save=save if save else None, templates=templates)

    if save:
        logger.info(f"Figure stored under {Path().cwd() / save}")


@cli_classy.command()
@click.argument("path", type=str)
def add(path):
    """Add a private spectra collection."""
    path = Path(path)

    if not path.is_file():
        click.echo("You need to pass the path of an index CSV file.")
        sys.exit()

    sources.private.parse_index(path)


@cli_classy.command()
def status():
    """Manage the index of asteroid spectra."""
    from rich import prompt

    # ------
    # Echo inventory
    cache.echo_inventory()

    # ------
    # Download all or clear
    decision = prompt.Prompt.ask(
        "Choose one of these actions:\n"
        "[blue][0][/blue] Do nothing "
        "[blue][1][/blue] Clear the cache "
        "[blue][2][/blue] Retrieve all spectra",
        choices=["0", "1", "2"],
        show_choices=False,
        default="0",
    )

    if decision == "1":
        decision = prompt.Prompt.ask(
            f"\nThis will delete the cache directory and all its contents. Are you sure?",
            choices=["y", "n"],
            show_choices=True,
        )

        if decision in ["y"]:
            cache.remove()

    elif decision == "2":
        rich.print()
        rocks.set_log_level("CRITICAL")
        classy.set_log_level("CRITICAL")
        sources._retrieve_spectra()

        # cache.echo_inventory()
