import pandas as pd
import rocks

from classy import config
from classy import index
from classy.sources import pds

SHORTBIB, BIBCODE = "Reddy 2009", "2009PhDT.......233R"

DATA_KWARGS = {"names": ["wave", "refl", "refl_err"], "delimiter": r"\s+"}


def _build_index(PATH_REPO):
    """Create index of spectra collection."""

    entries = []

    # Iterate over data directory
    for dir in PATH_REPO.iterdir():
        if dir.name != "data":
            continue

        # Extract meta from LBL file
        for xml_file in dir.glob("**/*lbl"):
            if xml_file.name.startswith("collection_gbo"):
                continue

            id_, _, date_obs = pds.parse_lbl(xml_file)

            if id_ == "4954 ERIC":
                id_ = 4954
            if id_ == "1980 TEZCATLIPOCA":
                id_ = 1980
            if id_ == "1620 GEOGRAPHOS":
                id_ = 1620
            if id_ == "4179 TOUTATIS":
                id_ = 4179
            if id_ == "6456 GOLOMBEK":
                id_ = 6456
            if id_ == "4015 WILSON-HARRINGTON":
                id_ = 4015

            file_ = xml_file.with_suffix(".tab")

            # Identify asteroid
            name, number = rocks.id(id_)

            # Create index entry
            entry = pd.DataFrame(
                data={
                    "name": name,
                    "number": number,
                    "date_obs": date_obs,
                    "shortbib": SHORTBIB,
                    "bibcode": BIBCODE,
                    "filename": file_.relative_to(config.PATH_DATA),
                    "source": "Misc",
                    "host": "PDS",
                    "module": "reddy_nea",
                },
                index=[0],
            )

            entries.append(entry)
    entries = pd.concat(entries)
    index.add(entries)
