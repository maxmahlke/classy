from pathlib import Path
import sys
import webbrowser

import click
import rich
from rich.table import Table
import rocks

import classy.classify
from classy import cache
from classy import index
from classy import sources


@click.group()
@click.version_option(version=classy.__version__, message="%(version)s")
def cli_classy():
    """CLI for minor body classification."""
    pass


@cli_classy.command()
@click.argument("path", type=str)
def add(path):
    """Add a local spectra collection."""
    path = Path(path)

    if not path.is_file():
        click.echo("You need to pass the path of an index CSV file.")
        sys.exit()

    sources.private.parse_index(path)


@cli_classy.command(context_settings=dict(ignore_unknown_options=True))
@click.argument("args", type=click.UNPROCESSED, nargs=-1)
@click.option(
    "-t",
    "--taxonomy",
    type=click.Choice(classy.taxonomies.SYSTEMS, case_sensitive=False),
    help="Taxonomic system shown in output plot.",
)
@click.option("-p", "--plot", is_flag=True, help="Plot the classification result.")
@click.option("-s", "--save", help="Save plot under specified filename.")
def classify(args, taxonomy, plot, save):
    """Classify spectra in classy index."""

    if not args:
        raise ValueError("No query parameters were specified.")

    id, kwargs = _parse_args(args)
    spectra = classy.Spectra(id, **kwargs)

    if not spectra:
        click.echo("No spectra matching these criteria found.")
        sys.exit()

    classy.set_log_level("CRITICAL")
    for t in ["mahlke", "demeo", "tholen"]:
        spectra.classify(taxonomy=t)
    classy.set_log_level("WARNING")

    # Echo result
    table, columns = _create_table(spectra, classify=True)

    for spec in spectra:
        row = []

        for c in columns:
            if c not in ["wave_min", "wave_max"]:
                row.append(str(getattr(spec, c)))
            elif c == "wave_min":
                row.append(f"{spec.wave.min():.3f}")
            elif c == "wave_max":
                row.append(f"{spec.wave.max():.3f}")
        table.add_row(*row)

    rich.print(table)

    # Plot
    if plot:
        spectra.plot(save=save, taxonomy=taxonomy)


@cli_classy.command()
def docs():
    """Open documentation in browser."""
    webbrowser.open("https://classy.readthedocs.io/en/latest/", new=2)


@cli_classy.command(context_settings=dict(ignore_unknown_options=True))
@click.argument("args", type=click.UNPROCESSED, nargs=-1)
@click.option(
    "-f", "--force", is_flag=True, help="Include spectra with feature parameters."
)
def features(args, force):
    """Run interactive feature detection for selected spectra."""
    if not args:
        raise ValueError("No query parameters were specified.")

    id, kwargs = _parse_args(args)
    spectra = classy.Spectra(id, **kwargs)

    if not spectra:
        click.echo("No spectra matching these criteria found.")
        sys.exit()

    spectra.inspect_features(force=force, progress=True)


@cli_classy.command(context_settings=dict(ignore_unknown_options=True))
@click.argument("args", type=click.UNPROCESSED, nargs=-1)
@click.option(
    "-f", "--force", is_flag=True, help="Include spectra with smoothing parameters."
)
def smooth(args, force):
    """Run interactive smoothing for selected spectra."""
    if not args:
        raise ValueError("No query parameters were specified.")

    id, kwargs = _parse_args(args)
    spectra = classy.Spectra(id, **kwargs)

    if not spectra:
        click.echo("No spectra matching these criteria found.")
        sys.exit()

    spectra.smooth(force=force, progress=True)


@cli_classy.command(context_settings=dict(ignore_unknown_options=True))
@click.argument("args", type=click.UNPROCESSED, nargs=-1)
@click.option("-p", "--plot", is_flag=True, help="Plot the spectra.")
@click.option("-s", "--save", help="Save plot under specified filename.")
def spectra(args, plot, save):
    """Search for spectra in classy index."""

    if not args:
        raise ValueError("No query parameters were specified.")

    id, kwargs = _parse_args(args)
    spectra = index.query(id, **kwargs)

    if spectra.empty:
        click.echo("No spectra matching these criteria found.")
        sys.exit()

    # Echo result
    table, columns = _create_table(spectra)

    for _, spec in spectra.iterrows():
        table.add_row(*spec[columns].astype(str))

    rich.print(table)

    # Plot
    if plot:
        classy.Spectra(id, **kwargs).plot(save=save)


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


# ------
# Utility functions
def _parse_args(args):
    """Separate identifiers and option key-value pairs from arguments."""

    # Separate query parameters and identifiers
    idx_options = [i for i, arg in enumerate(args) if arg.startswith("--")]
    kwargs = (
        {args[i].strip("--"): args[i + 1] for i in idx_options} if idx_options else {}
    )

    id = args[: min(idx_options)] if idx_options else args
    id = None if not id else id
    return id, kwargs


def _create_table(spectra, classify=False):
    """Create Table instance to echo query results."""
    table = Table(
        box=rich.box.ASCII2,
        caption=f"{len(spectra)} Spectr{'a' if len(spectra) > 1 else 'um'}",
    )

    # Construct column setup
    columns = ["name", "number", "wave_min", "wave_max"]

    if not classify:
        for c in ["date_obs", "phase", "source"]:
            columns.insert(4, c)

        for col in spectra.columns:
            if col not in classy.index.COLUMNS:
                columns += [col]

        for c in columns:
            if spectra[c].dtype == "float64":
                spectra[c] = spectra[c].round(3)
            if spectra[c].dtype in ["float64", "object"]:
                spectra[c] = spectra[c].fillna("-")
    else:
        columns += ["albedo", "class_mahlke", "class_demeo", "class_tholen"]

    columns += ["shortbib"]

    for c in columns:
        table.add_column(c)

    return table, columns
