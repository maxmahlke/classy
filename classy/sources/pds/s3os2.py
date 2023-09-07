import pandas as pd
import rocks

from classy import index
from classy import config
from classy.sources import pds

SHORTBIB, BIBCODE = "Lazzaro+ 2004", "2004Icar..172..179L"


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
    data = data[data.wave != 0]
    return data, {}


def _create_index(PATH_REPO):
    """Create index of spectra collection."""

    entries = []

    # Iterate over data directory
    for dir in (PATH_REPO / "data").iterdir():
        if not dir.is_dir():
            continue

        # Extract meta from LBL file
        for lbl_file in dir.glob("**/*lbl"):
            id_, _, date_obs = pds.parse_lbl(lbl_file)
            file_ = lbl_file.with_suffix(".tab")

            # Identify asteroid
            id_ = id_.split()[0]
            name, number = rocks.id(id_)

            # Create index entry
            entry = pd.DataFrame(
                data={
                    "name": name,
                    "number": number,
                    "date_obs": date_obs,
                    "shortbib": SHORTBIB,
                    "bibcode": BIBCODE,
                    "filename": str(file_).split("/classy/")[1],
                    "module": "s3os2",
                    "source": "S3OS2",
                    "host": "PDS",
                    "collection": "s3os2",
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
