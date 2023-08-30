"""Module to add private spectra sources to classy."""
import pandas as pd
import rocks

from classy import config
from classy import index


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
        # Verify asteroid identity
        name = row["name"]
        name, number = rocks.id(name)

        entry = pd.DataFrame(
            data={
                "name": name,
                "number": number,
                "filename": row.filename,
            },
            index=[0],
        )

        # Record other metadata
        for col in ["shortbib", "source", "bibcode", "date_obs"]:
            if col in ind.columns:
                entry[col] = row[col]

        entry["host"] = "Private"
        entry["module"] = "private"

        entries.append(entry)

    # Add to index
    entries = pd.concat(entries)
    index.add(entries)
    print(f"Added {len(entries)} spectra to the classy index.")
