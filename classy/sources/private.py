"""Module to add private spectra sources to classy."""
import numpy as np
import pandas as pd
import rocks

from classy import config
from classy import index


def _load_data(idx):
    """Load data and metadata of a cached Gaia spectrum.

    Parameters
    ----------
    idx : pd.Series
        A row from the classy spectra index.

    Returns
    -------
    pd.DataFrame, dict
        The data and metadata. List-like attributes are in the dataframe,
        single-value attributes in the dictionary.
    """
    PATH_DATA = config.PATH_CACHE / idx.filename

    # Try two different delimiters
    try:
        data = np.loadtxt(PATH_DATA)
    except ValueError:
        data = np.loadtxt(PATH_DATA, delimiter=",")

    data = pd.DataFrame(data)

    # Rename the columns that are present
    COLS = ["wave", "refl", "refl_err", "flag"]
    data = data.rename(columns={col: COLS.pop(0) for col in data.columns})
    return data, {}


def parse_index(PATH_INDEX):
    """Parse the user-passed index file of the private spectra repository.

    Parameters
    ----------
    PATH_INDEX : pathlib.Path
        The path of the user index.
    """

    # Read index
    ind = pd.read_csv(PATH_INDEX)

    # Check for necessary and optional columns
    for col in ["name", "filename"]:
        if col not in ind.columns:
            raise ValueError(f"The index needs to have a column called '{col}'.")

    entries = []

    for _, row in ind.iterrows():
        entry = {}

        # Verify asteroid identity
        name = row["name"]
        name, number = rocks.id(name)
        entry["name"] = name
        entry["number"] = number
        entry["filename"] = row.filename

        # Get sampling stats
        data = load_data(row.filename)
        wave = data[:, 0]

        entry["wave_min"] = wave.min()
        entry["wave_max"] = wave.max()
        entry["N"] = len(wave)

        # Record other metadata
        for col in ["shortbib", "source", "bibcode"]:
            if col in ind.columns:
                entry[col] = row[col]

        entry["host"] = "Private"
        entry["module"] = "private"

        entries.append(entry)

    # Add to index
    entries = pd.DataFrame(entries, index=range(len(entries)))
    index.add(entries)
    print(f"Added {len(entries)} spectra to the classy index.")
