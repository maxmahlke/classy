import pandas as pd
import rocks

from classy.sources import pds
from classy import config

REFERENCES = {
    "LEBOFSKY1980": ["1980AJ.....85..573L", "Lebofsky 1980"],
    "FEIERBERGETAL1985": ["1985Icar...63..183F", "Feierberg+ 1985"],
    "JONESETAL1990": ["1990Icar...88..172J", "Jones+ 1990"],
    "LEBOFSKYETAL1990": ["1990Icar...83...16L", "Lebofsky+ 1990"],
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
    file_ = config.PATH_DATA / idx.filename
    data = pd.read_csv(file_, names=["wave", "refl", "refl_err"], delimiter=r"\s+")
    return data, {}


def _build_index(PATH_REPO):
    """Create index of spectra collection."""

    index = pd.DataFrame()

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
                    "filename": file_.relative_to(config.PATH_DATA),
                    "source": "Misc",
                    "host": "PDS",
                    "module": "lebofsky_three_micron",
                },
                index=[0],
            )

            # Add spectrum metadata
            data, _ = _load_data(entry.squeeze())
            entry["wave_min"] = min(data["wave"])
            entry["wave_max"] = max(data["wave"])
            entry["N"] = len(data["wave"])

            index = pd.concat([index, entry])
    return index
