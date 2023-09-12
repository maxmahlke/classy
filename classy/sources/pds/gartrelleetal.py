from pathlib import Path

import pandas as pd
import rocks

from classy import config
from classy import index
from classy.sources import pds

SHORTBIB, BIBCODE = "Gartrelle+ 2021", "2021Icar..36314295G"
DATA_KWARGS = {"names": ["wave", "refl", "refl_err"]}


def _build_index(PATH_REPO):
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
                "filename": file_.relative_to(config.PATH_DATA),
                "source": "Misc",
                "host": "PDS",
                "module": "gartrelleetal",
            },
            index=[0],
        )

        entries.append(entry)
    entries = pd.concat(entries)
    index.add(entries)
