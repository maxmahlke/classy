import pandas as pd
import rocks

from classy import config
from classy import index
from classy.sources import pds

SHORTBIB, BIBCODE = "Willman+ 2008", "2008Icar..195..663W"


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
    data["wave"] /= 10000
    return data, {}


def _create_index(PATH_REPO):
    """Create index of spectra collection."""

    entries = []

    # Iterate over data directory
    for dir in PATH_REPO.iterdir():
        if dir.name != "data":
            continue

        # Extract meta from XML file
        for xml_file in dir.glob("**/*xml"):
            if xml_file.name.startswith("collection_gbo"):
                continue

            id_, _, date_obs = pds.parse_xml(xml_file)

            file_ = xml_file.with_suffix(".tab")

            # Identify asteroid
            name, number = rocks.id(id_)

            # Create index entry
            entry = pd.DataFrame(
                data={
                    "name": name,
                    "number": number,
                    "DATE_OBS": date_obs,
                    "SHORTBIB": SHORTBIB,
                    "bibcode": BIBCODE,
                    "filename": str(file_).split("/classy/")[1],
                    "module": "willman_iannini",
                    "source": "Misc",
                    "host": "PDS",
                    "collection": "willman_iannini",
                    "public": True,
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
