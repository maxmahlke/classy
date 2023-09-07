import pandas as pd
import rocks

from classy import index
from classy import config
from classy.sources import pds

REFERENCES = {
    "REDDYETAL": [
        "urn:nasa:pds:ast_spectra_reddy_neos_marscrossers::1.0",
        "Reddy and Sanchez 2017",
    ]
}


def _load_data(meta):
    """Load spectrum data.

    Returns
    -------
    pd.DataFrame

    """
    file_ = config.PATH_CACHE / meta.filename
    data = pd.read_csv(file_, names=["wave", "refl", "refl_err"], delimiter=r"\s+")
    return data, {}


def _create_index(PATH_REPO):
    """Create index of spectra collection."""

    entries = []

    # Iterate over data directory
    for dir in (PATH_REPO / "data").iterdir():
        if not dir.is_dir():
            continue

        # Extract meta from XML file
        for xml_file in dir.glob("**/*xml"):
            id_, ref, date_obs = pds.parse_xml(xml_file)

            if ref is None:
                ref = "REDDYETAL"

            file_ = xml_file.with_suffix(".tab")

            # Convert ref from XML to bibcode and shortbib
            bibcode, shortbib = REFERENCES[ref]

            # Identify asteroid
            name, number = rocks.id(id_)

            # Create index entry
            entry = pd.DataFrame(
                data={
                    "name": name,
                    "number": number,
                    "date_obs": date_obs,
                    "shortbib": shortbib,
                    "bibcode": bibcode,
                    "filename": str(file_).split("/classy/")[1],
                    "module": "reddy_nea_mc",
                    "source": "Misc",
                    "host": "pds",
                    "collection": "reddy_nea_mc",
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
