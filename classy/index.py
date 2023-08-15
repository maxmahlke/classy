"""Module to manage the global spectra index in classy."""
import sys
from datetime import datetime
from functools import cache

import numpy as np
import pandas as pd

from classy import config
from classy.log import logger

# Path to the global spectra index
PATH = config.PATH_CACHE / "index.csv"
PATH_FEATURES = config.PATH_CACHE / "features.csv"
PATH_SMOOTHING = config.PATH_CACHE / "smoothing.csv"


@cache
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

    return pd.read_csv(PATH, dtype={"number": "Int64"}, low_memory=False)


def save(index):
    """Save the global spectra index."""
    with np.errstate(invalid="ignore"):
        index["number"] = index["number"].astype("Int64")
    index.to_csv(PATH, index=False)


def add(entries):
    """Add entries to the global spectra index.

    Parameters
    ----------
    entries : list of pd.DataFrame
        The entries to add to the index.
    """

    # Cannot use the load() function here due to caching
    if not PATH.is_file():
        index = pd.DataFrame(data={"name": [], "source": [], "filename": []}, index=[])
    else:
        index = pd.read_csv(PATH, dtype={"number": "Int64"}, low_memory=False)

    # Find overlap between new entries and exisiting index
    # Store the DF index of the classy index to later drop duplicates via that index
    overlap = pd.merge(
        index.reset_index(), entries, how="inner", on=["name", "source", "filename"]
    )

    if not overlap.empty:
        # Drop duplicated rows
        overlap = overlap.set_index("index")
        index = index.drop(overlap.index)

    index = pd.concat([index, entries], ignore_index=True)
    save(index)


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
