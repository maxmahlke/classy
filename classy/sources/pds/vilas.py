import numpy as np
import pandas as pd
import rocks

from classy import config
from classy import index
from classy.sources import pds

REFERENCES = {
    "VILASETAL1985": ["1985Icar...63..201V", "Vilas+ 1985"],
    "VILAS&SMITH1985": ["1985Icar...64..503V", "Vilas and Smith 1985"],
    "VILAS&MCFADDEN1992": ["1992Icar..100...85V", "Vilas and McFadden 1992"],
    "VILASETAL1993A": ["1993Icar..102..225V", "Vilas+ 1993"],
    "VILASETAL1993B": ["1993Icar..105...67V", "Vilas+ 1993"],
}


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
                    "source": "Misc",
                    "host": "pds",
                    "collection": "vilas",
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
    data = pd.read_csv(file_, names=["wave", "refl", "refl_err"], delimiter=r"\s+")
    data = data[data.wave != 0]
    data.refl_err[data.refl_err == -9.999] = np.nan
    return data
