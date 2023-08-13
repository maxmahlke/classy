from pathlib import Path

import pandas as pd
import rocks

from classy import config
from classy import index

SHORTBIB, BIBCODE = "Marsset+ 2014", "2014AA...568L...7M"


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
    data = pd.read_csv(PATH_DATA, names=["wave", "refl"], delimiter="\s+")
    return data, {}


def _create_index(PATH_REPO):
    # Change file permissions, they arrive restricted from CDS
    PATH_REPO.chmod(0o755)

    for file in PATH_REPO.rglob("*"):
        Path(file).chmod(0o755)

    # Actual index
    cat = pd.read_fwf(
        PATH_REPO / "list.dat",
        colspecs=[(0, 6), (70, 80), (81, 92), (94, 104), (105, 116)],
        names=["number", "date_obs1", "file1", "date_obs2", "file2"],
    )
    entries = []

    # File 1 and Date 1
    for _, row in cat.iterrows():
        filename = row.file1
        date_obs = row.date_obs1

        # Identify asteroid
        name, number = rocks.id(row.number)
        if name is None:
            continue

        # Create index entry
        entry = pd.DataFrame(
            data={
                "name": name,
                "number": number,
                "date_obs": date_obs,
                "shortbib": SHORTBIB,
                "bibcode": BIBCODE,
                "filename": str(PATH_REPO / filename).split("/classy/")[1],
                "source": "Misc",
                "host": "CDS",
                "module": "J_AA_568_L7",
            },
            index=[0],
        )

        # Add spectrum metadata
        data, _ = _load_data(entry.squeeze())
        entry["wave_min"] = min(data["wave"])
        entry["wave_max"] = max(data["wave"])
        entry["N"] = len(data)

        entries.append(entry)

    # File 2 and Date 2
    for _, row in cat[~pd.isna(cat.date_obs2)].iterrows():
        filename = row.file2
        date_obs = row.date_obs2

        # Identify asteroid
        name, number = rocks.id(row.number)
        if name is None:
            continue

        # Create index entry
        entry = pd.DataFrame(
            data={
                "name": name,
                "number": number,
                "date_obs": date_obs,
                "shortbib": SHORTBIB,
                "bibcode": BIBCODE,
                "filename": str(PATH_REPO / filename).split("/classy/")[1],
                "source": "Misc",
                "host": "CDS",
                "module": "J_AA_568_L7",
            },
            index=[0],
        )

        # Add spectrum metadata
        data, _ = _load_data(entry.squeeze())
        entry["wave_min"] = min(data["wave"])
        entry["wave_max"] = max(data["wave"])
        entry["N"] = len(data)

        entries.append(entry)

    entries = pd.concat(entries)
    index.add(entries)
