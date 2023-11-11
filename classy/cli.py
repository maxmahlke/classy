from pathlib import Path
import sys
import webbrowser

import click
import rich
import rocks

import classy.classify
from classy import cache
from classy import core
from classy import index
from classy.log import logger
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

@cli_classy.command(
    context_settings=dict(
        ignore_unknown_options=True,
    )
)
@click.argument("args", type=click.UNPROCESSED, nargs=-1)
@click.option("-p", "--plot", is_flag=True, help="Plot the spectra.")
@click.option("-s", "--save", help="Save plot to file.")
def spectra(args, plot, save):
    """Retrieve, plot, classify spectra of given asteroid."""

    if not args:
        raise ValueError("No query parameters were specified.")

    # Separate query parameters and identifiers
    idx_options = [i for i, arg in enumerate(args) if arg.startswith("--")]
    kwargs = (
        {args[i].strip("--"): args[i + 1] for i in idx_options} if idx_options else {}
    )

    id = args[: min(idx_options)] if idx_options else args
    id = None if not id else id

    # Convert id to query criterion if provided
    if id is not None:
        if not isinstance(id, (list, tuple)):
            id = [id]

        id = [rocks.id(i)[0] for i in id if i is not None]

        if "name" in kwargs:
            logger.warning(
                "Specifying asteroid identifiers overrides the passed 'name' selection."
            )

        kwargs["name"] = id

    spectra = index.query(**kwargs)

    if spectra.empty:
        click.echo("No spectra matching these criteria found.")
        sys.exit()

    # Echo result
    table = Table(
        header_style="bold blue",
        box=rich.box.SQUARE,
        caption=f"{len(spectra)} {'Spectra' if len(spectra) > 1 else 'Spectrum'}",
    )

    columns = [
        "name",
        "number",
        "wave_min",
        "wave_max",
        "date_obs",
        "phase",
        "source",
        "shortbib",
    ]

    # Add non-index columns to the output
    for col in kwargs.keys():
        if col not in classy.index.COLUMNS and col != "query":
            columns += [col]

    for c in columns:
        if spectra[c].dtype == "float64":
            spectra[c] = spectra[c].round(3)
        table.add_column(c)

    spectra = spectra.fillna("-")
    for _, spec in spectra.iterrows():
        table.add_row(*spec[columns].astype(str))

    rich.print(table)

    # Plot
    if plot:
        spectra.plot(save=save)


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
        "[blue][1][/blue] Manage the cache "
        "[blue][2][/blue] Retrieve all public spectra",
        choices=["0", "1", "2"],
        show_choices=False,
        default="0",
    )

    if decision == "1":
        # Dache management diaglog
        decision = prompt.Prompt.ask(
            "\nChoose one of these actions:\n"
            "[blue][0][/blue] Do nothing "
            "[blue][1][/blue] Rebuild the index "
            # "[blue][2][/blue] Add phase angles "
            "[blue][2][/blue] Clear the cache",
            choices=["0", "1", "2", "3"],
            show_choices=False,
            default="0",
        )

        if decision == "1":
            rich.print()
            rocks.set_log_level("CRITICAL")
            classy.set_log_level("CRITICAL")
            index.build()

        # if decision == "2":
        #     index.add_phase_angles()

        if decision == "2":
            decision = prompt.Prompt.ask(
                "\nThis will delete the cache directory and all its contents,\n"
                "[bold]including the preprocessing- and feature parameters[/bold]. Are you sure?",
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
        index.build()
