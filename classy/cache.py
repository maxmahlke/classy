"""Cache management for classy."""

import shutil

import pandas as pd

# import percache
import requests
import rich

from classy import config
from classy import index
from classy import sources

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

    spectra = [
        getattr(sources, spec.host.lower()).load_spectrum(spec)
        for _, spec in idx_spectra.iterrows()
    ]

    return spectra


def remove():
    """Remove the cache directory."""
    shutil.rmtree(config.PATH_CACHE)


def echo_inventory():
    idx = index.load()
    sources_ = list(idx.source.unique())

    rich.print(
        f"""\nContents of {config.PATH_CACHE}:

    {len(idx)} asteroid reflectance spectra from {len(sources_)} sources
      """
    )

    if sources_:
        for i, (source, obs) in enumerate(
            idx.sort_values("source").groupby("source"), 1
        ):
            rich.print(f"    {source:<8} {len(obs):>5}", end="")

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
