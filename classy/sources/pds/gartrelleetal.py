from pathlib import Path

import pandas as pd
import rocks

from classy import index
from classy import config
from classy.sources import pds

SHORTBIB, BIBCODE = "Gartrelle+ 2021", "2021Icar..36314295G"


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
    data = pd.read_csv(file_, names=["wave", "refl", "refl_err"], delimiter=r",")
    return data, {}


def _create_index(PATH_REPO):
    """Create index of spectra collection."""

    entries = []
    PATH_REPO = Path(str(PATH_REPO).replace("V1_0", "V1.0"))

    # Iterate over data directory
    for xml_file in (PATH_REPO / "data").glob("*xml"):
        if xml_file.name in [
            "observationalparameters.xml",
            "collection_gbo.ast-dtype.gartrelleetal.irtf.spectra_data.xml",
        ]:
            continue
        id_, _, date_obs = pds.parse_xml(xml_file)
        file_ = xml_file.with_suffix(".csv")

        # Identify asteroid
        name, number = rocks.id(id_)
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
                "filename": str(file_).split("/classy/")[1],
                "source": "Misc",
                "host": "PDS",
                "module": "gartrelleetal",
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
