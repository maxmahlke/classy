from pathlib import Path

import pandas as pd
import rocks

from classy import index
from classy import config
from classy.sources import pds

REFERENCES = {
    "GARTRELLE": ["2021Icar..36314295G", "Gartrelle+ 2021"],
}


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
        id_, ref, date_obs = pds.parse_xml(xml_file)
        file_ = xml_file.with_suffix(".csv")

        # Convert ref from XML to bibcode and shortbib
        if ref is None:
            ref = "GARTRELLE"
        bibcode, shortbib = REFERENCES[ref]

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
                "shortbib": shortbib,
                "bibcode": bibcode,
                "filename": str(file_).split("/classy/")[1],
                "source": "Misc",
                "host": "pds",
                "collection": "gartrelleetal",
                "public": True,
            },
            index=[0],
        )

        # Add spectrum metadata
        data = _load_data(entry.squeeze())
        entry["wave_min"] = min(data["wave"])
        entry["wave_max"] = max(data["wave"])
        entry["N"] = data["wave"]

        entries.append(entry)
    entries = pd.concat(entries)
    index.add(entries)


def _load_data(meta):
    """Load spectrum data.

    Returns
    -------
    pd.DataFrame
    """
    file_ = config.PATH_CACHE / meta.filename
    return pd.read_csv(file_, names=["wave", "refl", "refl_err"], delimiter=r",")
