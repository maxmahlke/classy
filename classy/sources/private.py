"""Module to add private spectra sources to classy."""
import numpy as np
import pandas as pd
import rocks

import classy
from classy import index


def load_spectrum(meta):
    """Load a spectrum of a private repository."""

    data = load_data(meta.filename)

    wave = data[:, 0]
    refl = data[:, 1]

    if data.shape[1] > 2:
        refl_err = data[:, 2]
    else:
        refl_err = None

    spec = classy.Spectrum(
        wave=wave,
        refl=refl,
        refl_err=refl_err,
        name=meta["name"],
        number=meta["number"],
        bibcode=meta["bibcode"],
        shortbib=meta["shortbib"],
        date_obs=meta["date_obs"],
        filename=meta["filename"],
        source="private",
    )

    return spec


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

        entry["host"] = "private"
        entry["public"] = False

        entries.append(entry)

    # Add to index
    entries = pd.DataFrame(entries, index=range(len(entries)))
    index.add(entries)
    print(f"Added {len(entries)} spectra to the classy index.")


def load_data(filename):
    try:
        data = np.loadtxt(filename)
    except ValueError:
        data = np.loadtxt(filename, delimiter=",")
    return data
