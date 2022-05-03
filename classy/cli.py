import logging
import webbrowser

import click
import rich

import classy


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
@click.argument("path_data", type=str)
@_logging_option
def preprocess(path_data, log):
    """Apply the preprocessing routine to data in a CSV file."""

    classy.logging.init_logging(log)
    preprocessor = classy.preprocessing.Preprocessor(path_data)
    preprocessor.preprocess()
    preprocessor.to_file()


@cli_classy.command()
@click.argument("path_data", type=str)
@click.option("-p", "--plot", is_flag=True, help="Plot the classification result.")
@_logging_option
def classify(path_data, plot, log):
    """Classify asteroid observations."""

    classy.logging.init_logging(log)

    classifier = classy.classify.Classifier(path_data)
    classifier.classify()

    if plot:
        classifier.plot()

    classifier.to_file()
