from pathlib import Path

import numpy as np
import pandas as pd
import rocks

from classy import index

SHORTBIB = "Marsset+ 2014"
BIBCODE = "2014AA...568L...7M"


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
                "source": "CDS",
                "host": "cds",
                "collection": "J_AA_568_L7",
                "public": True,
            },
            index=[0],
        )

        # Add spectrum metadata
        data = _load_data(PATH_REPO / filename)
        entry["wave_min"] = min(data[:, 0])
        entry["wave_max"] = max(data[:, 0])
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
                "source": "CDS",
                "host": "cds",
                "collection": "J_AA_568_L7",
                "public": True,
            },
            index=[0],
        )

        # Add spectrum metadata
        data = _load_data(PATH_REPO / filename)
        entry["wave_min"] = min(data[:, 0])
        entry["wave_max"] = max(data[:, 0])
        entry["N"] = len(data)

        entries.append(entry)

    entries = pd.concat(entries)
    index.add(entries)


def _load_data(PATH):
    data = np.loadtxt(PATH)
    return data