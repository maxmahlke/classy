"""Cache management for classy."""

import shutil

import pandas as pd

# import percache
import requests
import rich

from classy import config
from classy import index
from classy import sources
from classy import tools

# cache = percache.Cache(str(config.PATH_CACHE / "cache"))


def load_mahlke_index():
    """Load the index of spectra from Mahlke+ 2022."""
    PATH_INDEX = config.PATH_CACHE / "mahlke/index.csv"
    return pd.read_csv(PATH_INDEX, dtype={"number": "Int64"})


# ------
# Load spectra from cache
def load_spectra(idx_spectra):
    """Load a spectrum from a known source.

    Returns
    -------
    list of classy.core.Spectrum
    """

    spectra = [sources.load_spectrum(spec) for _, spec in idx_spectra.iterrows()]

    return spectra


def remove():
    """Remove the cache directory."""
    shutil.rmtree(config.PATH_CACHE)


def echo_inventory():
    """Echo inventory statistics based on the classy spectra index."""
    idx = index.load()
    sources_ = list(idx.source.unique())

    all_public = idx[idx.host == "Private"].empty
    legend = "[[bold]public[/bold]|[dim]private[/dim]]" if not all_public else ""

    rich.print(
        f"""\nContents of {config.PATH_CACHE}:

    {len(idx)} asteroid reflectance spectra from {len(sources_)} sources {legend}
      """
    )

    if sources_:
        for i, (source, obs) in enumerate(
            idx.sort_values("source").groupby("source"), 1
        ):
            public = obs.host.values[0] != "Private"
            highlight = "dim" if not public else "bold"

            rich.print(
                f"    [{highlight}]{source:<8}[/{highlight}] {len(obs):>5}",
                end="",
            )

            if not i % 4:
                rich.print()
        else:
            rich.print("\n")


# @cache
def miriade_ephems(name, epochs):
    """Gets asteroid ephemerides from IMCCE Miriade.

    Parameters
    ----------
    name : str
        Name or designation of asteroid.
    epochs : list
        List of observation epochs in iso format.

    Returns
    -------
    :returns: pd.DataFrame - Input dataframe with ephemerides columns appended
                     False - If query failed somehow
    """

    # Pass sorted list of epochs to speed up query
    files = {"epochs": ("epochs", "\n".join(sorted(epochs)))}

    # ------
    # Query Miriade for phase angles
    url = "http://vo.imcce.fr/webservices/miriade/ephemcc_query.php"

    params = {
        "-name": f"a:{name}",
        "-mime": "json",
        "-tcoor": "5",
        "-output": "--jul",
        "-tscale": "UTC",
    }

    # Execute query
    try:
        r = requests.post(url, params=params, files=files, timeout=50)
    except requests.exceptions.ReadTimeout:
        return False
    j = r.json()

    # Read JSON response
    try:
        ephem = pd.DataFrame.from_dict(j["data"])
    except KeyError:
        return False

    return ephem


def load_cat(host, which):
    PATH_CAT = config.PATH_CACHE / f"{host}/{which}.csv"
    if not PATH_CAT.is_file():
        tools._retrieve_from_github(host, which, path=PATH_CAT)
    return pd.read_csv(PATH_CAT)
