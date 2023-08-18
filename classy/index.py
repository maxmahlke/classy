"""Module to manage the global spectra index in classy."""
import sys
from datetime import datetime
import functools

import numpy as np
import pandas as pd

from classy import config
from classy import cache
from classy.log import logger
from classy import sources

# Path to the global spectra index
PATH = config.PATH_CACHE / "index.csv"
PATH_FEATURES = config.PATH_CACHE / "features.csv"
PATH_SMOOTHING = config.PATH_CACHE / "smoothing.csv"


@functools.cache
def load():
    """Load the global spectra index.

    Returns
    -------
    pd.DataFrame
        The global spectra index. Empty if index does not exist yet.
    """
    if not PATH.is_file():
        if "status" not in sys.argv:
            logger.error(
                f"No reflectance spectra are available. Run '$ classy status' to retrieve them."
            )
        return pd.DataFrame(
            data={"name": [], "source": [], "filename": [], "host": []}, index=[]
        )

    return pd.read_csv(
        PATH, dtype={"number": "Int64"}, low_memory=False, index_col="filename"
    )


def save(index):
    """Save the global spectra index."""
    with np.errstate(invalid="ignore"):
        index["number"] = index["number"].astype("Int64")
    index.to_csv(PATH, index=True, index_label="filename")


def add(entries):
    """Add entries to the global spectra index.

    Parameters
    ----------
    entries : list of pd.DataFrame
        The entries to add to the index.
    """

    # Skip the cache of the load function as we change the index
    index = load.__wrapped__()

    # Append new entries and drop duplicate filenames
    entries = entries.set_index("filename")
    index = pd.concat([index, entries])
    index = index.drop_duplicates(keep="last")

    save(index)


def build():
    # readd the smass and mithneos obs dates
    # update index
    sources._build_index()


def add_phase_angles():
    """Add phase angles to all spectra in index."""

    # Get the relevant rows from index: has observation date but no phase anlge yet
    idx = load()
    print(len(idx), "complete")
    idx["phase"] = np.nan
    idx = idx.loc[(~pd.isna(idx.date_obs)) & (pd.isna(idx.phase))]
    print(len(idx), "with obds date but no phase")

    # ------
    # First round: those who have a single observation date
    idx_single = idx[~idx.date_obs.str.contains(",")]
    print(len(idx), "with single obs date")

    # Send one query per asteroid
    for name, spectra in idx_single.groupby("name"):
        epochs = spectra["date_obs"].values

        if len(epochs) == 1:
            continue

        ephem = cache.miriade_ephems(name, epochs)
        phase = ephem.phase.values
        breakpoint()

    # ------
    # Secound round: those who have more than one observation date


def convert_to_isot(dates, format):
    """Convert list of dates to ISOT format.

    Parameters
    ----------
    dates : str or list of str
        The dates to convert.
    format : str
        The current format string of the dates.
    """
    if isinstance(dates, str):
        dates = [dates]

    date_obs = ",".join(
        [datetime.strptime(date, format).isoformat(sep="T") for date in dates]
    )
    return date_obs


def load_smoothing():
    """Load the feature index."""
    if not PATH_SMOOTHING.is_file():
        return pd.DataFrame()
    return pd.read_csv(
        PATH_SMOOTHING,
        index_col="filename",
        dtype={
            "deg_savgol": int,
            "deg_spline": int,
            "window_savgol": int,
        },
    )


def store_smoothing(smoothing):
    """Store the feature index after copying metadata from the spectra index."""
    with np.errstate(invalid="ignore"):
        smoothing["number"] = smoothing["number"].astype("Int64")
    smoothing.to_csv(PATH_SMOOTHING, index=True)


def store_features(features):
    """Store the feature index after copying metadata from the spectra index."""
    with np.errstate(invalid="ignore"):
        features["number"] = features["number"].astype("Int64")
    features.to_csv(PATH_FEATURES, index=True)


def load_features():
    """Load the feature index."""
    if not PATH_FEATURES.is_file():
        return pd.DataFrame()
    return pd.read_csv(PATH_FEATURES, index_col=["filename", "feature"])
