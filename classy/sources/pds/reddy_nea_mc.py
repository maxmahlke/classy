import pandas as pd
import rocks

from classy import config
from classy import index
from classy.sources import pds

REFERENCES = {
    "REDDYETAL": [
        "urn:nasa:pds:ast_spectra_reddy_neos_marscrossers::1.0",
        "Reddy and Sanchez 2017",
    ]
}

DATA_KWARGS = {"names": ["wave", "refl", "refl_err"], "delimiter": r"\s+"}


def _build_index(PATH_REPO):
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
                    "filename": file_.relative_to(config.PATH_DATA),
                    "source": "Misc",
                    "host": "PDS",
                    "module": "reddy_nea_mc",
                },
                index=[0],
            )

            entries.append(entry)
    entries = pd.concat(entries)
    index.add(entries)
