"""Module to manage the global spectra index in classy."""
import numpy as np
import pandas as pd

from classy import config

# Path to the global spectra index
PATH = config.PATH_CACHE / "index.csv"


def load():
    """Load the global spectra index.

    Returns
    -------
    pd.DataFrame
        The global spectra index. Empty if index does not exist yet.
    """
    if not PATH.is_file():
        return pd.DataFrame(data={"name": [], "source": [], "filename": []}, index=[])
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
    index = load()

    # Find overlap between new entries and exisiting index
    # Store the DF index of the classy index to later drop duplicates via that index
    overlap = pd.merge(
        index.reset_index(), entries, how="inner", on=["name", "source", "filename"]
    )

    if not overlap.empty:
        # Drop duplicated rows
        overlap = overlap.set_index("index")
        index = index.drop(overlap.index)

        # for entry in entries:
        #
        #     # If name,source,filename combination already in index, replace it
        #     if not index.empty:
        #
        #         existing = index.loc[
        #             (index["name"] == entry["name"].values[0])
        #             & (index.source == entry.source.values[0])
        #             & (index.filename == entry.filename.values[0])
        #         ]
        #
        #         if not existing.empty:
        #             index = index.drop(existing.index)

    index = pd.concat([index, entries], ignore_index=True)

    save(index)
