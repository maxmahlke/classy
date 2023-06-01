import pandas as pd
import rocks

from classy.sources import pds
from classy import config

REFERENCES = {
    "Rivkinetal1995": ["1995Icar..117...90R", "Rivkin+ 1995"],
    "Rivkinetal1997": ["1997Icar..127..255R", "Rivkin+ 1997"],
    "Rivkinetal2000": ["2000Icar..145..351R", "Rivkin+ 2000"],
    "Rivkinetal2001": ["2001MPS...36.1727R", "Rivkin and Clark 2001"],
    "Rivkinetal2002": ["2002Icar..156...64R", "Rivkin+ 2002"],
    "RIVKINPDS": ["EAR-A-3-RDR-RIVKIN-THREE-MICRON-V3.0", "Rivkin and Neese 2003"],
}


def _create_index(PATH_REPO):
    """Create index of spectra collection."""

    index = pd.DataFrame()

    # Iterate over index file
    idx_repo = pd.read_fwf(
        PATH_REPO / "data/rivindex.tab",
        columns=[
            (0, 7),
            (7, 25),
            (25, 40),
            (40, 51),
            (51, 56),
            (56, 61),
            (61, 67),
            (67, 72),
            (72, 86),
        ],
        names=["number", "name", "filename", "date_obs", "d", "r", "phase", "V", "ref"],
    )

    for _, row in idx_repo.iterrows():
        if pd.isna(row.number):
            continue  # not including phobos and deimos here

        # Identify asteroid
        id_ = row.number
        name, number = rocks.id(id_)

        ref = row.ref if not pd.isna(row.ref) else "RIVKINPDS"
        bibcode, shortbib = REFERENCES[ref]

        # Create index entry
        entry = pd.DataFrame(
            data={
                "name": name,
                "number": number,
                "date_obs": row.date_obs,
                "shortbib": shortbib,
                "bibcode": bibcode,
                "collection": "rivkin_three_micron",
                "filename": str(file_).split("/classy/")[1].replace("75euri", "75eury"),
                "source": "Misc",
                "host": "pds",
                "collection": "rivkin_three_micron",
                "public": True,
            },
            index=[0],
        )

        # Add spectrum metadata
        data = _load_data(entry.squeeze())
        entry["wave_min"] = min(data["wave"])
        entry["wave_max"] = max(data["wave"])
        entry["N"] = data["wave"]

        index = pd.concat([index, entry])
    return index


def _load_data(meta):
    """Load spectrum data.

    Returns
    -------
    pd.DataFrame

    """
    file_ = config.PATH_CACHE / meta.filename
    data = pd.read_csv(file_, names=["wave", "refl", "refl_err"], delimiter=r"\s+")
    return data
