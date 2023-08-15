import pandas as pd
import rocks

from classy import index
from classy import config
from classy.sources import pds

REFERENCES = {
    "MOSKOVITZ": [
        "urn:nasa:pds:gbo.ast-v-type.moscovitz.spectra::1.0",
        "Moskovitz+ 2020",
    ],
    "MOSKOVITZETAL2008": ["2008Icar..198...77M", "Moskovitz+ 2008"],
    "MOSKOVITZETAL2008B": ["2008ApJ...682L..57M", "Moskovitz+ 2008"],
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

            id_, ref, date_obs = pds.parse_xml(xml_file)

            if ref is None:
                ref = "MOSKOVITZ"

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
                    "host": "PDS",
                    "module": "moskovitz_v_types",
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
