import pandas as pd
import rocks

from classy import index
from classy import config
from classy.sources import pds

REFERENCES = {
    "HARDERSENETAL2004B": ["2004Icar..167..170H", "Hardersen+ 2004"],
    "HARDERSENETAL2005": ["2005Icar..175..141H", "Hardersen+ 2005"],
    "HARDERSENETAL2011": ["2011MPS...46.1910H", "Hardersen+ 2011"],
    "HARDERSENETAL2015": ["2014Icar..242..269H", "Hardersen+ 2014"],
    "HARDERSENETAL2015B": ["2015ApJS..221...19H", "Hardersen+ 2015"],
    "HARDERSENETAL2018": ["2018AJ....156...11H", "Hardersen+ 2018"],
}


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
    file_ = config.PATH_CACHE / idx.filename
    data = pd.read_csv(file_, names=["wave", "refl", "refl_err"], delimiter=r"\s+")
    data = data[data.wave != 0]
    return data, {}


def _create_index(PATH_REPO):
    """Create index of spectra collection."""

    entries = []

    # Iterate over data directory
    for dir in (PATH_REPO / "data").iterdir():
        if not dir.is_dir():
            continue

        # Extract meta from LBL file
        for lbl_file in dir.glob("**/*lbl"):
            id_, ref, date_obs = pds.parse_lbl(lbl_file)
            file_ = lbl_file.with_suffix(".tab")

            # Identify asteroid
            id_ = id_.split()[0]
            name, number = rocks.id(id_)

            if ref is None:
                ref = "HARDERSENETAL2018"

            # Convert ref from lbl to bibcode and shortbib
            bibcode, shortbib = REFERENCES[ref]

            # Create index entry
            entry = pd.DataFrame(
                data={
                    "name": name,
                    "number": number,
                    "date_obs": date_obs,
                    "shortbib": shortbib,
                    "bibcode": bibcode,
                    "filename": str(file_).split("/classy/")[1],
                    "source": "Hardersen",
                    "host": "PDS",
                    "module": "hardersenspec",
                },
                index=[0],
            )

            # Add spectrum metadata
            data, _ = _load_data(entry.squeeze())
            entry["wave_min"] = min(data["wave"])
            entry["wave_max"] = max(data["wave"])
            entry["N"] = len(data["wave"])

            entries.append(entry)
    entries = pd.concat(entries)
    index.add(entries)
