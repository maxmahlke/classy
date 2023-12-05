"""Module to add private spectra sources to classy."""
from pathlib import Path
import shutil

import pandas as pd
import rocks

from classy import config
from classy import index
from classy.utils.logging import logger


def parse_index(PATH_INDEX):
    """Parse the user-passed index file of the private spectra repository.

    Parameters
    ----------
    PATH_INDEX : pathlib.Path
        The path of the user index.
    """

    # Read index
    ind = pd.read_csv(PATH_INDEX)

    if ind.empty:
        raise ValueError("The passed index file is empty.")

    # Check for necessary and optional columns
    for col in ["name", "filename"]:
        if col not in ind.columns:
            raise ValueError(f"The index needs to have a column called '{col}'.")

    entries = []

    for _, row in ind.iterrows():
        # Verify asteroid identity
        name = row["name"]
        name, number = rocks.id(name)

        # Copy spectrum to cache
        filename = Path(row.filename)

        PATH_DEST = config.PATH_DATA / filename.parent.name / filename.name
        PATH_DEST.parent.mkdir(exist_ok=True)

        shutil.copy(filename, PATH_DEST)

        entry = pd.DataFrame(
            data={
                "name": name,
                "number": number,
                "filename": str(PATH_DEST.relative_to(config.PATH_DATA)),
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
    logger.info(f"Added {len(entries)} spectra to the classy cache: {PATH_DEST.parent}")
